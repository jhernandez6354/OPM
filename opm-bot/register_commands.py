import requests
from dotenv import load_dotenv
import os
load_dotenv()
def register_command():
  APP_ID = "873055299299315712"
  BOT_TOKEN = os.getenv("DISCORD_TOKEN")
  
  # global commands are cached and only update every hour
  url = f"https://discord.com/api/v10/applications/{APP_ID}/commands"
  
  json = [
    {
        "name": "opm",
        "description": "Search hero based on full name, initials, or wildcard (*) ex. Terrible Tornado, or TT, or Terr*.",
        "options": [
          {
            "type": 3,
            "name": "hero",
            "description": "Hero Name",
            "required": 1
          },
          {
            "name": "edition",
            "description": "Special Editions of the Hero",
            "type": 3,
            "required": False,
            "choices": [
              {
                  "name": "Old World",
                  "value": "old"
              },
              {
                  "name": "Music Festival",
                  "value": "music"
              },
              {
                  "name": "Exotic World",
                  "value": "exotic"
              },
              {
                  "name": "Future Tech",
                  "value": "future"
              },
              {
                  "name": "Anniversary",
                  "value": "anniversary"
              },
              {
                  "name": "Valentine's Day",
                  "value": "love"
              },
              {
                  "name": "Easter Edition",
                  "value": "easter"
              },
              {
                  "name": "Spring Carnival",
                  "value": "spring"
              },
              {
                  "name": "Summer Party",
                  "value": "summer"
              },
              {
                  "name": "Autumn Festival",
                  "value": "autumn"
              },
              {
                  "name": "Phantom Night",
                  "value": "phantom"
              },
              {
                  "name": "Ice Festival",
                  "value": "ice"
              }
            ]
        }
        ]
    },{
        "name": "upcoming",
        "description": "Returns the latest known heroes that will soon release to One Punch Man: Road to Hero 2.0.",
        "options": []
    }
  ]
  response = requests.put(url, headers={
    "Authorization": f"Bot {BOT_TOKEN}"
  }, json=json)
  print(response)

register_command()