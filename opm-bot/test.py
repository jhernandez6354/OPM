import os
import requests
import json
import re

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

def hero(message, vHero):
  heroData = requests.get("https://opmdata.com/hero-list")
  heroStats = requests.get("https://opmdata.com/hero-stats")
  json_data = json.loads(heroData.text)
  stats_data = json.loads(heroStats.text)
  for hero in json_data:
    if hero['hero'] == vHero:
      #Since there is a character Limit, I'm only going to return their highest level abilities.
      result=hero['details']
      vSkillResult=''
      for key, skill in enumerate(hero['details']['skill'][0]):
        startLevel=0
        for vkey, lSkill in enumerate(skill):
          vSkillName=lSkill
          if int(skill[vSkillName][vkey]['level']) > int(startLevel):
            startLevel=skill[vSkillName][vkey]['level']
            vSkill=skill[vSkillName][vkey]['desc']
          vSkillResult+=vSkillName + ":** " + vSkill + "\n**"
      result="**"+hero['hero'] + "**" + \
        "\n**Type:** " + stats_data[hero['hero']][0]['base']['type'] + \
        "\n**Class:** " + stats_data[hero['hero']][0]['base']['class'] + \
        "\n**Characteristic:** " + stats_data[hero['hero']][0]['base']['characteristic'] + \
        "\n**Role:** " + stats_data[hero['hero']][0]['base']['role'] + \
        "\n**Stats:** **HP:** " + stats_data[hero['hero']][0]['base']['HP'] + "**Attack:** " + stats_data[hero['hero']][0]['base']['ATK'] + "**Defense:** " + stats_data[hero['hero']][0]['base']['DEF'] +\
        "\n***Skills***\n**" + vSkillResult +\
        "Limiter:** " + cleanhtml(hero['details']['limit'])
        
      print('{}'.format(result))

hero("",'Genos')