from azure_chat_llm import AzureChatLLM
from multi_agent.l1_agent import L1Agent

llm = AzureChatLLM()
agent = L1Agent(llm_callable=llm)

test_queries = [
    "User cannot log into online banking",
    "Multiple incorrect password attempts detected",
    "Login session expires immediately after success",
    "Customer reports suspicious authentication activity",
]

for i, query in enumerate(test_queries, start=1):
    print(f"\n=========== TEST {i} ===========")
    print(f"USER QUERY: {query}")

    result = agent.diagnose(query)

    print("\n--- AGENT RESPONSE ---")
    print(f"Summary       : {result['summary']}")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Confidence    : {result['confidence']}")
    print(f"Related Logs  : {result['related_logs']}")