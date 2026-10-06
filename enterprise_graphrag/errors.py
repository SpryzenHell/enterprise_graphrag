from __future__ import annotations


class BackendUnavailable(RuntimeError):
    """A configured external backend could not serve a request."""
