class DomainError(Exception):
    """A closed domain denial; deliberately carries no dossier or path."""

    def __init__(self, code: str):
        if code not in {"HOME_CONTEXT", "HOME_WRITER_EXISTS", "RECOVERY_INACTIVE", "OPERATION_ID_CONFLICT"}:
            raise ValueError("Unknown foundation denial")
        self.code = code
        super().__init__(code)


class StoreError(Exception):
    """Internal store failure. Future RPC maps this to -32603, never raw details."""
