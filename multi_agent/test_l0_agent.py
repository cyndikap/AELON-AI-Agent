from ui.azure_chat_llm import AzureChatLLM
from l0_agent import L0Agent

llm = AzureChatLLM()
l0 = L0Agent(
    llm=llm,
    kb_path="knowledge_base/it_support_kb.md"
)

queries = [
    "I cannot log into my online banking account",
    "My session expires immediately",
    "I want to change my mailing address"
]

for q in queries:
    print("\nUSER:", q)
    result = l0.handle(q)
    print("DECISION:", result["decision"])
    print("LLM OUTPUT:", result["llm_output"])