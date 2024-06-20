import json
import re
import os

def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).encode('ascii', errors='ignore').strip().decode('ascii')

def remove_punctuation(text):
    return re.sub("[^a-zA-Z0-9,'%()]".format(text), ' ', text).rstrip()

def remove_lvl(text):
    if text.startswith('Lv'):
        return text[5:].lstrip()
    else:
        return text
    
def talents(name, talents,file):
    i=1
    parsed={}
    for talent in talents:
        for ability in talent[list(talent.keys())[0]]:
            parsed[i]=remove_lvl(remove_punctuation(remove_html_tags(ability['desc'])))
            i+=1
    write_to_file(name, "talent", parsed,file)

def skill(name, skills,file):
    parsed={}
    parse_list={}
    x=1
    for skill_list in skills:
        for skill in skill_list:
            i=1
            for ability in skill[list(skill.keys())[0]]:
                parsed[i]=remove_lvl(remove_punctuation(remove_html_tags(ability['desc'])))
                i+=1
            if x==1:
                slot="normal"
            elif x==2:
                slot="active"
            elif x==3:
                slot="passive1"
            else:
                slot="passive2"
            parse_list[slot]=parsed
            parsed={}
            x+=1
    write_to_file(name, "skills", parse_list,file)

def blessing(name, blessing,file):
    if len(blessing) > 0:
        write_to_file(name,"blessing",remove_punctuation(remove_html_tags(blessing['bless_desc'])),file)
    else:
        write_to_file(name,"blessing","None",file)

def limit(name, limit,mega,file):
    if mega is True:
        limiter="mega_limit"
    else:
        limiter="limit"
    write_to_file(name,limiter,remove_html_tags(limit),file)

def write_to_file(name,ability,text,ability_file):
    if not os.path.exists(ability_file):
        with open(ability_file, 'w'): pass
    if os.stat(ability_file).st_size == 0:
        vdict={name:{ability:text}}
        with open(ability_file, 'w+') as f: json.dump(vdict,f)
    with open(ability_file, 'r+') as f:
        data = json.load(f)
        try:
            data[name][ability]=text
        except:
            data[name] = {ability:text}
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()     # remove remaining part

def clean_abilities(hero,file):
    hero_abilities={}
    for entry in hero:
        if entry['details']['active'] is True:
            talents(entry['hero'],entry['details']['talent'],file)
            skill(entry['hero'],entry['details']['skill'],file)
            blessing(entry['hero'],entry['details']['blessing'],file)
            limit(entry['hero'],entry['details']['limit'],False,file)
            limit(entry['hero'],entry['details']['mega_limit'],True,file)
    return hero_abilities