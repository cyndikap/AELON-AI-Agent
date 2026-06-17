from pathlib import Path

kb_path = r"C:\Users\MBASSEL\devs\ICA\mcp_multi_agent_V2\knowledge_base\it_support_kb.md"
#kb_path = r"./knowledge_base/it_support_kb.md"

class KnowledgeBase:
    def __init__(self, kb_path: str):
        self.kb_text = Path(kb_path).read_text(encoding="utf-8")

    def get_text(self) -> str:
        return self.kb_text
