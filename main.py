#!/usr/bin/env python

#pip install httpx
#pip install git+https://github.com/Vaelor/python-mattermost-driver.git

from mattermostdriver import Driver
import requests
import datetime
import time
import yaml

#async def my_event_handler(message):
    #print(message)
#    pass

def main():
    print("read config")
    config = ""
    with open("/home/tuff/Documents/section77/mattermost-spaceapi/s77-status-bot-config.yaml", "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    if (config == ""):
        print("config is empty")
        return
    
    print("start login")
    driver = Driver({'url': config['url'], 'login_id': config['user'], 'password': config['password'], 'scheme': 'https', 'port': 443})
    driver.login()
    
    #driver.init_websocket(my_event_handler)
    #driver.disconnect()

    print("login successful")

    return driver

def refresh(driver, lastStatus):
    team = driver.teams.get_team_by_name('section77')
    channel = driver.channels.get_channel_by_name(team['id'], 'test-python-api')
    
    #get current time
    hour = str(datetime.datetime.now().strftime("%H"))
    minute = str(datetime.datetime.now().strftime("%M"))
    timestamp = f"{hour}:{minute}"

    #get spaceapi status
    response = requests.get('https://api.section77.de')
    status = response.json()['state']['open']

    #if state has changed
    if (lastStatus != status):
    
        #create message
        message = ""
        name = ""
        if (status):
            message = f'{timestamp} Die Section77 ist offen'
            name = "Status: Offen"
        else:
            message = f'{timestamp} Die Section77 ist geschlossen'
            name = "Status: Geschlossen"
    
        #send message
        post = driver.posts.create_post({
            'channel_id': channel['id'],
            'message': message
        })
        #update room name
        driver.channels.patch_channel(channel['id'], {'id': channel['id'], 'display_name': name})

        #log message
        print(f"Nachricht \"{message}\" gesendet!")
    return status

if __name__ == '__main__':
    #execute once
    driver = main()

    lastStatus = False

    #execute every minute
    while True:
        lastStatus = refresh(driver, lastStatus)
        time.sleep(60)

