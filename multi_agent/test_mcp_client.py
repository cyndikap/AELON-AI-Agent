from mcp_client import MCPClient

client = MCPClient()

print("Fetching logs...")
logs = client.get_all_logs()
print(logs)

print("Creating a log...")
log = client.create_log(
    service="authentication",
    severity="warning",
    message="Test log from MCPClient"
)
print(log)

print("Creating an incident...")
incident = client.create_incident(
    category="fraud",
    description="Unauthorized login detected",
    customer_id="CUST-001"
)
print(incident)
