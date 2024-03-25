import re
import json
import os
import requests
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from dotenv import load_dotenv

load_dotenv()
PUBLIC_KEY = os.getenv("DISCORD_PUBLIC")

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

editions={
  "old": "Old World Edition",
  "music":"Music Festival Edition",
  "exotic":"Exotic World Edition",
  "future":"Future Tech Edition",
  "anniversary":"Anniversary Edition",
  "love":"Valentine's Day Edition",
  "easter":"Easter Edition",
  "spring":"Spring Carnival Edition",
  "summer":"Summer Party Edition",
  "autumn":"Autumn Festival Edition",
  "phantom":"Night Phantom Edition",
  "ice":"Ice Festival Edition",
}

abbr_editions={
  "old": "OWE",
  "music":"MFE",
  "exotic":"EWE",
  "future":"FTE",
  "anniversary":"AE",
  "love":"VDE",
  "easter":"EE",
  "spring":"SCE",
  "summer":"SPE",
  "harvest":"HFE",
  "phantom":"NPE",
  "ice":"IFE",
}

load_dotenv()
#Uncomment after making changes to the register command script
#from register_commands import register_command
#register_command()

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

def lambda_handler(event, context):
  try:
    body = json.loads(event['body'])
  except:
    body = event['body']
  signature = event['headers']['x-signature-ed25519']
  timestamp = event['headers']['x-signature-timestamp']

  # validate the interaction

  verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
  message = timestamp + json.dumps(body, separators=(',', ':'))
  
  try:
    verify_key.verify(message.encode(), signature=bytes.fromhex(signature))
  except BadSignatureError:
    pass
    #return {
    #  'statusCode': 401,
    #  'body': json.dumps('invalid request signature')
    #}
  
  # handle the interaction

  t = body['type']
  if t == 1:
    return {
      'statusCode': 200,
      'body': json.dumps({
        'type': 1
      })
    }
  elif t == 2:
    return command_handler(body)
  else:
    return {
      'statusCode': 400,
      'body': json.dumps('unhandled request type')
    }


def command_handler(body):
  command = body['data']['name']
  try:
    special=body['data']['options'][1]['value']
  except:
    special=None
  if command=='opm':
    #if command['message'].content.split(" ")[0].lower() == '$opm!sp':
    #  lang='-sp'
    #elif command['message'].content.split(" ")[0].lower() == '$opm!ru':
    #  lang='-ru'
    #else:
    lang=''
    return {
      'type': 4,
      'data': {
        'content': hero(command, body['data']['options'][0]['value'],special,lang),
      }
    }
  elif command == 'upcoming':
    #if ['message'].content.split(" ")[0].lower() == '$opm!sp':
    #  lang='-sp'
    #elif command['message'].content.split(" ")[0].lower() == '$opm!ru':
    #  lang='-ru'
    #else:
    lang=''
    return {
      'type': 4,
      'data': {
        'content': upcoming(command, lang),
      }
    }
  else:
    return 'unhandled command'

def check_input(vHero, hero, special):
  clean_name=hero['hero'].strip()
  #Strip Special Characters
  if "「" in hero['hero']:
    clean_name=" ".join(clean_name.split("「")[1].split("」")[0:2]) #I have no idea why some characters have these stupid symbols...
  #Rename to common names
  if 'bang' in vHero.lower() or 'silverfang' in vHero.lower(): #I'm doing it this way because most know him as fang.
    vHero='Silverfang (Bang)'
  #Clean up Abbreviations
  try:
    if ''.join(c for c in vHero if c.islower()) == "":
      abbrev=''.join([x[0].upper() for x in clean_name.split(' ')]).replace('-','')
      if len(abbrev)<=1:
        abbrev=None
    else:
      abbrev=None
  except:
    abbrev=None
  #Cleanup some commonly misspelled names (At least I spell them wrong a lot)
  if "siry" in vHero.lower():
    vHero='Suiryu'
  if "gorbi" in vHero.lower():
    vHero='Groribas'
  if "garu" in vHero.lower():
    vHero="Garou"
  if "goket" in vHero.lower():
    vHero="Gouketsu"
  #If they specified an edition, we need to parse it into the vHero String. Some names can have the edition before or after the hero name.
  #Sometimes the special edition name can be reversed on some characters (Night Phantom vs Phantom Night)
  #Finally Anniversary editions can be either "Anniversary Edition" or a year like "2023"
  if special is not None:
    if abbrev is None:
      if special == "anniversary":
        if "mumen" in vHero.lower(): #This can also be abbreviated
          vHero = "Mumen Rider - 2022 Edition"
        elif "suir" in vHero.lower():
          vHero = "Suiryu-2023 Edition"
        elif 'geno' in vHero.lower():
          vHero="Genos - Anniversary Edition"
        elif 'garou' in vHero.lower():
          vHero="Garou - 2nd Anniversary Edition"
        elif 'atomic' in vHero.lower():
            vHero="Atomic Samurai -3rd Anniversary Edition"#This can also be abbreviated
      if special == "phantom":
        if "metal" in vHero.lower() or 'bat' in vHero.lower(): #This can also be abbreviated
          vHero = 'Metal Bat - Phantom Night Edition'
        if "fuke" in vHero.lower():
          vHero = 'Fukegao - Phantom Night Edition'
        else:
          vHero = f"{vHero} - {editions[special]}"
      if special == 'summer':
        if 'flash' in vHero.lower(): #This can also be abbreviated
          vHero = "Flashy Flash - Summer Edition"
        else:
          vHero = f"{vHero} - {editions[special]}"
      if special in ['future','exotic','easter','music','ice']:
        vHero = f"{vHero} - {editions[special]}"
      if special == 'love':
        if 'ring' in vHero.lower():
          vHero = f"{vHero}- {editions[special]}" #This fucking game sometimes...
        else:
          vHero = f"{vHero}- {editions[special]}"
      if special == 'old':
        if 'speed' in vHero.lower():
          vHero='Speed-o\'-Sound Sonic - Old Word Edition'
        if vHero.lower() in ['boros', 'hellish','hellish blizzard', 'deep','deep sea', 'deep sea king', 'watchdog','watchdog man', 'child','child emperor','pig','pig god']:
          vHero = f"Old World {vHero}"
        else:
          vHero = f"{vHero} - {editions[special]}"
      #print("Looks like a regular or fuzzy search" + vHero)
    else:
      if special == 'summer':
        if 'FF' in vHero:
          vHero = "Flashy Flash - Summer Edition"
        else:
          vHero = f"{vHero}{abbr_editions[special]}"
      if special == "phantom":
        if "MB" in vHero:
          vHero = 'Metal Bat - Phantom Night Edition'
        else:
          vHero = f"{vHero}{abbr_editions[special]}"
      if special == "anniversary":
        if "MR" in vHero:
          vHero = "Mumen Rider - 2022 Edition"
        if 'AS' in vHero:
          vHero = "Atomic Samurai -3rd Anniversary Edition"
      if special in ['future','exotic','easter','music','ice']:
        vHero = f"{vHero}{abbr_editions[special]}"
      if special == 'love':
        if 'RR' in vHero:
          vHero = f"{vHero}{abbr_editions[special]}" #This fucking game sometimes...
        else:
          vHero = f"{vHero}{abbr_editions[special]}"
      if special == 'old':
        if 'SS' in vHero:
          vHero='Speed-o\'-Sound Sonic - Old Word Edition'
        elif vHero in ['HB', 'DSK', 'WM', 'WDM', 'CE','PG']:
          abbrev_ow='OW'
          vHero = f"{abbrev_ow}{vHero}"
        else:
          vHero = f"{vHero}{abbr_editions[special]}"
      #print(f"I got an abbreviated name: {vHero} which should match {abbrev}")
  #Case 1: Exact Match (Needed for heroes like King)
  #Case 2: Abbreviated Name
  #Case 3: Fuzzy search
  if clean_name.capitalize() == vHero.capitalize() or abbrev == vHero.upper() or (vHero.split("*")[0].capitalize() in hero['hero'].strip() and vHero.endswith("*")):
    #print(vHero)
    return True
  else:
    return False

def hero(message, vHero, special, lang):
  if len(''.join(e for e in vHero if e.isalnum())) > 1:
    if lang != '':
      v_lang=lang.split('-')[1]
    else:
      v_lang='en'
    heroData = requests.get(f"https://api.thelazygame.com/hero-list{lang}")
    json_data = json.loads(heroData.text)
    #heroStats = requests.get(f"https://api.thelazygame.com/hero-stats{lang}")
    #stats_data = json.loads(heroStats.text)
    hero_list=""
    temp_list=""
    for hero in json_data:
      if hero['details']['active'] is True:
        if check_input(vHero, hero, special):
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
            f"{d_lang[v_lang]['limiter']}:** " + cleanhtml(hero['details']['limit'])  + "\n"
            #f"\n***{d_lang[v_lang]['stat']}:*** **{d_lang[v_lang]['hp']}:** " + stats_data[hero['hero']][0]['base']['HP'] + f" **{d_lang[v_lang]['atk']}:** " + stats_data[hero['hero']][0]['base']['ATK'] + f" **{d_lang[v_lang]['def']}:** " + stats_data[hero['hero']][0]['base']['DEF'] +\
            #"\n**Type:** " + stats_data[hero['hero']][0]['base']['type'] + \
            #"\n**Class:** " + stats_data[hero['hero']][0]['base']['class'] + \
            #"\n**Characteristic:** " + stats_data[hero['hero']][0]['base']['characteristic'] + \
            #"\n**Role:** " + stats_data[hero['hero']][0]['base']['role'] + \
          temp_list+=result
          if len(temp_list) >=2000:
            break
          else:
            hero_list+=result
    return hero_list


def upcoming(message, lang):
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
  return result

