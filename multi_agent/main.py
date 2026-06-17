from orchestrator import Orchestrator

orch =Orchestrator()

query =" Icannot access my account and my card is bloqued" 

response = orch.handle_user_query(query)

print(response)