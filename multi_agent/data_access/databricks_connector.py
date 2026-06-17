#C'est le fichier qui fait le lien: DATA ENGINEERING → INTELLIGENCE ARTIFICIELLE

class DatabricksConnector:
    """
    Connecteur entre Databricks et les agents IA
    """

    def load_data(self):
    #Simulation des données issues de Databricks
        return [
            {"text":"client cannot login"},
            {"text":"payment failed for order #1234"},
            {"text":"how to reset my password?"},
            {"text": "fraud detected on account"}
        ]