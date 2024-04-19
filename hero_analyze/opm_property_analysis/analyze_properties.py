# This script is used to generate card attributes

import pandas as pd
import os
# from personal_tools import opm_tools as tools
from openpyxl import load_workbook

path = ''


# Add dataframe to excel without overwriting
def _excel_add_sheet(_df, _writer, sht_name):
    book = load_workbook(_writer.path)
    _writer.book = book
    _df.to_excel(excel_writer=_writer, sheet_name=sht_name, index=None)
    _writer.close()


def compare_version(v1, v2):
    if len(v1.split(".")) < 3:
        return v2
    if len(v2.split(".")) < 3:
        return v1

    a, b, c = v1.split('.')
    A, B, C = v2.split('.')
    x = int(a) * 10000 + int(b) * 100 + int(c)
    y = int(A) * 10000 + int(B) * 100 + int(C)
    if x >= y:
        return v1
    else:
        return v2


def set_version_path():
    # _p = "/Users/oas/Documents/work/github/opm_specs\\hero_analyze\\specs\\"
    _p = os.path.abspath('..') + "\\hero_analyze\\specs\\"
    folders = os.listdir(_p)
    current_version = folders[0]
    for folder in folders:
        current_version = compare_version(current_version, folder)

    global path
    path = _p + current_version + '\\xlsx_origin\\'


def get_hero_grade_by_level(_level):
    if _level <= 10:
        return 1
    else:
        return min(19, int((_level - 1) / 20) + 2)


def get_hero_equips(_role, _quality):
    return [_role * 1000 + 100 + _quality,
            _role * 1000 + 200 + _quality,
            _role * 1000 + 300 + _quality,
            _role * 1000 + 400 + _quality]


def union_dict(dict_base, dict2, rate=1.0):
    for key in dict2.keys():
        dict_base[key] += dict2[key] * rate
    return dict_base


def print_attribute(attr_dict, _head):
    dict_names = {21: 'hp',
                  22: 'hp bonus',
                  31: 'atk',
                  32: 'atk bonus',
                  41: 'def',
                  42: 'def bonus',
                  50: 'damage reduction',
                  60: 'Critical hit reduction',
                  70: 'critical hit',
                  140: 'block',
                  150: 'accuracy'}
    desc = _head
    for key in attr_dict.keys():
        desc += dict_names[key] + ',' + str(attr_dict[key]) + ';'
    print(desc)


def read_spec_file(file_name):
    _df = pd.read_excel(path + file_name + '.xlsx', header=2, sheet_name=file_name)  # Read the data with the 3rd line header
    _df.dropna(axis=0, how='all')  # Delete empty lines
    _df = _df.drop([0])  # Remove Chinese label
    return _df.reset_index()  # Return after resetting the index number

def get_dict_from_str(_str):
    _str = str(_str)
    if _str == 'nan' or _str == '':
        return pd.Series({'AttributeInfo': None})
    _str = _str.replace(',', ':')
    _str = _str.replace(';', ',')
    _str = '{' + _str + '}'
    _dict = eval(_str)
    return pd.Series({'AttributeInfo': _dict})


def get_specific_property(_df, target_name, column_name1, value1, column_name2='', value2=None):
    if column_name2 == '':
        n = _df[_df[column_name1] == value1].index.values.astype(int)[0]
    else:
        n = _df[(_df[column_name1] == value1) & (_df[column_name2] == value2)].index.values.astype(int)[0]
    return _df.loc[n, target_name]


def get_power(hero_hp, hero_atk, hero_def, hero_crit, hero_crit_res, hero_precise, hero_parry, hero_dmg_res):
    return hero_hp * power_hp + hero_atk * power_atk + hero_def * power_def + hero_crit * power_crit + \
           hero_crit_res * power_crit_res + hero_precise * power_precise + hero_parry * power_parry + \
           hero_dmg_res * power_dmg_res


def calculate_properties(hp_base, atk_base, def_base, crit_base, property_dict, _hp_m=-1, _atk_m=-1, _def_m=-1,
                         _init=False):
    # 计算最终属性
    if _init:
        hero_hp = hp_base
        hero_atk = atk_base
        hero_def = def_base
        hero_crit = crit_base
        hero_crit_res = 0
        hero_precise = 0
        hero_parry = 0
        hero_dmg_res = 0
    else:
        hero_hp = hp_base * (property_dict[22]) / 10000 + property_dict[21]
        hero_atk = atk_base * (property_dict[32]) / 10000 + property_dict[31]
        hero_def = def_base * (property_dict[42]) / 10000 + property_dict[41]
        hero_crit = property_dict[70]
        hero_crit_res = property_dict[60]
        hero_precise = property_dict[150]
        hero_parry = property_dict[140]
        hero_dmg_res = property_dict[50]

    # 计算战斗力
    power = get_power(hero_hp, hero_atk, hero_def, hero_crit, hero_crit_res, hero_precise, hero_parry, hero_dmg_res)
    hero_dict = {
        'hp': hero_hp,
        'atk': hero_atk,
        'def': hero_def,
        'crit': hero_crit,
        'crit_res': hero_crit_res,
        'precise': hero_precise,
        'parry': hero_parry,
        'dmg_res': hero_dmg_res,
        'power': power,
    }
    return hero_dict


def get_hero_base_property(_id, _quality, _level, _lv_enhance):
    print('\tProcessing role：%d' % _id)
    # 角色初始属性
    hp_init = get_specific_property(df_hero, 'HpBase', 'Id', _id)
    atk_init = get_specific_property(df_hero, 'AtkBase', 'Id', _id)
    def_init = get_specific_property(df_hero, 'DefBase', 'Id', _id)
    crit_init = get_specific_property(df_hero, 'CritBase', 'Id', _id)
    if test_mode:
        print('Initial attributes: health = %f, attack = %f, defense = %f, critical hit = %f' % (hp_init, atk_init, def_init, crit_init))
    # 角色品质属性
    hp_qua_per = get_specific_property(df_hero_quality_growth, 'HpParam', 'HeroId', _id, 'QualityLevel', _quality)
    atk_qua_per = get_specific_property(df_hero_quality_growth, 'AtkParam', 'HeroId', _id, 'QualityLevel', _quality)
    def_qua_per = get_specific_property(df_hero_quality_growth, 'DefParam', 'HeroId', _id, 'QualityLevel', _quality)
    if test_mode:
        print('Quality growth: life bonus = %f, attack bonus = %f, defense bonus = %f' % (hp_qua_per, atk_qua_per, def_qua_per))
    hp_qua_inc = get_specific_property(df_hero_quality_growth, 'HpInc', 'HeroId', _id, 'QualityLevel', _quality)
    atk_qua_inc = get_specific_property(df_hero_quality_growth, 'AtkInc', 'HeroId', _id, 'QualityLevel', _quality)
    def_qua_inc = get_specific_property(df_hero_quality_growth, 'DefInc', 'HeroId', _id, 'QualityLevel', _quality)
    if test_mode:
        print('Quality growth: life = %f, attack = %f, defense = %f' % (hp_qua_inc, atk_qua_inc, def_qua_inc))
    # 角色等级成长
    hp_lv_inc = get_specific_property(df_hero_lv_growth, 'HpInc', 'Level', _level, 'EnhancePeriod', _lv_enhance)
    atk_lv_inc = get_specific_property(df_hero_lv_growth, 'AtkInc', 'Level', _level, 'EnhancePeriod', _lv_enhance)
    def_lv_inc = get_specific_property(df_hero_lv_growth, 'DefInc', 'Level', _level, 'EnhancePeriod', _lv_enhance)
    if test_mode:
        print('Level growth: health = %f, attack = %f, defense = %f' % (hp_lv_inc, atk_lv_inc, def_lv_inc))
    # Character level attributes
    _grade = get_hero_grade_by_level(_level)
    hp_grade_inc = get_specific_property(df_hero_grade_growth, 'HpInc', 'HeroId', _id, 'GradeLevel', _grade)
    atk_grade_inc = get_specific_property(df_hero_grade_growth, 'AtkInc', 'HeroId', _id, 'GradeLevel', _grade)
    def_grade_inc = get_specific_property(df_hero_grade_growth, 'DefInc', 'HeroId', _id, 'GradeLevel', _grade)
    if test_mode:
        print('Level growth: life = %f, attack = %f, defense = %f' % (hp_grade_inc, atk_grade_inc, def_grade_inc))
    # Calculate character basic attributes
    hp_base = hp_init + hp_lv_inc * hp_qua_per / 10000 + hp_qua_inc + hp_grade_inc
    atk_base = atk_init + atk_lv_inc * atk_qua_per / 10000 + atk_qua_inc + atk_grade_inc
    def_base = def_init + def_lv_inc * def_qua_per / 10000 + def_qua_inc + def_grade_inc
    crit_base = crit_init

    return hp_base, atk_base, def_base, crit_base


def get_hero_property(_id, _quality, _level, _lv_enhance, _e_qua, _e_enhance, _talent, _core, _job, _limiter=0):
    print('Processing role：%d' % _id)
    # Calculate character basic attributes
    hp_base, atk_base, def_base, crit_base = get_hero_base_property(_id, _quality, _level, _lv_enhance)
    if test_mode:
        print('Basic attributes: health = %f, attack = %f, defense = %f, critical hit = %f' % (hp_base, atk_base, def_base, crit_base))

    property_dict = {21: 0, 22: 0, 31: 0, 32: 0, 41: 0, 42: 0, 50: 0, 60: 0, 70: 0, 140: 0, 150: 0}
    hero_dict = calculate_properties(hp_base, atk_base, def_base, crit_base, property_dict, _init=True)

    # Character equipment attributes
    if _e_qua > 0:
        property_dict = {21: 0, 22: 0, 31: 0, 32: 0, 41: 0, 42: 0, 50: 0, 60: 0, 70: 0, 140: 0, 150: 0}
        _role = get_specific_property(df_hero, 'Role', 'Id', _id)
        equip_list = get_hero_equips(_role, _e_qua)
        for equip in equip_list:
            equip_attr = get_specific_property(df_equip_property, 'AttributeInfo', 'Id', equip)
            if test_mode:
                print_attribute(equip_attr, 'Equipment attributes: ')

            # Default rule: If there is enhancement, the equipment will have type bonus by default, otherwise there will be no bonus.
            if _e_enhance > 0:
                property_dict = union_dict(property_dict, equip_attr, 1.3 + _e_enhance / 10)
            else:
                property_dict = union_dict(property_dict, equip_attr, 1)
        hero_dict = union_dict(hero_dict, calculate_properties(hp_base, atk_base, def_base, crit_base, property_dict))

    # 角色Talent attributes
    if _talent >= 0:
        property_dict = {21: 0, 22: 0, 31: 0, 32: 0, 41: 0, 42: 0, 50: 0, 60: 0, 70: 0, 140: 0, 150: 0}
        talent_attr = get_specific_property(df_hero_talent_growth, 'AttributeInfo', 'HeroId', _id, 'TalentLevel',
                                            _talent)
        if test_mode:
            print_attribute(talent_attr, 'Talent attributes: ')
        property_dict = union_dict(property_dict, talent_attr)
        hero_dict = union_dict(hero_dict, calculate_properties(hp_base, atk_base, def_base, crit_base, property_dict))

    # Institute attributes
    if _core > 0:
        property_dict = {21: 0, 22: 0, 31: 0, 32: 0, 41: 0, 42: 0, 50: 0, 60: 0, 70: 0, 140: 0, 150: 0}
        core_attr = get_specific_property(df_core_property, 'AttributeInfo', 'Id', _core)
        if test_mode:
            print_attribute(core_attr, 'core attributes: ')
        property_dict = union_dict(property_dict, core_attr)
        hero_dict = union_dict(hero_dict, calculate_properties(hp_base, atk_base, def_base, crit_base, property_dict))

    # Class attributes
    if _job > 0:
        property_dict = {21: 0, 22: 0, 31: 0, 32: 0, 41: 0, 42: 0, 50: 0, 60: 0, 70: 0, 140: 0, 150: 0}
        job = get_specific_property(df_hero, 'Job', 'Id', _id)
        job_attr = get_specific_property(df_job_property, 'AttributeInfo', 'Level', _job, 'Job', job)
        if test_mode:
            print_attribute(job_attr, 'Class attributes: ')
        property_dict = union_dict(property_dict, job_attr)
        hero_dict = union_dict(hero_dict, calculate_properties(hp_base, atk_base, def_base, crit_base, property_dict))

    # Limiter Breakthrough-Self Properties
    if _limiter > 0:
        property_dict = {21: 0, 22: 0, 31: 0, 32: 0, 41: 0, 42: 0, 50: 0, 60: 0, 70: 0, 140: 0, 150: 0}
        limiter_attr = get_specific_property(df_limiter, 'AttributeInfo', 'LimiterLevel', _limiter, 'Heroid', _id)
        if test_mode:
            print_attribute(limiter_attr, 'Limiter properties: ')
        property_dict = union_dict(property_dict, limiter_attr)
        if test_mode:
            print(property_dict)
        hp_max = get_specific_property(df_hero_quality_growth, 'AttributeInfo', 'HeroId', _id, 'QualityLevel', _quality)[21]
        atk_max = get_specific_property(df_hero_quality_growth, 'AttributeInfo', 'HeroId', _id, 'QualityLevel', _quality)[31]
        def_max = get_specific_property(df_hero_quality_growth, 'AttributeInfo', 'HeroId', _id, 'QualityLevel', _quality)[41]
        hero_dict = union_dict(hero_dict,
                               calculate_properties(hp_base, atk_base, def_base, crit_base, property_dict, hp_max,
                                                    atk_max, def_max))
    # if not test_mode:
    #     tools.process_bar(_id / 98, start_str='正在进行计算：')

    # Output final properties
    return hero_dict


def get_hero_equip_property(_id, _quality, _level, _lv_enhance, _e_qua, _e_enhance):
    print('\tProcessing role：%d' % _id)
    # Character equipment attributes
    property_dict = {21: 0, 22: 0, 31: 0, 32: 0, 41: 0, 42: 0, 50: 0, 60: 0, 70: 0, 140: 0, 150: 0}
    if _e_qua > 0:
        _role = get_specific_property(df_hero, 'Role', 'Id', _id)
        equip_list = get_hero_equips(_role, _e_qua)
        for equip in equip_list:
            equip_attr = get_specific_property(df_equip_property, 'AttributeInfo', 'Id', equip)

            # Default rule: If there is enhancement, the equipment will have type bonus by default, otherwise there will be no bonus.
            if _e_enhance > 0:
                property_dict = union_dict(property_dict, equip_attr, 1.3 + _e_enhance / 10)
            else:
                property_dict = union_dict(property_dict, equip_attr, 1)
    return calculate_properties(0, 0, 0, 0, property_dict)


def get_hero_talent_property(_id, _quality, _level, _lv_enhance, _talent):
    print('\tProcessing role：%d' % _id)
    hp_base, atk_base, def_base, crit_base = get_hero_base_property(_id, _quality, _level, _lv_enhance)
    property_dict = {21: 0, 22: 0, 31: 0, 32: 0, 41: 0, 42: 0, 50: 0, 60: 0, 70: 0, 140: 0, 150: 0}
    if _talent >= 0:
        talent_attr = get_specific_property(df_hero_talent_growth, 'AttributeInfo', 'HeroId', _id, 'TalentLevel',
                                            _talent)
        property_dict = union_dict(property_dict, talent_attr)
    return calculate_properties(hp_base, atk_base, def_base, crit_base, property_dict)


def get_hero_core_property(_id, _quality, _level, _lv_enhance, _core):
    print('\tProcessing role：%d' % _id)
    property_dict = {21: 0, 22: 0, 31: 0, 32: 0, 41: 0, 42: 0, 50: 0, 60: 0, 70: 0, 140: 0, 150: 0}
    if _core > 0:
        core_attr = get_specific_property(df_core_property, 'AttributeInfo', 'Id', _core)
        property_dict = union_dict(property_dict, core_attr)
    return calculate_properties(0, 0, 0, 0, property_dict)


def get_hero_job_property(_id, _quality, _level, _lv_enhance, _job):
    print('\tProcessing role：%d' % _id)
    property_dict = {21: 0, 22: 0, 31: 0, 32: 0, 41: 0, 42: 0, 50: 0, 60: 0, 70: 0, 140: 0, 150: 0}
    if _job > 0:
        job = get_specific_property(df_hero, 'Job', 'Id', _id)
        job_attr = get_specific_property(df_job_property, 'AttributeInfo', 'Level', _job, 'Job', job)
        property_dict = union_dict(property_dict, job_attr)
    return calculate_properties(0, 0, 0, 0, property_dict)


def get_hero_limiter_property(_id, _quality, _level, _lv_enhance, _limiter):
    print('\tProcessing role：%d' % _id)
    hp_base, atk_base, def_base, crit_base = get_hero_base_property(_id, _quality, _level, _lv_enhance)
    property_dict = {21: 0, 22: 0, 31: 0, 32: 0, 41: 0, 42: 0, 50: 0, 60: 0, 70: 0, 140: 0, 150: 0}
    if _limiter > 0:
        limiter_attr = get_specific_property(df_limiter, 'AttributeInfo', 'LimiterLevel', _limiter, 'Heroid', _id)
        property_dict = union_dict(property_dict, limiter_attr)
    hp_max = get_specific_property(df_hero_quality_growth, '21', 'HeroId', _id, 'QualityLevel', _quality)
    atk_max = get_specific_property(df_hero_quality_growth, '31', 'HeroId', _id, 'QualityLevel', _quality)
    def_max = get_specific_property(df_hero_quality_growth, '41', 'HeroId', _id, 'QualityLevel', _quality)
    return calculate_properties(hp_base, atk_base, def_base, crit_base, property_dict, 1, hp_max, atk_max, def_max)


def save_output_auto(_df, is_total=False, _name=''):
    print('Saving data...')
    _list_attr = _df['attribute'].values.tolist()
    _df1 = pd.DataFrame(_list_attr)
    _df = pd.concat([_df, _df1], axis=1)
    _df = _df.drop(['attribute'], axis=1)
    if is_total:
        _df['team_power'] = _df['power'] * 5
    excel_writer = pd.ExcelWriter('output_split.xlsx', engine='openpyxl')
    # pd.DataFrame().to_excel('output_auto.xlsx')
    _excel_add_sheet(_df, excel_writer, _name)
    # df.to_excel('output_auto.xlsx', sheet_name='total', index=False)
    print('Data saved...')


set_version_path()
os.system('clear')
print(
    '*' * 50 + '\n' + '*' * 50 + '\n' + 'Welcome to One Punch Man Data Analyzing Center!\n' + '*' * 50 + '\n' + '*' * 50 + '\n')
print('Initializing Data...')

# 1. Read hero basic information
df_hero = read_spec_file('Hero')
df_hero = df_hero.loc[:, df_hero.columns.intersection(
    ['Id', 'Rarity', 'Type', 'Role', 'HpBase', 'AtkBase', 'DefBase', 'CritBase', 'Job'])]
df_hero = df_hero.drop(df_hero[df_hero['Id'] > 1000].index)

# 2. 读取等级成长信息
df_hero_lv_growth = read_spec_file('HeroLevelGrowth')

# 3. 读取等级突破成长信息
df_hero_grade_growth = read_spec_file('HeroGradeProperty')

# 4. 读取品质成长信息
df_hero_quality_growth = read_spec_file('HeroQualityProperty')
df_hero_quality_growth = df_hero_quality_growth.join(
    df_hero_quality_growth['LimiterPropertyMax'].apply(get_dict_from_str))

# 5. 读取天赋成长信息
df_hero_talent_growth = read_spec_file('HeroTalentAttribute')
df_hero_talent_growth = df_hero_talent_growth.drop([0])
df_hero_talent_growth = df_hero_talent_growth.join(df_hero_talent_growth['Attribute'].apply(get_dict_from_str))
df_hero_talent_growth = df_hero_talent_growth.drop(['Attribute'], axis=1)

# 6. 读取装备信息
df_equip_property = read_spec_file('Equip')
df_equip_property = df_equip_property.join(df_equip_property['Attribute'].apply(get_dict_from_str))
df_equip_property = df_equip_property.loc[:, df_equip_property.columns.intersection(['Id', 'AttributeInfo'])]

# 7. 读取核心研究所信息
df_core_property = read_spec_file('HeroAcademyLevel')
df_core_property = df_core_property.join(df_core_property['Attribute'].apply(get_dict_from_str))
df_core_property = df_core_property.loc[:, df_core_property.columns.intersection(['Id', 'Level', 'AttributeInfo'])]

# 7. 读取职阶信息
df_job_property = read_spec_file('HeroJobLevel')
df_job_property = df_job_property.join(df_job_property['Attribute'].apply(get_dict_from_str))
df_job_property = df_job_property.loc[:, df_job_property.columns.intersection(['Id', 'Job', 'Level', 'AttributeInfo'])]

# 8. Read combat power parameters
df_configs = read_spec_file('Configs')
power_hp = get_specific_property(df_configs, 'value', 'key', 'PowerParamHp')
power_atk = get_specific_property(df_configs, 'value', 'key', 'PowerParamAtk')
power_def = get_specific_property(df_configs, 'value', 'key', 'PowerParamDef')
power_crit = get_specific_property(df_configs, 'value', 'key', 'PowerParamCrit')
power_crit_res = get_specific_property(df_configs, 'value', 'key', 'PowerParamCritRes')
power_parry = get_specific_property(df_configs, 'value', 'key', 'PowerParamParry')
power_precise = get_specific_property(df_configs, 'value', 'key', 'PowerParamPrecise')
power_dmg_res = get_specific_property(df_configs, 'value', 'key', 'PowerParamDmgRes')

# 9. Read hero breakthrough information
df_limiter = read_spec_file('HeroLimiter')
df_limiter = df_limiter.join(df_limiter['Property'].apply(get_dict_from_str))
df_limiter = df_limiter.loc[:, df_limiter.columns.intersection(['Id', 'Heroid', 'LimiterLevel', 'AttributeInfo'])]

test_mode = True
while True:
    print('\n' + '*' * 100)
    cmd = input('\nInput Hero Information:\n 0: quit\n 1: use data.xlsx，Use data data to generate bot data for running AI\n 2: use data_auto.xlsx '
                'Generate data in large batches and calculate combat power, which is used for combat power intervals in places such as the Road to the Strong\n 3: use data_400.xlsx, use data_400 data, 400-level basic attributes\n else: ( _id, '
                '_quality, _level, _lv_enhance, _e_qua, _e_enhance, _talent, _core, _job)\n')

    # quit
    if cmd == '0':
        print('Thanks for using OPM DATA CENTER, goodbye！\n')
        exit()

    # Read data.xlsx table information, calculate attributes and output to output.xlsx
    elif cmd == '1':
        test_mode = False
        df = pd.read_excel(os.getcwd()+'\\opm_property_analysis\\data.xlsx', header=0, sheet_name='Sheet1')  # Read data with row 1 header
        df.dropna(axis=0, how='all')  # Delete empty lines
        df['attribute'] = df.apply(
            lambda col: get_hero_property(col['_id'], col['_quality'], col['_level'], col['_lv_enhance'], col['_e_qua'],
                                          col['_e_enhance'], col['_talent'], col['_core'], col['_job'], col['_limiter']), axis=1)
        list_attr = df['attribute'].values.tolist()
        df1 = pd.DataFrame(list_attr)
        df = pd.concat([df, df1], axis=1)
        # 迎合bot表格式
        df.insert(2, '_type', 2)
        df.insert(6, '_e_list', '')
        df.insert(19, '_crit_bonus', 15000)
        df['_fury'] = 0
        df['_show_level'] = df['_level']
        df['_chase'] = 5000
        # print(df['power'])
        df = df.drop(['attribute', '_e_qua', '_e_enhance', '_core', '_job', 'power'], axis=1)
        df.to_excel('output.xlsx', index=False)
        print('计算完毕，结果已输出到output.xlsx文件中！\n')
    # 读取data_auto.xlsx表信息，计算属性并输出到output_auto.xlsx

    elif cmd == '2':
        test_mode = False
        df = pd.read_excel('data_auto.xlsx', header=0, sheet_name='Sheet1')  # Read data with row 1 header
        df.dropna(axis=0, how='all')  # Delete empty lines
        df['attribute'] = df.apply(
            lambda col: get_hero_property(col['_id'], col['_quality'], col['_level'], col['_lv_enhance'], col['_e_qua'],
                                          col['_e_enhance'], col['_talent'], col['_core'], col['_job'], ), axis=1)
        # save_output_auto(df, True, 'total')
        # list_attr = df['attribute'].values.tolist()
        # df1 = pd.DataFrame(list_attr)
        # df = pd.concat([df, df1], axis=1)
        # df = df.drop(['attribute'], axis=1)
        # df['team_power'] = df['power'] * 5
        df.to_excel('output_auto.xlsx', sheet_name='total', index=False)
        # print('计算完毕，结果已输出到output_auto.xlsx文件total页签中！\n')
        df_ave = df.groupby('_level').agg(mean_hp=('hp', 'mean'), mean_atk=('atk', 'mean'), mean_def=('def', 'mean'))
        df_ave.to_excel('output_auto_average.xlsx', sheet_name='average', index=False)

    # 读取data_400.xlsx表信息，计算属性并输出到output_400.xlsx

    elif cmd == '3':
        test_mode = False
        df = pd.read_excel('data_400.xlsx', header=0, sheet_name='Sheet1')  # Read data with row 1 header
        df.dropna(axis=0, how='all')  # Delete empty lines
        df['attribute'] = df.apply(
            lambda col: get_hero_property(col['_id'], col['_quality'], col['_level'], col['_lv_enhance'], col['_e_qua'],
                                          col['_e_enhance'], col['_talent'], col['_core'], col['_job'], ), axis=1)
        list_attr = df['attribute'].values.tolist()
        df1 = pd.DataFrame(list_attr)
        df = pd.concat([df, df1], axis=1)
        # 迎合bot表格式
        df.insert(2, '_type', 2)
        df.insert(6, '_e_list', '')
        df.insert(19, '_crit_bonus', 15000)
        df['_fury'] = 0
        df['_show_level'] = df['_level']
        df['_chase'] = 5000
        # print(df['power'])
        df = df.drop(['attribute', '_e_qua', '_e_enhance', '_core', '_job', 'power'], axis=1)
        df.to_excel('output_400.xlsx', index=False)

    elif cmd == '4':
        test_mode = False
        df = pd.read_excel('data.xlsx', header=0, sheet_name='Sheet1')  # Read data with row 1 header
        df.dropna(axis=0, how='all')

        print('正在处理基础属性...')
        df['attribute'] = df.apply(lambda col: get_hero_base_property(col['_id'], col['_quality'], col['_level'],
                                                                      col['_lv_enhance']), axis=1)
        save_output_auto(df, False, 'base')

        # print('正在处理装备属性...')
        # df['attribute'] = df.apply(
        #     lambda col: get_hero_equip_property(col['_id'], col['_quality'], col['_level'], col['_lv_enhance'],
        #                                         col['_e_qua'], col['_e_enhance']), axis=1)
        # save_output_auto(df, False, 'equip')
        #
        # print('正在处理Talent attributes...')
        # df['attribute'] = df.apply(
        #     lambda col: get_hero_talent_property(col['_id'], col['_quality'], col['_level'], col['_lv_enhance'],
        #                                          col['_talent']), axis=1)
        # save_output_auto(df, False, 'talent')
        #
        # print('正在处理研究所core attributes...')
        # df['attribute'] = df.apply(
        #     lambda col: get_hero_core_property(col['_id'], col['_quality'], col['_level'], col['_lv_enhance'],
        #                                        col['_core']), axis=1)
        # save_output_auto(df, False, 'core')
        #
        # print('正在处理研究所Class attributes...')
        # df['attribute'] = df.apply(
        #     lambda col: get_hero_job_property(col['_id'], col['_quality'], col['_level'], col['_lv_enhance'],
        #                                       col['_job']), axis=1)
        # save_output_auto(df, False, 'job')

        # df['attribute'] = df.apply(
        #     lambda col: get_hero_limiter_property(col['_id'], col['_quality'], col['_level'], col['_lv_enhance'],
        #                                           col['_limiter']), axis=1)
        # save_output_auto(df, False, 'limiter')
    elif cmd == '5':
        test_mode = False
        df = pd.read_excel('data_400_base.xlsx', header=0, sheet_name='Sheet1')  # Read data with row 1 header
        df.dropna(axis=0, how='all')  # Delete empty lines
        df['attribute'] = df.apply(
            lambda col: get_hero_property(col['_id'], col['_quality'], col['_level'], col['_lv_enhance'], col['_e_qua'],
                                          col['_e_enhance'], col['_talent'], col['_core'], col['_job'], ), axis=1)
        list_attr = df['attribute'].values.tolist()
        df1 = pd.DataFrame(list_attr)
        df = pd.concat([df, df1], axis=1)
        df = df.drop(['attribute', '_e_qua', '_e_enhance', '_core', '_job', 'power'], axis=1)
        df.to_excel('output_400_base.xlsx', index=False)

    # 根据提供的信息计算单个角色属性
    else:
        test_mode = True
        params = cmd.split(',')
        p = [int(i) for i in params]
        get_hero_property(p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8])
