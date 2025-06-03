import requests
import os

EXPANDING_KEY = os.environ.get("EXPANDING_KEY")
EXPANDING_SECRET = os.environ.get("EXPANDING_SECRET")
def send_messages(profile_link, custom_placeholder: str | None = None):
    print(profile_link, custom_placeholder)
    url = "https://api.liaufa.com/api/v1/open-api/campaign-instance/678395/assign/"
    params = {
        "key": os.getenv("EXPANDING_API_KEY"),
        "secret": os.getenv("EXPANDING_API_SECRET")
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = { 
        "profile_link": profile_link,   
        "custom_placeholder": custom_placeholder 
    }
    response = requests.post(url, params=params, headers=headers, json=data)
    return response.json()