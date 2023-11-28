from flask import session, request
from models import db, User


class Context:
    def __init__(self):
        self._data = {}
        self.endpoint = request.endpoint
        self.session_user = session.get("user")
        self.login_user = None
        if self.session_user:
            self.login_user = User.query.filter_by(
                id=int(self.session_user["id"])
            ).first()

    @property
    def data(self):
        return self._data

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]

    def __getattr__(self, name):
        if name.startswith("_"):
            return super().__getattr__(name)
        if name in self._data:
            return self._data[name]
        else:
            raise AttributeError(f"'Context' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        if name.startswith("_"):
            return super().__setattr__(name, value)
        # Dynamically handle attribute assignment
        self._data[name] = value

    def __delattr__(self, name):
        if name.startswith("_"):
            return super().__delattr__(name)
        if name in self._data:
            del self._data[name]
        else:
            raise AttributeError(f"'Context' object has no attribute '{name}'")

    def __repr__(self):
        return repr(self._data)

    def __iter__(self):
        return iter(self._data.items())
