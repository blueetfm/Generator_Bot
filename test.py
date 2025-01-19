import requests
import json

base_url = "https://api.telegram.org/bot7175031755:AAFffMwivVxUvhSDjyO4Gt8cNd4Oz9rDOYU/sendPoll"

parameters = {
    "chat_id" : "insert chat id",
    "question" : "are you alive or not",
    "options" : json.dumps(["yes", "no"])
}

resp = requests.get(base_url, data = parameters)
print(resp.text)