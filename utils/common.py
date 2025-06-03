import io
import time
import requests
import pandas as pd
from typing import Optional
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def getCSV(url: str, columns: list[str] = None) -> Optional[pd.DataFrame]:
    try:
        response = requests.get(url)
        response.raise_for_status()

        df = pd.read_csv(io.BytesIO(response.content), encoding="utf-8")

        if columns:
            # Kiểm tra xem tất cả các cột đều tồn tại
            missing = [col for col in columns if col not in df.columns]
            if missing:
                print(f"⚠️ Missing columns in CSV: {missing}")
                return None
            return df[columns]

        return df

    except Exception as e:
        print(f"❌ Error while reading CSV from URL: {e}")
        return None
def phantom_fetch_output(id: str, api_key: str) -> str:
        url = f"https://api.phantombuster.com/api/v2/agents/fetch-output?id={id}"
        headers = {
            "accept": "application/json",
            "X-Phantombuster-Key": api_key
        }
        while True:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                result = response.json()
                status = result.get('status', '')
                if status == "running":
                    print("Agent is still running... Waiting for completion.")
                    time.sleep(10)  # Đợi 10 giây rồi thử lại
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