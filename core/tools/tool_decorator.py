from langchain_core.tools import tool
from core.tools.tool_registry import registry

def register_tool(name, domain, level="atomic", risk="low", description=None):
    def decorator(func):
        desc = description or func.__doc__

        if not desc:
            raise ValueError(f"Tool '{name}' must have a description")

        lc_tool = tool(name, description=desc)(func)

        registry.register(name, {
            "name": name,
            "func": lc_tool,
            "domain": domain,
            "level": level,
            "risk": risk,
            "description": desc,
        })

        return lc_tool

    return decorator