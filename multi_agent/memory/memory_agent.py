class MemoryAgent:

    def __init__(self):
        self.memory = {}

    def update_memory(self, session_id, user_input, response):
        if session_id not in self.memory:
            self.memory[session_id] = []

        self.memory[session_id].append({
            "user": user_input,
            "assistant": response
        })

        # ✅ garder les 5 derniers échanges
        self.memory[session_id] = self.memory[session_id][-5:]

    def get_context(self, session_id):
        return self.memory.get(session_id, [])
