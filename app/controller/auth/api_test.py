import requests

BASE = "http://contradashboard.online"

response = requests.post(BASE+"/contra",{'name':'qwerty','phone':'views','email':'likes'})
print(response.json())

# response = requests.get(BASE+"/contraEP2")
# print(response.json())
