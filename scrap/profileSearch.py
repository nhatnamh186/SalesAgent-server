import requests
import json
import time

class ProfileSearcher:
    def __init__(self, agent_id, api_key):
        self.agent_id = agent_id
        self.api_key = api_key
        self.base_url = 'https://api.phantombuster.com/api/v2/agents'
        self.headers = {
            'Content-Type': 'application/json',
            'x-phantombuster-key': api_key,
        }
    def launch_agent(self):
        data = json.dumps({"id": self.agent_id})
        response = requests.post(f'{self.base_url}/launch', headers=self.headers, data=data)
        if response.status_code == 200:
            print("Agent launched successfully.")
        else:
            print(f"Error: {response.status_code}, {response.text}")
    def fetch_output(self):
        while True:
            response = requests.get(f"{self.base_url}/fetch-output?id={self.agent_id}", headers=self.headers)
            if response.status_code == 200:
                result = response.json()
                status = result.get('status', '')

                print(f"Current status: {status}")

                if status == "running":
                    print("Agent is still running... Waiting for completion.")
                    time.sleep(10) 
                    continue

                output_text = result.get('output', '')
                csv_url = None

                for word in output_text.split():
                    if word.startswith("https://") and word.endswith(".csv"):
                        csv_url = word
                        break

                return csv_url
            else:
                print(f"Error: {response.status_code}, {response.text}")
                return None
