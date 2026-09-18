"""Bounded frame codec with real application dispatch; unfinished routes fail."""
from concurrent.futures import ThreadPoolExecutor
from importlib.resources import files
import json
import uuid

from jsonschema import Draft202012Validator, FormatChecker
from apps.edge.principal import current_principal
from packages.application.session import Application
from packages.domain.errors import DomainError, StoreError


MAX_FRAME = 1_048_576


class ProtocolError(Exception):
    def __init__(self, code, message):
        self.code, self.message = code, message


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def _nonfinite(value):
    raise ValueError("Nonfinite JSON number")


def _has_float(value):
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(_has_float(v) for v in value.values())
    if isinstance(value, list):
        return any(_has_float(v) for v in value)
    return False


class Core:
    def __init__(self, owner_root):
        resource = files("apps.edge").joinpath("resources/schemas")
        self.schema = json.loads(resource.joinpath("contract.json").read_text(encoding="utf-8"))
        self.methods = json.loads(resource.joinpath("methods.json").read_text(encoding="utf-8"))
        if len(self.methods) != 20:
            raise StoreError("Method registry mismatch")
        base = Draft202012Validator(self.schema, format_checker=FormatChecker())
        self._validators = {name: base.evolve(schema={"$ref": "#/$defs/" + contract["request"]})
                            for name, contract in self.methods.items()}
        self.application = Application(owner_root, principal=current_principal())
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="fullkit-core")
        self._closed = False

    @property
    def workspace(self):
        return self.application.workspace

    @property
    def context(self):
        return self.application.context

    def raw_frame(self, frame):
        if self._closed:
            raise StoreError("Core is closed")
        return self._executor.submit(self._frame, frame).result()

    def _frame(self, frame):
        request_id = None
        try:
            if not isinstance(frame, bytes) or len(frame) > MAX_FRAME or not frame.endswith(b"\n") or b"\n" in frame[:-1]:
                raise ProtocolError(-32700, "Parse error")
            try:
                request = json.loads(frame[:-1].decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_nonfinite)
            except (ValueError, UnicodeError, RecursionError):
                raise ProtocolError(-32700, "Parse error") from None
            if isinstance(request, dict) and isinstance(request.get("id"), str):
                try:
                    uuid.UUID(request["id"])
                    request_id = request["id"]
                except ValueError:
                    pass
            if not isinstance(request, dict) or set(request) != {"jsonrpc", "id", "method", "params"} or request["jsonrpc"] != "2.0" or request_id is None or not isinstance(request["method"], str):
                raise ProtocolError(-32600, "Invalid Request")
            method = request["method"]
            if method not in self.methods:
                raise ProtocolError(-32601, "Method not found")
            if _has_float(request["params"]) or not self._validators[method].is_valid(request):
                raise ProtocolError(-32602, "Invalid params")
            response = {"jsonrpc": "2.0", "id": request_id, "result": self.application.dispatch(method, request["params"])}
        except DomainError as error:
            response = {"jsonrpc": "2.0", "id": request_id,
                        "error": {"code": -32000, "message": error.code, "data": {}}}
        except ProtocolError as error:
            response = {"jsonrpc": "2.0", "id": request_id, "error": {"code": error.code, "message": error.message}}
        except Exception:
            # No traceback/path/foreign identity goes to protocol stdout.
            response = {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32603, "message": "Internal error"}}
        return (json.dumps(response, ensure_ascii=False, allow_nan=False, separators=(",", ":")) + "\n").encode("utf-8")

    def close(self):
        if not self._closed:
            try:
                self._executor.submit(self.application.close).result()
            finally:
                self._executor.shutdown(wait=True)
                self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
