import requests

# BASE = "http://contradashboard.online"
BASE = "http://127.0.0.1:8000"

# response = requests.post(BASE+"/contra",{'name':'qwerty','phone':9998564854,'email':'likes','password':'qwe'})
# print(response.json())

response = requests.post(BASE+"/api/resetpassword",{'email':'parikh.madhav1999@gmail.com'},headers ={'Content-Type':'application/json'})
print(response.json())

# response = requests.get(BASE+"/contraEP2")
# print(response.json())
