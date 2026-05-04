class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, name, spec):
        self._tools[name] = spec

    def get_all(self):
        return [t["func"] for t in self._tools.values()]

registry = ToolRegistry()