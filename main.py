#!/usr/bin/env python

#pip install httpx
#pip install git+https://github.com/Vaelor/python-mattermost-driver.git

from mattermostdriver import Driver
import requests
import time
import os
import yaml

def main():
    print("read config")
    config = ""
    with open("/config/config.yaml", "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    if (config == ""):
        print("config is empty")
        return
    
    print("start login")
    driver = Driver({'url': config['url'], 'login_id': config['user'], 'token': config['token'], 'scheme': 'https', 'port': 443})
    driver.login()

    print("login successful")

    os.environ['TZ'] = 'Europe/Berlin'
    time.tzset()

    return driver

def refresh(driver, lastStatus):
    team = driver.teams.get_team_by_name('section77')
    channel = driver.channels.get_channel_by_name(team['id'], 'clubstatus')
    
    #get current time
    timestamp = time.strftime('%H:%M')

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

    lastStatus = True

    #execute every minute
    while True:
        lastStatus = refresh(driver, lastStatus)
        time.sleep(60)