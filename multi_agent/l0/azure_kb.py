import os
from dotenv import load_dotenv

load_dotenv()

from azure.core.credentials import AzureKeyCredential

class AzureKB:

    def __init__(self, endpoint, index_name, api_key):
        self.endpoint = endpoint
        self.index_name = index_name
        self.api_key = api_key

    def search(self, query):
        # version simplifiée (simulation)
        return [
            {"text": "simulated result from Azure Search"}
        ]