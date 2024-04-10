#The purpose of this script is to analyze the current hero lineup
#    and determine hero win-rates.
import json
from helper_abilities import clean_abilities
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
        if abilities_file is not False:
            print('Please wait while I compile hero talents.')
            clean_abilities(self.hero,abilities_file) #Creates a clean file with all hero abilities that will be used for sims.
            print("File has been updated.")
        self.get_hero_stats(lineup,compare)
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
        lineup_dict=compare_dict={}
        for hero in self.hero:
            if hero['hero'] in lineup:
                lineup_dict[hero['hero']]=hero['details']
            elif hero['hero'] in compare:
                compare_dict[hero['hero']]=hero['details']
        for key, value in self.stats.items():
            if key in lineup:
                #print("Lineup entry: "+key)
                #print(self.get_stats(value[0],lineup_dict[key]))
                pass
            elif key in compare:
                #print("Compare entry: "+key)
                #print(self.get_stats(value[0],compare_dict[key]))
                pass

    def model_power(self):
        pass
    
    def model_abilities(self):
        pass

analyze(b_max=True,abilities_file='analyze/abilities.json')