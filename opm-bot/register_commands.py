import requests
def register_command():
  APP_ID = ""
  BOT_TOKEN = ""
  
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