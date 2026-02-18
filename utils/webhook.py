import requests

def webhook(message):
    payload = { "text": message }
    response = requests.post("", json=payload)
    if response.status_code == 200:
        return
    else:
        print(f"Error: {response.status_code}")