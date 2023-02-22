import json
import codecs
import re #Used to remove the <material markup
from ppadb.client import Client as AdbClient
import os
#This assumes these files exist in the csv folder and will save them to their own maps to be used later.
#The files in \Storage\Android\data\com.alpha.mpsen.android\cache\DiffConfig and are subject to change weekly.
lang='Default_English'

#BaseStats               HeroQualityProperty, HeroLevel, and Hero
#Essense Laboratory      HeroAcademyLevel
#Class Essence           HeroJobLevel
#Battle Will             HeroLevelGrowth                
#Hero Quality            HeroQualityProperty
#Cards                   CollectFrame, CollectLevel, and CollectGroupAddition
#Machine Core            MechanicalPowerLevel
#Talent                  HeroTalentAttribute
#Gear                    Equip, CombatAttribute (see mCombatAttr mapping)
#Limiter Breakthrough    HeroLimiter
#                        HeroGradeProperty
#Bots Level              DroidLevelGrowth
#Bots Quality            DroidStar

lFiles=[  #There should be a function that matches each name in this list, which tell genMappings how to read to file.
    lang,
    'HeroLimiter',
    'HeroSkillDesc',
    'Hero',
    'HeroQualityProperty',
    'HeroLevelGrowth',
    'HeroJobLevel',
    'HeroAcademyLevel',
    'HeroGradeProperty',
    'MechanicalPowerLevel',
    'HeroTalentAttribute',
    'Equip',
    'CollectFrame',
    'CollectLevel',
    'CollectGroupAddition',
    'DroidLevelGrowth',
    'DroidStar'
]

mBotType={ #I recorded this, but Hero isn't reliable for this data, so I need to find it somewhere else.
    1: 'Weapon',
    2: 'Future',
    3: 'Technical'
}

mType={
    1: 'Agile',
    2: 'Psychic',
    3: 'Tech',
    4: 'Physical',
    5: 'Complete',
    6: 'Old World'
}

mCharacteristic={
    1: 'Fearless',
    2: 'Agile',
    3: 'Tactical'
}

mRole={ 
    1: 'Damage over Time',
    2: 'Burst Damage',
    3: 'Group Attack',
    4: 'Control',
    5: 'Tank',
    6: 'Assassin',
    7: 'Healer',
    8: 'Debuff',
    9: 'Buff'
}

mClass={
    1: 'Fortifier',
    2: 'Sentinel',
    3: 'Rescuer',
    4: 'Infiltrator',
    5: 'Bombarder'
}

mQuality={
    1: 'Rough',
    2: 'Common',
    3: 'Rare',
    4: 'Rare+',
    5: 'Elite',
    6: 'Elite+',
    7: 'Epic',
    8: 'Epic+',
    9: 'Lgendary',
    10: 'Legendary+',
    11: 'Mythical',
    12: 'Mythical*',
    13: 'Mythical**',
    14: 'Mythical***',
    15: 'Mythical****',
    16: 'Mythical*****'
}

mCombatAttr={
    20:'Max HP',
    21:'HP',
    22:'Max HP',
    23:'Final HP', #If 20, then = HP 0.2%
    30:'ATK',
    31:'ATK',
    32:'ATK',
    33:'Final ATK',
    40:'DEF',
    41:'DEF',
    42:'DEF',
    43:'Final DEF',
    50:'DR',
    51:'DR',
    60:'CRIR',
    61:'CRIR',
    70:'CRIC',
    71:'CRIC',
    80:'CRID',
    81:'CRID',
    140:'PAR',
    150:'ACC',
    162:'DR',
    163:'DR',
    172:'DMG Dealt',
    173:'DMG Dealt',
    190:'ACC',
    191:'ACC',
    300:'PAR',
    201:'PAR',
    253:'Rage GEN'
}

mFrame={
    1:'Basic',
    2:'Common',
    3:'Rare',
    4:'Elite',
    5:'Legendary',
    6:'Flash'
}

mGroup={
    1:'Gathering A',
    2:'Gathering B',
    3:'Invasion A',
    4:'Invasion B'
}

mSlot={
    1: 'Weapon',
    2: 'Helmet',
    3: 'Clothes',
    4: 'Shoes'
}

invalidHeroes=[ #These heroes are capable of being mythic heroes, but do not have 4 abilities. Fucking up my scripts...
    'ghost',
    'snowman',
    'eggmonster',
    'saitama3year'
]

data_path="hero_data\\"

def adb_pull_files():
    client=AdbClient(host="127.0.0.1", port=5037)
    file_path=os.getcwd()+"\csv"
    device = client.device("127.0.0.1:62001")
    opm_data_path="/mnt/user/0/primary/Android/data/com.alpha.mpsen.android/cache/DiffConfig"
    files=device.shell(f"ls {opm_data_path}")
    print("Attempting to retrieve game data files.")
    try:
        for file in files.split():
            device.pull(f"{opm_data_path}/{file}",f"{file_path}\{file}")
        print("Successfully pulled files into csv directory.")
    except Exception as error:
        print(error)        

#When parsing their CSV files, * is a delimiter as well.
def genMappings():
    dFiles={}
    for fName in lFiles:
        dFiles[fName]=[]
        file_name="csv/"+fName+'.csv' 
        print("Mapping out "+ file_name)
        reader = codecs.open(file_name, 'r', encoding='utf-8')
        dFiles[fName]=eval(fName)(reader)
    return dFiles

def Default_English(reader):
    #Standard formatting: *10421573*Metal Bat Rare Card Frame *
    dText={}
    for line in reader:
        row = line.split('\\n')
        if not row[0].startswith("#"): #All of these files start with a commented descriptor.
            stringID=row[0].split('*')[1]
            stringText=row[0].split('*')[2]
            dText[stringID]=stringText
    try:
       dText
    except:
        dText=None
    return dText

def Hero(reader):
    dLine={}
    for line in reader:
        row = line.split('\\n')
        if not row[0].startswith("#"): #All of these files start with a commented descriptor.
            hero=True  
            row=row[0].split('*')
            if int(row[1]) >= 20000: #Bots are in this range
                hero=False    
            if int(row[1]) < 2000 and row[1] != '' and row[9] not in invalidHeroes and int(row[2]) > 2: #10000 heroes are unplayable bosses or test heroes. Also, exclude heroes that don't have a name. Finally, exclude any heroes of "Quality" 2 or less.
                #['', '1', '3', '3', '1', '5', '8', '200110001', '2001042', 'fukegao', 'fukegao', '', '', '10012', '10011,10013,10014', '', '10011,10012,10013,10014', '496', '130', '46', '500', '0', ''
                # , 'attack,skill', '10010', '10003,20001,30004', '2001043', '10015', '0', '393', '33,25,1', '2.0.23', '', '1', '1', '4', '61,44,0.9', '0', '5,-22', '0', '2', '\n']
                if  row[9] != '':
                    skill=int(row[14].split(',')[0])
                    mString={
                        'hero': True,
                        'heroid':row[1],
                        'heronameid':row[7],
                        'shortname': row[9],
                        'type': mType[int(row[3])],
                        'role': mRole[int(row[5])],
                        'characteristic': mCharacteristic[int(row[4])],
                        'class': mClass[int(row[35])],
                        'hp': row[17],
                        'atk': row[18],
                        'def': row[19],
                        'skill0': str(skill), 
                        'skill1': str(skill+1),
                        'skill2': str(skill+2),
                        'skill3': str(skill+3),
                        'talent': str(skill+4)#I know it's stupid, but at least they are consistent.
                    }
                    dLine[row[1]]=mString
            if hero is False and int(row[14]) != 0 and int(row[1]) > 1 and int(row[1]) > 20000: # Exclude bots that dont' have skills and bots less than "blue" quality
                mString={
                    'hero': False,
                    'heroid':row[1],
                    'heronameid':row[7],
                    'shortname': row[7],
                    'hp': row[17],
                    'atk': row[18],
                    'def': row[19],
                    'skill0': row[16].split(',')[0],
                    'skill1':  str(int(row[16].split(',')[0])+1)
                }
                dLine[row[1]]=mString
    try:
        dLine
    except:
        dLine=None
    return dLine

def HeroSkillDesc(reader):
    #*103821*10382*1*300003820*300003821*50%*0*
    dLine={}
    for line in reader:
        row = line.split('\\n')
        if not row[0].startswith("#"): #All of these files start with a commented descriptor.
            mString={row[0].split('*')[1]:{ #They simply append 1-5 to the end of the id to get the talent id.
                'level': row[0].split('*')[3], 
                'name': row[0].split('*')[4],
                'desc': row[0].split('*')[5],
                'perct': row[0].split('*')[6],
                'val': row[0].split('*')[7],
            }}
            try: #The first entry for the individual skill will throw an error without this.
                dLine[row[0].split('*')[2]].update(mString) #Then set the base skill id as the key for all skill level ids.
            except:
                dLine[row[0].split('*')[2]]=mString #Create a map list of all skill levels and associate them to a single skill id.
    try:
       dLine
    except:
        dLine=None
    return dLine

def HeroLimiter(reader):
    #*230*38*10*21,35712;31,19702;41,9230;22,175;32,525;42,311*30103802*50%*21,0;31,33981;41,0;22,0;32,1575;42,0*21,0;31,16990;41,0;22,0;32,787;42,0*30203801*2038*21,4411;31,2433;41,1164;22,175;32,525;42,311*21,0;31,4197;41,0;22,0;32,1575;42,0*21,0;31,2098;41,0;22,0;32,787;42,0
    dLine={}
    for line in reader:
        row = line.split('\\n')
        if not row[0].startswith("#"): #All of these files start with a commented descriptor.
            mLimStat={}
            mString={
                'desc': row[0].split('*')[5],
                'descval':row[0].split('*')[6],
                row[0].split('*')[3]:{
                'perct': row[0].split('*')[6],
                'hp': row[0].split('*')[4].split(';')[0].split(',')[1],
                'atk': row[0].split('*')[4].split(';')[1].split(',')[1],
                'def': row[0].split('*')[4].split(';')[2].split(',')[1]
                
            }}
            try: #The first entry for the individual skill will throw an error without this.
                dLine[row[0].split('*')[2]].update(mString) #Then set the base skill id as the key for all skill level ids.
            except:
                dLine[row[0].split('*')[2]]=mString #Create a map list of all skill levels and associate them to a single skill id.
    try:
       dLine
    except:
        dLine=None
    return dLine

def HeroQualityProperty(reader): #You can upgrade the quality of the hero, like moving from purple to red, etc
    #*1*1*1*10000*10000*10000*0*0*0*21,1;31,1;41,1*21,1;31,1;41,1*21,1;31,1;41,1*21,1;31,1;41,1*21,1;31,1;41,1*21,1;31,1;41,1*
    dLine={}
    for line in reader:
        row = line.split('\\n')
        if not row[0].startswith("#"): #All of these files start with a commented descriptor.
            mString={
                 mQuality[int(row[0].split('*')[3])]:{ #We are keeping the stats of all quality levels
                    'hp': row[0].split('*')[10].split(';')[0].split(',')[1], #I'm not yet sure how these values calculate as raw stats.
                    'atk': row[0].split('*')[10].split(';')[1].split(',')[1], #But I know that 21 translates to HP, 31 = ATK, and 41 = DEF.
                    'def': row[0].split('*')[10].split(';')[2].split(',')[1], #I'm also not sure why there are 6 entries with stats data.
                }
            }
            try:
                dLine[row[0].split('*')[2]].update(mString)
            except:
                dLine[row[0].split('*')[2]]=mString
            
    try:
       dLine
    except:
        dLine=None
    return dLine

def HeroLevelGrowth(reader):  #Battle Will
    #*1*1*1*0*18*3*1*
    #*2*2*1*0*35*7*2*
    dLine={}
    for line in reader:
        row = line.split('\\n')
        if not row[0].startswith("#"): #All of these files start with a commented descriptor.
            mString={ #Once the level hits 240, it each level has 10 sublevels.
                row[0].split('*')[4]: {
                    'hp': row[0].split('*')[5],
                    'atk': row[0].split('*')[6],
                    'def': row[0].split('*')[7],
                }
            }
            try: 
                dLine[row[0].split('*')[2]].update(mString) 
            except:
                dLine[row[0].split('*')[2]]=mString
    try:
       dLine
    except:
        dLine=None
    return dLine

def DroidLevelGrowth(reader):  #Bots Level
    #*240*20002*120*24000*4800*1031755*108607*19163*6000*
    #*241*20003*1*0*0*180*18*3*0*
    dLine={}
    for line in reader:
        row = line.split('\\n')
        if not row[0].startswith("#"): #All of these files start with a commented descriptor.
            mString={ #Once the level hits 240, it each level has 10 sublevels.
                row[0].split('*')[3]: {
                    'hp': row[0].split('*')[6],
                    'atk': row[0].split('*')[7],
                    'def': row[0].split('*')[8],
                }
            }
            try: 
                dLine[row[0].split('*')[2]].update(mString) 
            except:
                dLine[row[0].split('*')[2]]=mString
    try:
       dLine
    except:
        dLine=None
    return dLine

def DroidStar(reader):  #Bots Quality
    #*60*5*20012*1500*0*0*0*40000*40000*40000*20000*
    #*61*1*20013*30*0*0*0*10000*10000*10000*10000*
    dLine={}
    for line in reader:
        row = line.split('\\n')
        if not row[0].startswith("#"): #All of these files start with a commented descriptor.
            mString={ #Once the level hits 240, it each level has 10 sublevels.
                row[0].split('*')[2]: {
                    'hp': str(int(row[0].split('*')[7])/1000)+'%',
                    'atk': str(int(row[0].split('*')[8])/1000)+'%',
                    'def': str(int(row[0].split('*')[9])/1000)+'%',
                }
            }
            try: 
                dLine[row[0].split('*')[3]].update(mString) 
            except:
                dLine[row[0].split('*')[3]]=mString
    try:
       dLine
    except:
        dLine=None
    return dLine

def HeroJobLevel(reader): #Class Essence 
    # *10*1*10*160*
    # 21,9172;31,740;41,1200;60,140;50,140  This is our mClassStat mapping
    # *1,2,3*2,0,0*21,28280;31,2392;41,3264;60,140;50,140*  I'm not yet sure what this part is for.
    dLine={}
    for line in reader:
        row = line.split('\\n')
        if not row[0].startswith("#"): #All of these files start with a commented descriptor.
            mClassStat={}
            for stat in  row[0].split('*')[5].split(';'):
                try:
                    mClassStat[mCombatAttr[int(stat.split(',')[0])]].update(stat.split(',')[1]) #There are a varying amount of values that can be here, so we are creating custom maps of each stat.
                except:
                     mClassStat[mCombatAttr[int(stat.split(',')[0])]]=stat.split(',')[1] #Most should trigger the exception, and use this to build the stat.
            mString={ #Instead of a hero ID, we reference mClass name associated to the hero.
                row[0].split('*')[3]: mClassStat #There are currently 150 class levels (Subject to change in future updates.)
            }
            try:
                dLine[mClass[int(row[0].split('*')[2])]].update(mString) #I'm adding 30000 to reuse mClass which exists in hero.csv as well, but as 30001 instead of 1.
            except:
                 dLine[mClass[int(row[0].split('*')[2])]]=mString
    try:
       dLine
    except:
        dLine=None
    return dLine

def HeroAcademyLevel(reader): #Essense Laboratory 
    # *268*268*24
    # *21,652664;31,113562;41,102606*150
    # *21,55140;31,9247;41,10514*   I'm not sure why there is a second list of stats
    dLine={}
    for line in reader:
        row = line.split('\\n')
        if not row[0].startswith("#"): #All of these files start with a commented descriptor.
            mString={#As of 2.2.23, it doesn't matter if we use the index or the second field for the level.
                'hp': row[0].split('*')[6].split(';')[0].split(',')[1], 
                'atk': row[0].split('*')[6].split(';')[1].split(',')[1],
                'def': row[0].split('*')[6].split(';')[2].split(',')[1], 
            }
            try:
                dLine[row[0].split('*')[2]].update(mString) 
            except:
                dLine[row[0].split('*')[2]]=mString 
    try:
       dLine
    except:
        dLine=None
    return dLine

def HeroGradeProperty(reader): #Not sure yet what the hero grade is supposed to be for, but it has 20 levels per hero
    #*1961*88*1*133*46*11*
    dLine={}
    for line in reader:
        row = line.split('\\n')
        if not row[0].startswith("#"): #All of these files start with a commented descriptor.
            mString={
                 row[0].split('*')[3]:{ #We are keeping the stats of all quality levels
                    'stat1': row[0].split('*')[4], #Calling these stat1,2 and 3 until I figure out what they do.
                    'stat2': row[0].split('*')[5],
                    'stat3': row[0].split('*')[6],
                }
            }
            try:
                dLine[row[0].split('*')[2]].update(mString)
            except:
                dLine[row[0].split('*')[2]]=mString
    try:
       dLine
    except:
        dLine=None
    return dLine

def MechanicalPowerLevel(reader): #Machine Core
    #*330*21*30*47000*2350000*21,594786;31,100437;41,99599*21,66982;31,11310;41,11450*
    dLine={}
    for line in reader:
        row = line.split('\\n')
        if not row[0].startswith("#"): #All of these files start with a commented descriptor.
            mString={ 
                row[0].split('*')[3]: {
                'hp': row[0].split('*')[6].split(';')[0].split(',')[1],
                'atk': row[0].split('*')[6].split(';')[1].split(',')[1],
                'def': row[0].split('*')[6].split(';')[2].split(',')[1]
            }}
            try: 
                dLine[row[0].split('*')[2]].update(mString) 
            except:
                dLine[row[0].split('*')[2]]=mString 
    try:
       dLine
    except:
        dLine=None
    return dLine

def HeroTalentAttribute(reader): #Talent stats
    #*8805*88*5*22,600;32,240;42,360;140,250*
    dLine={}
    for line in reader:
        row = line.split('\\n')
        if not row[0].startswith("#"): #All of these files start with a commented descriptor.
            try:
                mClassStat={}
                for stat in  row[0].split('*')[4].split(';'):
                    try:
                        mClassStat[mCombatAttr[int(stat.split(',')[0])]].update(stat.split(',')[1]) #There are a varying amount of values that can be here, so we are creating custom maps of each stat.
                    except:
                        mClassStat[mCombatAttr[int(stat.split(',')[0])]]=stat.split(',')[1] #Most should trigger the exception, and use this to build the stat.
                mString={
                    row[0].split('*')[3]: mClassStat}  #There are currently 30 talent levels or 40 for complete characters (Subject to change in future updates.)
                try:
                    dLine[row[0].split('*')[2]].update(mString) 
                except:
                    dLine[row[0].split('*')[2]]=mString
            except:
                pass
    try:
        dLine
    except:
        dLine=None
    return dLine

def Equip(reader): #Equippable gear
    #*1201*2*1*1*200311201*200321201*31,3;41,7;140,40;50,50*31,1000;41,1000;140,1000;50,1000*0*1201*
    dLine={}
    for line in reader:
        row = line.split('\\n')
        if not row[0].startswith("#"): #All of these files start with a commented descriptor.
            mClassStat={}
            for stat in  row[0].split('*')[7].split(';'):
                try:
                    mClassStat[mCombatAttr[int(stat.split(',')[0])]].update(stat.split(',')[1]) #There are a varying amount of values that can be here, so we are creating custom maps of each stat.
                except:
                    mClassStat[mCombatAttr[int(stat.split(',')[0])]]=stat.split(',')[1] #Most should trigger the exception, and use this to build the stat.
            mString={
                'quality': mQuality[int(row[0].split('*')[4])],
                'characteristic': mCharacteristic[int(row[0].split('*')[3])],
                'stats': mClassStat,
            }
            try: 
                dLine[row[0].split('*')[5]].update(mString) 
            except:
                dLine[row[0].split('*')[5]]=mString 
    try:
        dLine
    except:
        dLine=None
    return dLine

def CollectFrame(reader): #Hero Cards, the frame enhances a specific hero.
    #*3*3*40*21,800*10421503*16,1**21,80*40*5040*prop_collect_frame_3*3*0*
    #*4*4*40*21,1200;23,20*10421504*16,1**21,120;23,20*40*5040*prop_collect_frame_4*5*0*
    #*201*6*40*21,1800;23,80*10421678*16,1*CollectDetailLaser01,CollectDetailLaser02*21,180;23,80*40*5040*prop_collect_frame_5*9*0*
    dLine={}
    for line in reader:
        row = line.split('\\n')
        if not row[0].startswith("#"): #All of these files start with a commented descriptor.
            lStat={}
            for stat in row[0].split('*')[4].split(';'):
                if int(stat.split(',')[1]) == 23 or int(stat.split(',')[1]) == 33 or int(stat.split(',')[1]) == 43:
                    iStat=int(stat.split(',')[1]) / float(100)
                    iStat=str(iStat)+"%"
                else:
                    iStat=stat.split(',')[1]
                try: 
                    lStat[mCombatAttr[int(stat.split(',')[0])]].update(iStat) 
                except:
                    lStat[mCombatAttr[int(stat.split(',')[0])]] = iStat
            mString={
                mFrame[int(row[0].split('*')[2])]: lStat # [2] is the Card Frame
            }
            try: 
                dLine[row[0].split('*')[3]].update(mString) 
            except:
                dLine[row[0].split('*')[3]]=mString 
    try:
       dLine
    except:
        dLine=None
    return dLine

def CollectLevel(reader): #Hero Cards, level of the heroes
    #*3100*4*11*100*21,106567;31,14209;41,11829*548*21,10657;31,1421;41,1183*5011*
    #*17*1*40*17*31,1096;41,913*73*31,211;41,175*5040*
    dLine={}
    for line in reader:
        row = line.split('\\n')
        if not row[0].startswith("#"): #All of these files start with a commented descriptor.
            lStat={}
            for stat in row[0].split('*')[5].split(';'):
                if int(stat.split(',')[0]) == 23 or int(stat.split(',')[0]) == 33 or int(stat.split(',')[0]) == 43:
                    iStat=int(stat.split(',')[1]) / float(100)
                    iStat=str(iStat)+"%"
                else:
                    iStat=stat.split(',')[1]
                try: 
                    lStat[mCombatAttr[int(stat.split(',')[0])]].update(iStat) 
                except:
                    lStat[mCombatAttr[int(stat.split(',')[0])]] = iStat
            mString={ #The card group name
                'group': mGroup[int(row[0].split('*')[2])],
                row[0].split('*')[4]: lStat #The card level
                    
            }
            try: 
                dLine[row[0].split('*')[3]].update(mString) 
            except:
                dLine[row[0].split('*')[3]]=mString 
    try:
       dLine
    except:
        dLine=None
    return dLine

def CollectGroupAddition(reader): #Hero Cards, this id the final calculation when cards hit certain total levels.
    #*10*1*600*23,1305;33,1080;43,1215*prop,837,60*10421017*23,1305;33,1080;43,1215*4,2,3000;2,1,3000;5,2,1500*
    dLine={}
    for line in reader:
        row = line.split('\\n')
        if not row[0].startswith("#"): #All of these files start with a commented descriptor.
            lStat={}
            for stat in row[0].split('*')[4].split(';'):
                if int(stat.split(',')[0]) == 23 or int(stat.split(',')[0]) == 33 or int(stat.split(',')[0]) == 43:
                    iStat=int(stat.split(',')[1]) / float(100)
                    iStat=str(iStat)+"%"
                else:
                    iStat=stat.split(',')[1]
                try: 
                    lStat[mCombatAttr[int(stat.split(',')[0])]].update(iStat) 
                except:
                    lStat[mCombatAttr[int(stat.split(',')[0])]] = iStat
            mString={ 
                row[0].split('*')[3]: lStat #Total Level thresholds.
            }
            try: 
                dLine[mGroup[int(row[0].split('*')[2])]].update(mString) 
            except:
                dLine[mGroup[int(row[0].split('*')[2])]]=mString 
    try:
       dLine
    except:
        dLine=None
    return dLine

def mapSkills(dSkills,name):
    mSkill={}
    for key, vSkill in dSkills.items():
        skill_name=dMap[lang].get(vSkill['name'])
        try:
            if ',' not in vSkill['perct'] and ',' not in vSkill['val']:
                if vSkill['perct'] != '': #More often than not, we need to update the dynamic value for each skill level.
                    sDesc=((dMap[lang].get(vSkill['desc']))).format(vSkill['perct']).replace('\\n','')
                elif vSkill['val'] != '':
                    sDesc=((dMap[lang].get(vSkill['desc']))).format(vSkill['val']).replace('\\n','')
                else:
                    sDesc=(dMap[lang].get(vSkill['desc']))
            else:
                if vSkill['perct'] != '': #We need to update the dynamic value for each skill level and we don't know how many arguments are going to be in the string.
                    sDesc=((dMap[lang].get(vSkill['desc']))).format(*vSkill['perct'].split(',')).replace('\\n','')
                elif vSkill['val'] != '':
                    sDesc=((dMap[lang].get(vSkill['desc']))).format(*vSkill['val'].split(',')).replace('\\n','')
        except Exception as error:
            print(f"Failed to pull the skill description for {name}: {vSkill}")
            print(error)
            quit()
        sDesc=((re.sub('<material.*?>', '', sDesc).replace('<color=#',"<font color=#")).replace("</color>","</font>")).replace('</material>','')
        lSkill={
            "level": vSkill["level"],
            "desc": sDesc
        }
        try:
            mSkill[skill_name].append(lSkill)
        except:
            mSkill[skill_name]=[lSkill] #We want it to be a list of maps.
    return mSkill

def mapStats(dStats):
    mStat={}
    for key, vStat in dStats['Hero'].items():
        if vStat['hero'] != False: #Bots only have the Type and Role. Still not sure where to get those from though.
            try: #A small percentage of the heroes have their own cards.
                vCardGroup=dStats['CollectLevel'][vStat['heroid']]['group']
                vCardLevel=dStats['CollectLevel'][vStat['heroid']]
                vCardFrame=dStats['CollectFrame'][vStat['heroid']]
            except:
                vCardFrame=vCardLevel=vCardGroup=None
            try:
                limiter=dStats['HeroLimiter'][vStat['heroid']]
            except:
                limiter=None
            try:
                lStat={
                    'base': {
                        'HP': vStat['hp'],
                        'ATK': vStat['atk'],
                        'DEF': vStat['def'],
                        'type': vStat['type'],
                        'role': vStat['role'],
                        'characteristic': vStat['characteristic'],
                        'class': vStat['class'],
                    },
                    'machinecore': dStats['MechanicalPowerLevel'][vStat['heroid']],
                    'talent':dStats['HeroTalentAttribute'][vStat['heroid']],
                    'cards': {
                        'frame':vCardFrame,
                        'group':vCardGroup,
                        'level':vCardLevel
                    },
                    'essence':{
                        'class': dStats['HeroJobLevel'][vStat['class']]
                    },
                    'quality': dStats['HeroQualityProperty'][vStat['heroid']],
                    'grade': dStats['HeroGradeProperty'][vStat['heroid']], #This is not yet implemented as of August 2021, but I'm putting it in now before I forget how to read/write my script.
                    'limiter': limiter  
                }
            except:
                print(vStat)
        else:
            vType=None
            vRole=None
            vCharacteristic=None
            vClass=None
            vCardGroup=None
            lStat={
                'base': {
                    'HP': vStat['hp'],
                    'ATK': vStat['atk'],
                    'DEF': vStat['def'],
                },
                'level': dStats['DroidLevelGrowth'][vStat['heroid']],
                'quality': dStats['DroidStar'][vStat['heroid']]
            }
            pass
        name=dMap[lang].get(vStat['heronameid']) #Like in mapHero, we need to bind the stats to its respective hero.
        try:
            mStat[name].append(lStat)
        except:
            mStat[name]=[lStat] #We want it to be a list of maps.
    return mStat

def mapEquip(dEquip):
    lEquip={}
    for key, gear in dMap['Equip'].items():
        
        aEquip={
            'quality': gear['quality'],
            'characteristic': gear['characteristic'],
            'stats': gear['stats'],
        }
        try:
            lEquip[dMap[lang].get(key)].update(aEquip)
        except:
             lEquip[dMap[lang].get(key)]=aEquip
    return lEquip

def mapHero(dMap):
    mHero=[]
    for key, hero in dMap['Hero'].items(): #First Loop though the list of heroes as your primary list
        name=dMap[lang].get(hero['heronameid'])
        aHero={"hero": name,"details":{"skill":[],"talent":[],"limit":""}}
        if hero['hero'] is False: #Bots only have 2 skills and no talents.
            limit=2
        else: #Heroes that noramally start at elite quality have 4 skills and 1 talent.
            limit=4
        count=0
        skill=[]
        if name not in invalidHeroes and name is not None:
            while(count<limit): 
                try:
                    skill.append(mapSkills(dMap['HeroSkillDesc'].get(hero['skill'+str(count)]),name))
                except Exception as error:
                    print(error)
                    #I didn't bother having it scan any heroes without at least 4 abilities as they are not worth anything past stage 25 and are useless in tournaments.
                    print("Failed while scanning for "+ name + " skills")
                    break
                count +=1
            try:
                aHero["details"]['skill'].append(skill)
            except:
                aHero["details"]['skill']=skill
            #Now we need the talent tiers and limit breaks if they have one. Though balance type heroes can go to tier 40, they also only have 4 levels of effects.
            #I suspect that they might change that in the future, so I programmed this to count the possible talents for each hero.
            if hero['hero'] is True:
                talent=[]
            #Trying to get the list of Talents    
                try:
                    talent.append(mapSkills(dMap['HeroSkillDesc'].get(hero['talent']),name))
                except Exception as error:
                    print(error)
                    #I didn't bother having it scan any heroes without at least 4 abilities as they are not worth anything past stage 25 and are useless in tournaments.
                    print("Failed while scanning for "+ name + " talent")
                    break
                try:
                    aHero["details"]['talent'].update(talent)
                except:
                    aHero["details"]['talent']=talent
            #Now trying to get limit breakthrough
                try:
                    dLimit=dMap['HeroLimiter'].get(hero['heroid'])
                    limitDesc=dMap[lang].get(dLimit['desc']).replace('\\n','')
                    if limitDesc is None:
                        dLimit=None
                except:
                    dLimit=None
                if dLimit is not None: #This part of the code sucks and it really should automatically find the number of values for the limiter, but it's not formatting my strings correctly
                    for key, val in enumerate(dLimit['descval'].split(',')):
                        limitDesc=limitDesc.replace("{"+str(key)+"}", val)
                    aHero["details"]['limit']=(limitDesc)
        try:
            mHero.append(aHero)
        except:
            mHero=aHero
    return (mHero)

adb_pull_files()
dMap=genMappings()
print("Success! Getting the list of heroes")
mHero=mapHero(dMap)
print("Success! Now retrieving the hero stats")
mStats=mapStats(dMap) #Currently I feel that using separate json files for the data would be more practical than trying to shove all the data into one file.
print("One more to go! Getting the list of equippable gear")
mEquip=mapEquip(dMap)

with open(data_path+'herolist.json', 'w') as f:
    json.dump(mHero,f)
with open(data_path+'herostats.json', 'w') as f:
    json.dump(mStats,f)
with open(data_path+'heroequip.json', 'w') as f:
    json.dump(mEquip,f)


#I need somewhere to put the total class levels 
#'level':[
#    dStats['HeroAcademyLevel'][vStat['heroid']]
#]