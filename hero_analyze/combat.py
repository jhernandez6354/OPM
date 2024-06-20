#The purpose of this script is to analyze the current hero lineup
#    and determine hero win-rates.
import json
from helper_abilities import clean_abilities
from helper_defs import *
#list lineup=[hero1,hero2,hero3,hero4,hero5]
#list l_compare=[hero1,hero2,hero3,hero4,hero5] or [boss] #Test your lineup against a single boss or against another 5 man team.
#boolean b_max="True/False" If true, heroes will use all max stats. If not, they will have the following:
    # Mythic 5*
    # Limiter 10
    # Talent 30
    # No Machine Core
    # No blessing
    # Gear refinement Lvl. 1

    #The following is default when analyzing heroes:
    # Hero Level is 151
    # No Potential Chips - Because they can be moved around
    # No Cards - Maybe later
    # No Essence Laboratory - Because it is global
    # No Gear Polish (maybe for a different analyze later on.)

'''
    parser=argparse.ArgumentParser()
    parser.add_argument("--bar", help="Do the bar option")
    parser.add_argument("--max                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           ", help="If true, heroes will use all max stats.")

    args=parser.parse_args()

    print(f"Args: {args}\nCommand Line: {sys.argv}\nfoo: {args.foo}")
    print(f"Dict format: {vars(args)}")
'''

class analyze(object):
    def __init__(self,b_max=False,abilities_file=False):
        self.b_max=b_max
        with open('analyze/lineup.json') as analyze_file:
            analyze=json.load(analyze_file)
            lineup=analyze['lineup']
            compare=analyze['compare']
        with open('analyze/herostats.json') as stats_file:
            self.stats=json.load(stats_file)
        with open('analyze/herolist.json') as hero_file:
            self.hero=json.load(hero_file)
        with open('analyze/initialize.json') as initial_file:
            self.initialize=json.load(initial_file)
        with open('analyze/test.json') as ability_file:
            self.abilities=json.load(ability_file)
        if abilities_file is not False:
            print('Please wait while I compile hero talents.')
            clean_abilities(self.hero,abilities_file) #Creates a clean file with all hero abilities that will be used for sims.
            print("File has been updated.")
        self.get_hero_stats(lineup,compare)
        self.start_combat(lineup,compare)
        #d_placement=self.set_hero_position(lineup,l_compare)

    def set_hero_position(self,lineup,compare):
        d_placement={}
        position=0
        #Positions are a 3x3 matrix
        for position in lineup:
            position+=1
        return d_placement
    
    def set_compare(self):
        pass

    def analyze_rank(self):
        pass

    def get_max_stat(self,stat):
        try:
            max_stat=stat[str(len(stat))]
        except Exception:
            max_stat=stat[str(len(stat)-1)] #Some start at zero instead of 1
        return max_stat
    
    def get_stats(self,stats,hero):
        return_stat={}
        stat_squish=[]
        d_stats=self.parse_stat_values(stats,hero)
        for key, stat in d_stats.items():
            if stat is not None:
                for name, value in stat.items():
                    if name not in stat_squish:
                        stat_squish.append(name.lower().replace(' ','_'))
                    if str(value).endswith("%"):
                        value=float(value.split('%')[0])/100
                    if hasattr(self,name.lower().replace(' ','_')):
                        setattr(self,name,int(getattr(self,name.lower().replace(' ','_')))+int(value))
                    else:
                        setattr(self,name.lower().replace(' ','_'),int(value))
                    value=None
        for key in stat_squish:
            if key != 'perct':
                return_stat[key]=getattr(self,key)
        return return_stat
    
    def parse_stat_values(self,stats,hero):
        if self.b_max==False:
            talent_stat=stats['talent']["30"]
            limiter=stats['limiter']["10"]
            mega_limiter=None
            blessing=None
            machinecore=None
        else:
            machinecore=self.get_max_stat(stats["machinecore"])
            talent_stat=self.get_max_stat(stats["talent"])
            limiter=stats["limiter"]["10"]
            mega_limiter=stats["mega_limiter"]["35"]
            blessing=stats["blessing"]
        quality=stats["quality"]['Mythical*****']
        grade=self.get_max_stat(stats["grade"])
        #Dont forget that the hero type combos also affect overall stats.
        return {
            "machinecore": machinecore,
            "talent_stat":talent_stat,
            "quality":quality,
            "grade": grade,
            "limiter": limiter,
            "mega_limiter": mega_limiter,
            "blessing": blessing
        }

    def get_hero_stats(self,lineup,compare):
        lineup_dict=dict()
        compare_dict=dict()
        self.return_compare=dict()
        self.return_lineup=dict()
        for hero in self.hero:
            if hero['hero'] in lineup:
                lineup_dict[hero['hero']]=hero['details']
            elif hero['hero'] in compare:
                compare_dict[hero['hero']]=hero['details']
        for key, value in self.stats.items():
            if key in lineup:
                self.return_lineup[key]=self.get_stats(value[0],lineup_dict[key])
            elif key in compare:
                self.return_compare[key]=self.get_stats(value[0],compare_dict[key])

    def class_bonus(self, class_input):
        h_class={"old world":0,'complete':0,"tech":0,"weapon":0,"psychic":0,"physical":0,"boss":0}
        h_class[class_input["type"].lower()]+=1
        if h_class['old world'] >= 1: #This has its own category
            ow_bonus=self.initialize["ow_bonus"][str(h_class['old world'])]
        else:
            ow_bonus=None
        sum_wildcard=int(h_class['complete']) + int(h_class['old world'])
        if sum_wildcard >= 4: #Complete and OW counts as a wildcard for the four main types, so if you have at least four, you have the best bonus.
            main_bonus=self.initialize["char_bonus"]["5"]
            bonus=5
        else:
            bonus=int(h_class['tech']) + sum_wildcard
            if h_class['psychic'] >= 2:
                if bonus < 5 and int(h_class['psychic']) + sum_wildcard > bonus:
                    bonus=int(h_class['psychic']) + sum_wildcard
            elif h_class['physical'] >= 2:
                if bonus < 5 and int(h_class['physical']) + sum_wildcard > bonus:
                    bonus=int(h_class['physical']) + sum_wildcard
            elif h_class['weapon'] >= 2:
                if bonus < 5 and int(h_class['weapon']) + sum_wildcard > bonus:
                    bonus=int(h_class['weapon']) + sum_wildcard
            if bonus == 3 and sum_wildcard == 1: #This is the only circumstance a wildcard can make the 3/2 bonus.
                for key, value in h_class.items():
                    if value == 2:
                        main_bonus=self.initialize["char_bonus"]["32"]
                try:
                    main_bonus
                except:
                    main_bonus=self.initialize["char_bonus"]["3"]
            try:
                bonus
            except: 
                bonus=sum_wildcard #That means no typed characters are set and they are using less than 5 complete/ow characters.
                    
            if bonus >= 3 and sum_wildcard == 1 and bonus < 5:
                for key, value in h_class.items():
                    if value == 2: 
                        main_bonus=self.initialize["char_bonus"]["32"]
            if bonus <= 2:
                main_bonus=None
            else:
                main_bonus=self.initialize["char_bonus"][str(bonus)]

            if ow_bonus is not None and main_bonus is not None:
                type_bonus = ow_bonus | main_bonus
            elif ow_bonus is not None and main_bonus is None:
                type_bonus= ow_bonus
            else:
                type_bonus = main_bonus
            return type_bonus
    
    def talents(self, talents):
        for value in talents:
            print(value)

    def skills(self, skills):
        for value in skills:
            print(value)

    def start_combat(self,lineup,compare):
        #Initialize combat stacks and stats, character positions, same character boosts, rage levels, and turn order.
        rage=50
        lineup_hero=dict()
        compare_hero=dict()
        lineup_status=dict()
        compare_status=dict()
        for hero, ability in self.abilities.items():
            if hero in lineup:
                lineup_hero[hero]={"ability":ability,"setup":lineup[hero]}
                lineup_bonus=self.class_bonus(ability)
                #Many talents affects skills, which is why skills need to be assigned to self and run first.
                self.talents(ability['skills'])
                if 
                self.skills(ability['talent'])
                self.skills(ability['limit'])
                self.skills(ability['mega_limit'])
            elif hero in compare:
                compare_hero[hero]={"ability":ability,"setup":compare[hero]}
                compare_bonus=self.class_bonus(ability)
                self.talents(ability['skills'])
                if ability['type'].lower() != 'boss': 
                    self.skills(ability['talent'])
                    self.skills(ability['limit'])
                    self.skills(ability['mega_limit'])
        
        #return json.dumps({"lineup":lineup_bonus,"compare":compare_bonus})


    def combat_log():
        pass

analyze(b_max=True,abilities_file=False)