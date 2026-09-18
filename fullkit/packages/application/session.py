"""Selected context authorization is application policy, independent of transport."""
from concurrent.futures import ThreadPoolExecutor
import time
import uuid
from packages.application.homes import HomeWorkspace
from packages.domain.errors import DomainError, StoreError


class Application:
    def __init__(self, owner_root, principal):
        self.workspace = HomeWorkspace(owner_root)
        self.principal = principal
        self.session_id, self.generation = str(uuid.uuid4()), 0
        self.context = self.store = None
        self.cursors = {}
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="fullkit-application")
        self._closed = False

    def dispatch(self, method, params):
        if self._closed:
            raise StoreError("Application is closed")
        return self._executor.submit(self._dispatch, method, params).result()

    def _dispatch(self, method, params):
        if method == "home.list":
            return {"homes": self.workspace.list_homes()}
        if method == "session.select_home":
            return self._select(params)
        context = dict(params["context"])
        for field in ("home_id", "store_instance_id", "session_id"):
            context[field] = str(uuid.UUID(context[field]))
        if self.context is None or context != self.context:
            raise DomainError("HOME_CONTEXT")
        if "cmd" in params:
            cmd = dict(params["cmd"])
            for field in ("home_id", "job_id", "operation_id"):
                if cmd[field] is not None:
                    cmd[field] = str(uuid.UUID(cmd[field]))
            if cmd["command"] != method or cmd["home_id"] != context["home_id"]:
                raise DomainError("HOME_CONTEXT")
            return self.store.submit_command(cmd, self.principal)
        if method == "operation.get":
            return self.store.get_operation(str(uuid.UUID(params["operation_id"])))
        if method == "job.list":
            return self._jobs(params)
        raise NotImplementedError("Method not implemented")

    def _select(self, params):
        # Resolve only owner-index metadata first; no business lookup in peer stores.
        home, store_id = str(uuid.UUID(params["home_id"])), str(uuid.UUID(params["store_instance_id"]))
        descriptor = next((h for h in self.workspace.list_homes() if h["home_id"] == home and h["store_instance_id"] == store_id), None)
        if descriptor is None:
            raise DomainError("HOME_CONTEXT")
        previous = self.context
        previous_readonly = self.store.readonly if self.store else None
        if self.store:
            self.store.close()
        self.store = self.context = None
        self.cursors.clear()
        try:
            self.store = self.workspace.open_store(home, store_id, readonly=descriptor["recovery"] or not descriptor["active"])
        except Exception:
            if previous:
                try:
                    self.store = self.workspace.open_store(previous["home_id"], previous["store_instance_id"],
                                                           readonly=previous_readonly)
                    self.generation += 1
                    self.context = dict(previous, session_generation=self.generation)
                except Exception:
                    self.store = self.context = None
            raise
        self.generation += 1
        self.context = {"home_id": home, "store_instance_id": store_id, "session_id": self.session_id,
                        "session_generation": self.generation}
        return dict(self.context)

    def _jobs(self, params):
        now = time.monotonic()
        self.cursors = {key: value for key, value in self.cursors.items() if value["expires"] > now}
        token = params["cursor"]
        if token is not None:
            cursor = self.cursors.get(token)
            if cursor is None or cursor["context"] != self.context:
                raise DomainError("HOME_CONTEXT")
            high, last = cursor["high"], cursor["last"]
        else:
            high, last = None, (0, "")
        items, high, last, more = self.store.list_jobs(high, last, params["limit"])
        next_cursor = None
        if more:
            next_cursor = str(uuid.uuid4())
            self.cursors[next_cursor] = {"expires": now + 120, "context": dict(self.context), "high": high, "last": last}
        return {"items": items, "next_cursor": next_cursor}

    def close(self):
        if self._closed:
            return
        self._closed = True
        def cleanup():
            if self.store:
                self.store.close()
                self.store = self.context = None
            self.workspace.close()
        try:
            self._executor.submit(cleanup).result()
        finally:
            self._executor.shutdown(wait=True)
