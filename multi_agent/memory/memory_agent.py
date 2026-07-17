from multi_agent.privacy.privacy_agent import PrivacyAgent


class MemoryAgent:

    def __init__(self):
        self.memory = {}
        self.privacy = PrivacyAgent()

    def update_memory(self, session_id, user_input, response):
        if session_id not in self.memory:
            self.memory[session_id] = []

        safe_user = self.privacy.process(user_input, language="fr").get("anonymized_text", user_input)
        safe_assistant = self.privacy.process(response, language="fr").get("anonymized_text", response)

        self.memory[session_id].append({
            "user": safe_user,
            "assistant": safe_assistant
        })

        # ✅ garder les 5 derniers échanges
        self.memory[session_id] = self.memory[session_id][-5:]

    def get_context(self, session_id):
        return self.memory.get(session_id, [])
