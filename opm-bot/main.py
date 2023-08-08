import discord
import os
import requests
import json
import re
from discord.ext import commands
import os 
import platform
from dotenv import load_dotenv

load_dotenv()
if platform.python_version() >= '3.8.0':
  intents = discord.Intents.default()
  intents.message_content = True
  bot = commands.Bot(command_prefix='$',intents=intents)
else:
  bot = commands.Bot(command_prefix='$')

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

d_lang={
  "en": {
      "skill": "Skills",
      "blessing": "Blessing",
      "noblessing": "No Blessing",
      "limiter": "Limiter",
      "stat": "Stats",
      "atk": "Atk",
      "hp": "HP",
      "def": "Def"
  },
  "sp": {
      "skill": "Habilidades",
      "blessing": "Bendición",
      "noblessing": "Sin Bendición",
      "limiter": "Limitador",
      "stat": "Stats",
      "atk": "Atk",
      "hp": "HP",
      "def": "Def"
  },
  "ru": {
      "skill": "\u0421\u043f\u043e\u0441\u043e\u0431\u043d\u043e\u0441\u0442\u0438",
      "blessing": "\u0411\u043b\u0430\u0433\u043e\u0441\u043b\u043e\u0432\u0435\u043d\u0438\u0435",
      "noblessing": "\u041d\u0435\u0442\u0020\u0431\u043b\u0430\u0433\u043e\u0441\u043b\u043e\u0432\u0435\u043d\u0438\u044f",
      "limiter": "\u041e\u0433\u0440\u0430\u043d\u0438\u0447\u0438\u0442\u0435\u043b\u044c",
      "stat": "Stats",
      "atk": "Atk",
      "hp": "HP",
      "def": "Def"
  }
}

@bot.command(name='opm')
async def hero(message, vHero, lang):
  if len(''.join(e for e in vHero if e.isalnum())) > 1:
    if lang != '':
      v_lang=lang.split('-')[1]
    else:
      v_lang='en'
    heroData = requests.get(f"https://api.thelazygame.com/hero-list{lang}")
    json_data = json.loads(heroData.text)
    #heroStats = requests.get(f"https://api.thelazygame.com/hero-stats{lang}")
    #stats_data = json.loads(heroStats.text)
    for hero in json_data:
      if hero['details']['active'] is True:
        clean_name=hero['hero']
        if "「" in hero['hero']:
          clean_name=" ".join(clean_name.split("「")[1].split("」")[0:2]) #I have no idea why some characters have these stupid characters...
        clean_name=clean_name.strip()
        if vHero.lower() == 'bang' or vHero.lower() == 'silverfang': #I'm doing it this way because most people wont type in the full thing when doing the non-fuzzy search.
          vHero='Silverfang (Bang)'
        try:
          abbrev=''.join([x[0].upper() for x in hero['hero'].split(' ')]).split("-")[0]
        except:
          abbrev=None
        if clean_name == vHero.capitalize() or abbrev == vHero.upper() or (vHero.split("*")[0].capitalize() in hero['hero'] and vHero.endswith("*")):
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
              vSkillResult+=vSkillName + ":** " + cleanhtml(vSkill) + "\n - **"
          vSkillResult=vSkillResult[:-5]
          try: 
            blessing=f"- **{d_lang[v_lang]['blessing']}:** " + cleanhtml(hero['details']['blessing']['bless_desc']) + "\n- **"
          except:
            blessing=f"- **{d_lang[v_lang]['noblessing']}**\n- **"
          result="__**"+hero['hero'] + "**__" + \
            f"\n- ***{d_lang[v_lang]['skill']}***\n - **{vSkillResult}" +\
            blessing +\
            f"{d_lang[v_lang]['limiter']}:** " + cleanhtml(hero['details']['limit'])
            #f"\n***{d_lang[v_lang]['stat']}:*** **{d_lang[v_lang]['hp']}:** " + stats_data[hero['hero']][0]['base']['HP'] + f" **{d_lang[v_lang]['atk']}:** " + stats_data[hero['hero']][0]['base']['ATK'] + f" **{d_lang[v_lang]['def']}:** " + stats_data[hero['hero']][0]['base']['DEF'] +\
            #"\n**Type:** " + stats_data[hero['hero']][0]['base']['type'] + \
            #"\n**Class:** " + stats_data[hero['hero']][0]['base']['class'] + \
            #"\n**Characteristic:** " + stats_data[hero['hero']][0]['base']['characteristic'] + \
            #"\n**Role:** " + stats_data[hero['hero']][0]['base']['role'] + \

          await message.channel.send('{}'.format(result))

@bot.command(name='upcoming')
async def upcoming(message, lang):
  heroData = requests.get(f"https://api.thelazygame.com/hero-list{lang}")
  json_data = json.loads(heroData.text)
  result=[]
  for hero in json_data:
    if hero['details']['active'] is False:
      try:
        result.append(hero['hero'])
      except:
        result=[hero['hero']]
  result="- "+"\n- ".join(result)
  await message.channel.send('{}'.format(result))

@bot.event
async def on_ready():
  print('We have logged in as {0.user}'.format(bot))
  
@bot.event
async def on_message(message):
  if message.author == bot.user:
    return
  if message.content.startswith('$opm') and message.content.split(" ")[1].lower() != 'upcoming':
    if message.content.split(" ")[0].lower() == '$opm!sp':
      lang='-sp'
    elif message.content.split(" ")[0].lower() == '$opm!ru':
      lang='-ru'
    else:
      lang=''
    await hero(message, message.content.split(' ',1)[1],lang)
  elif message.content.startswith('$opm') and message.content.split(" ")[1].lower() == 'upcoming':
    if message.content.split(" ")[0].lower() == '$opm!sp':
      lang='-sp'
    elif message.content.split(" ")[0].lower() == '$opm!ru':
      lang='-ru'
    else:
      lang=''
    await upcoming(message, lang)

bot.run(os.getenv("DISCORD_TOKEN"))  
