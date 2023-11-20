import requests


def send_message(token, users, message, title):
    for user in users:
        data = {
            'token': token,
            'user': users,
            'title': title,
            'message': message
        }
        requests.post("https://api.pushover.net/1/messages.json", data=data)
 
 