from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, ToolMessage
from core.tools.tool_registry import registry
import core.tools # Leave import as it is loading tools
import json

BASE_DIR = Path(__file__).resolve().parents[1]
PROMPTS_DIR = BASE_DIR / "prompts"

MODEL = "gemma4:31b-cloud"

class LLMClient:
    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader(str(PROMPTS_DIR)),
            autoescape=select_autoescape()
        )

        self.tools = registry.get_all()

        self.llm = ChatOllama(
            model=MODEL,
            temperature=0
        ).bind_tools(self.tools)

        self.tool_map = {t.name: t for t in self.tools}

    def run(self, payload: dict) -> dict:
        context = payload.get("context", "")
        user = payload.get("user", "")

        template = self.env.get_template("general_prompt.j2")
        prompt = template.render(context=context, user=user)

        messages = [HumanMessage(content=prompt)]

        for _ in range(3):  # limit tool loop depth
            response = self.llm.invoke(messages)
            messages.append(response)

            # ---- tool call detected ----
            if response.tool_calls:
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]

                    tool = self.tool_map.get(tool_name)

                    if not tool:
                        continue

                    result = tool.invoke(tool_args)

                    messages.append(
                        ToolMessage(
                            content=json.dumps(result),
                            tool_call_id=tool_call["id"]
                        )
                    )

                continue  # loop back to LLM with tool result

            # ---- final response ----
            return self._normalize_output(response.content)

        return {"response": "Tool loop exceeded", "notepad": ""}

    def _normalize_output(self, result: str) -> dict:
        if not isinstance(result, str):
            result = str(result)

        cleaned = result.strip()

        if cleaned.startswith("```"):
            parts = cleaned.split("```")
            if len(parts) >= 2:
                cleaned = parts[1].strip()

        try:
            parsed = json.loads(cleaned)

            if not isinstance(parsed, dict):
                raise ValueError("Not dict")

            parsed.setdefault("response", "")
            parsed.setdefault("notepad", "")

        except Exception:
            parsed = {
                "response": cleaned,
                "notepad": ""
            }

        return parsed