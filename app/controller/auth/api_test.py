import requests

BASE = "http://127.0.0.1:8000"

response = requests.post(BASE+"/contra",{'name':'qwerty','phone':'views','email':'likes'})
print(response.json())

# response = requests.get(BASE+"/contraEP2")
# print(response.json())
