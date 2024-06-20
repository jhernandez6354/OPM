# Used to analyze role attributes

import pandas as pd
import os
from openpyxl import load_workbook


def compare_version(v1, v2):
    """
    Compare and return the newer version number
    :param v1:
    :param v2:
    :return:
    """
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
    """
    Get spec path
    :return:
    """
    _p = os.path.abspath('..') + "\\hero_analyze\\specs\\"
    folders = os.listdir(_p)
    current_version = folders[0]
    for folder in folders:
        current_version = compare_version(current_version, folder)
    return _p + current_version + '\\xlsx_origin\\'


def read_spec_file(file_name):
    """
    Read the spec table and process it uniformly
    :param file_name:
    :return:
    """
    # Read the data with the 3rd line header
    _df = pd.read_excel(path + file_name + '.xlsx', header=2, sheet_name=file_name)
    # Delete empty lines
    _df.dropna(axis=0, how='all')
    _df = _df.drop([0])
    return _df.reset_index()


def get_specific_property(_df, target_name, column_name1, value1, column_name2='', value2=None):
    """
    Get the value of the specified condition from the DataFrame, limiting up to two conditions
    :param _df:
    :param target_name:
    :param column_name1:
    :param value1:
    :param column_name2:
    :param value2:
    :return:
    """
    if column_name2 == '':
        n = _df[_df[column_name1] == value1].index.values.astype(int)[0]
    else:
        n = _df[(_df[column_name1] == value1) & (_df[column_name2] == value2)].index.values.astype(int)[0]
    return _df.loc[n, target_name]


def get_dict_from_str(_str,_name='AttributeInfo'):
    """
    Convert dictionary type data separated by ",;" into characters separated by ":," and unify the attribute name to _name
    :param _str:
    :return:
    """
    _str = str(_str)
    if _str == 'nan' or _str == '':
        return pd.Series({'AttributeInfo': None})
    _str = _str.replace(',', ':')
    _str = _str.replace(';', ',')
    _str = '{' + _str + '}'
    _dict = eval(_str)
    return pd.Series({_name: _dict})


def get_aura_dict_from_str(_str):
    return get_dict_from_str(_str,'AuraAttribute')


def get_type_aura_dict_from_str(_str):
    return get_dict_from_str(_str,'TypeAuraAttribute')


def read_data_from_specs():
    print('Reading spec data...')
    # 0. Determine the hero list, used to find out whether the limiter is open
    global df_heroes_configs
    df_heroes_configs = pd.read_excel('design table.xlsx', sheet_name='heroes', header=0, index_col='HeroId')
    df_heroes_configs.dropna(axis=0, how='all')

    # 1. 读取英雄基础信息
    global df_hero
    df_hero = read_spec_file('Hero')
    df_hero = df_hero.loc[:, df_hero.columns.intersection(
        ['Id', 'Rarity', 'Type', 'Role', 'HpBase', 'AtkBase', 'DefBase', 'CritBase', 'Job'])]
    df_hero = df_hero.drop(df_hero[df_hero['Id'] > 1000].index)

    # 2. 读取等级成长信息
    global df_hero_lv_growth
    df_hero_lv_growth = read_spec_file('HeroLevelGrowth')

    # 3. 读取等级突破成长信息
    global df_hero_grade_growth
    df_hero_grade_growth = read_spec_file('HeroGradeProperty')

    # 4. 读取品质成长信息
    global df_hero_quality_growth
    df_hero_quality_growth = read_spec_file('HeroQualityProperty')
    if a_type=='pve':
        df_hero_quality_growth = df_hero_quality_growth.join(
            df_hero_quality_growth['LimiterPropertyMax'].apply(get_dict_from_str))
        df_hero_quality_growth = df_hero_quality_growth.join(
            df_hero_quality_growth['LimiterAuraMax'].apply(get_aura_dict_from_str))
        df_hero_quality_growth = df_hero_quality_growth.join(
            df_hero_quality_growth['LimiterTypeAuraMax'].apply(get_type_aura_dict_from_str))
    else:
        df_hero_quality_growth = df_hero_quality_growth.join(
            df_hero_quality_growth['PvpLimiterPropertyMax'].apply(get_dict_from_str))
        df_hero_quality_growth = df_hero_quality_growth.join(
            df_hero_quality_growth['PvpLimiterAuraMax'].apply(get_aura_dict_from_str))
        df_hero_quality_growth = df_hero_quality_growth.join(
            df_hero_quality_growth['PvpLimiterTypeAuraMax'].apply(get_type_aura_dict_from_str))

    # 5. 读取天赋成长信息
    global df_hero_talent_growth
    df_hero_talent_growth = read_spec_file('HeroTalentAttribute')
    df_hero_talent_growth = df_hero_talent_growth.drop([0])
    df_hero_talent_growth = df_hero_talent_growth.join(df_hero_talent_growth['Attribute'].apply(get_dict_from_str))
    df_hero_talent_growth = df_hero_talent_growth.drop(['Attribute'], axis=1)

    # 6. 读取装备信息
    global df_equip_property
    df_equip_property = read_spec_file('Equip')
    df_equip_property = df_equip_property.join(df_equip_property['Attribute'].apply(get_dict_from_str))
    df_equip_property = df_equip_property.loc[:, df_equip_property.columns.intersection(['Id', 'AttributeInfo'])]

    # 7. 读取核心研究所信息
    global df_core_property
    df_core_property = read_spec_file('HeroAcademyLevel')
    if a_type == 'pve':
        df_core_property = df_core_property.join(df_core_property['Attribute'].apply(get_dict_from_str))
    else:
        df_core_property = df_core_property.join(df_core_property['PvpAttribute'].apply(get_dict_from_str))
    df_core_property = df_core_property.loc[:, df_core_property.columns.intersection(['Id', 'Level', 'AttributeInfo'])]

    # 7. 读取职阶信息
    global df_job_property
    df_job_property = read_spec_file('HeroJobLevel')
    if a_type == 'pve':
        df_job_property = df_job_property.join(df_job_property['Attribute'].apply(get_dict_from_str))
    else:
        df_job_property = df_job_property.join(df_job_property['PvpAttribute'].apply(get_dict_from_str))
    df_job_property = df_job_property.loc[:, df_job_property.columns.intersection(['Id', 'Job', 'Level', 'AttributeInfo'])]

    # 9. 读取英雄限制器突破信息
    global df_limiter
    df_limiter = read_spec_file('HeroLimiter')
    if a_type == 'pve':
        df_limiter = df_limiter.join(df_limiter['Property'].apply(get_dict_from_str))
        df_limiter = df_limiter.join(df_limiter['Aura'].apply(get_aura_dict_from_str))
        df_limiter = df_limiter.join(df_limiter['TypeAura'].apply(get_type_aura_dict_from_str))
    else:
        df_limiter = df_limiter.join(df_limiter['PvpProperty'].apply(get_dict_from_str))
        df_limiter = df_limiter.join(df_limiter['PvpAura'].apply(get_aura_dict_from_str))
        df_limiter = df_limiter.join(df_limiter['PvpTypeAura'].apply(get_type_aura_dict_from_str))
    df_limiter = df_limiter.loc[:, df_limiter.columns.intersection(['Id', 'Heroid', 'LimiterLevel', 'AttributeInfo', 'AuraAttribute', 'TypeAuraAttribute'])]

    # 10. 读取机械核心信息
    global df_mechanical_core
    df_mechanical_core = read_spec_file('MechanicalPowerLevel')
    if a_type == 'pve':
        df_mechanical_core = df_mechanical_core.join(df_mechanical_core['Attribute'].apply(get_dict_from_str))
    else:
        df_mechanical_core = df_mechanical_core.join(df_mechanical_core['PvpAttribute'].apply(get_dict_from_str))
    df_mechanical_core = df_mechanical_core.loc[:, df_mechanical_core.columns.intersection(['Id', 'Heroid', 'Level', 'AttributeInfo'])]

    # 8. 读取战力参数
    df_configs = read_spec_file('Configs')
    global power_hp
    power_hp = get_specific_property(df_configs, 'value', 'key', 'PowerParamHp')
    global power_atk
    power_atk = get_specific_property(df_configs, 'value', 'key', 'PowerParamAtk')
    global power_def
    power_def = get_specific_property(df_configs, 'value', 'key', 'PowerParamDef')
    global power_crit
    power_crit = get_specific_property(df_configs, 'value', 'key', 'PowerParamCrit')
    global power_crit_res
    power_crit_res = get_specific_property(df_configs, 'value', 'key', 'PowerParamCritRes')
    global power_parry
    power_parry = get_specific_property(df_configs, 'value', 'key', 'PowerParamParry')
    global power_precise
    power_precise = get_specific_property(df_configs, 'value', 'key', 'PowerParamPrecise')
    global power_dmg_res
    power_dmg_res = get_specific_property(df_configs, 'value', 'key', 'PowerParamDmgRes')

    print('Spec data reading is completed!')


# 生成标准状态角色属性
def get_standard_bot_info():
    """
    Obtain the standard status of each character between levels 1-500
    :return:
    """
    _df1 = pd.read_excel('design table.xlsx', sheet_name='heroes', header=0)
    s1 = _df1['HeroId']

    _df2 = pd.DataFrame()
    if a_type == 'pve':
        _df2 = pd.read_excel('design table.xlsx', sheet_name='autobot', header=0)
    else:
        _df2 = pd.read_excel('design table.xlsx', sheet_name='autobot_pvp', header=0)
    _df4 = pd.DataFrame()

    for i in s1:
        _df3 = _df2.copy(deep=True)
        _df3.insert(0, '_id', i)
        _df4 = pd.concat([_df4, _df3], axis=0)
    return _df4


# 生成用于AI combat的bot，数据源：design table.xlsx
def get_designed_bot_info():
    """
    Get the bot of conditions set in the design table
    :return:
    """
    _df1 = pd.read_excel('design table.xlsx', sheet_name='heroes', header=0)
    s1 = _df1['HeroId']

    _df2 = pd.DataFrame()
    if a_type == 'pve':
        _df2 = pd.read_excel('design table.xlsx', sheet_name='conditions', header=0)
    else:
        _df2 = pd.read_excel('design table.xlsx', sheet_name='conditions_pvp', header=0)

    _df4 = pd.DataFrame()
    for i in s1:
        _df3 = _df2.copy(deep=True)
        _df3.insert(0, '_id', i)
        _df4 = pd.concat([_df4, _df3], axis=0)
    return _df4


def get_designed_conditions_bot_info():
    """
        Get the bot of the conditions set by the design table
        :return:
        """
    _df1 = pd.read_excel('design table.xlsx', sheet_name='heroes', header=0)
    s1 = _df1['HeroId']

    _df2 = pd.DataFrame()
    if a_type == 'pve':
        _df2 = pd.read_excel('design table.xlsx', sheet_name='conditions_400', header=0)
    else:
        _df2 = pd.read_excel('design table.xlsx', sheet_name='conditions_400_pvp', header=0)

    _df4 = pd.DataFrame()
    for i in s1:
        _df3 = _df2.copy(deep=True)
        _df3.insert(0, '_id', i)
        _df4 = pd.concat([_df4, _df3], axis=0)
    return _df4


def _excel_add_sheet(_df, _writer, sht_name):
    """
    Store the data in the sheet by replacing the sheet excel
    :param _df:
    :param _writer:
    :param sht_name:
    :return:
    """
    book = load_workbook(_writer.path)
    _writer.book = book
    _df.to_excel(excel_writer=_writer, sheet_name=sht_name, index=None)
    _writer.close()


def save_output_auto(_df, is_total=False, _name=''):
    _list_attr = _df['attribute'].values.tolist()
    _df1 = pd.DataFrame(_list_attr)
    _df = pd.concat([_df, _df1], axis=1)
    _df = _df.drop(['attribute'], axis=1)
    if is_total:
        _df['team_power'] = _df['power'] * 5
    _file_name = 'Summary of PVE attributes.xlsx' if a_type == 'pve' else 'Summary of PVP attributes'
    excel_writer = pd.ExcelWriter('Summary of PVE attributes.xlsx', engine='openpyxl')
    _excel_add_sheet(_df, excel_writer, _name)


# Attribute analysis module
def get_hero_grade_by_level(_level):
    if _level <= 10:
        return 1
    else:
        return min(19, int((_level - 1) / 20) + 2)


def get_hero_equips(_role, _quality):
    if a_type == 'pve':
        return [_role * 1000 + 100 + _quality,
                _role * 1000 + 200 + _quality,
                _role * 1000 + 300 + _quality,
                _role * 1000 + 400 + _quality]
    else:
        return [_role * 1000 + 100 + 10,
                _role * 1000 + 200 + 10,
                _role * 1000 + 300 + 10,
                _role * 1000 + 400 + 10]


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


def get_power(hero_hp, hero_atk, hero_def, hero_crit, hero_crit_res, hero_precise, hero_parry, hero_dmg_res):
    return hero_hp * power_hp + hero_atk * power_atk + hero_def * power_def + hero_crit * power_crit + \
           hero_crit_res * power_crit_res + hero_precise * power_precise + hero_parry * power_parry + \
           hero_dmg_res * power_dmg_res


def calculate_properties(hp_base, atk_base, def_base, crit_base, property_dict, _hp_m=99999999, _atk_m=99999999, _def_m=99999999, _init=False):
    # Calculate final properties
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
        hero_hp = min(_hp_m, hp_base * (property_dict[22]) / 10000) + property_dict[21]
        hero_atk = min(_atk_m, atk_base * (property_dict[32]) / 10000) + property_dict[31]
        hero_def = min(_def_m, def_base * (property_dict[42]) / 10000) + property_dict[41]
        hero_crit = property_dict[70]
        hero_crit_res = property_dict[60]
        hero_precise = property_dict[150]
        hero_parry = property_dict[140]
        hero_dmg_res = property_dict[50]

    # Calculate combat effectiveness
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
    global id_now
    if _id != id_now:
        id_now = _id
        print('\t is handling the role:%d' % _id)
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
    # 角色品阶属性
    _grade = get_hero_grade_by_level(_level)
    hp_grade_inc = get_specific_property(df_hero_grade_growth, 'HpInc', 'HeroId', _id, 'GradeLevel', _grade)
    atk_grade_inc = get_specific_property(df_hero_grade_growth, 'AtkInc', 'HeroId', _id, 'GradeLevel', _grade)
    def_grade_inc = get_specific_property(df_hero_grade_growth, 'DefInc', 'HeroId', _id, 'GradeLevel', _grade)
    if test_mode:
        print('Level growth: life = %f, attack = %f, defense = %f' % (hp_grade_inc, atk_grade_inc, def_grade_inc))
    # 计算角色Basic attributes
    hp_base = hp_init + hp_lv_inc * hp_qua_per / 10000 + hp_qua_inc + hp_grade_inc
    atk_base = atk_init + atk_lv_inc * atk_qua_per / 10000 + atk_qua_inc + atk_grade_inc
    def_base = def_init + def_lv_inc * def_qua_per / 10000 + def_qua_inc + def_grade_inc
    crit_base = crit_init

    return hp_base, atk_base, def_base, crit_base


def get_hero_property(_id, _quality, _level, _lv_enhance, _e_qua, _e_enhance, _talent, _core, _job, _limiter=0):
    global id_now
    if _id != id_now:
        id_now = _id
        print('\t is handling the role:%d' % _id)

    # 计算角色Basic attributes
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

    # Character talent attributes
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

    # 职阶属性
    if _job > 0:
        property_dict = {21: 0, 22: 0, 31: 0, 32: 0, 41: 0, 42: 0, 50: 0, 60: 0, 70: 0, 140: 0, 150: 0}
        job = get_specific_property(df_hero, 'Job', 'Id', _id)
        job_attr = get_specific_property(df_job_property, 'AttributeInfo', 'Level', _job, 'Job', job)
        if test_mode:
            print_attribute(job_attr, 'Class attributes: ')
        property_dict = union_dict(property_dict, job_attr)
        hero_dict = union_dict(hero_dict, calculate_properties(hp_base, atk_base, def_base, crit_base, property_dict))

    # 限制器突破-自身属性
    if (_limiter > 0) & (df_heroes_configs.loc[_id, 'Limiter'] == 1):
        property_dict = {21: 0, 22: 0, 31: 0, 32: 0, 41: 0, 42: 0, 50: 0, 60: 0, 70: 0, 140: 0, 150: 0}

        limiter_attr = get_specific_property(df_limiter, 'AttributeInfo', 'LimiterLevel', _limiter, 'Heroid', _id)

        if test_mode:
            print_attribute(limiter_attr, 'Limiter properties: ')
        property_dict = union_dict(property_dict, limiter_attr)

        hp_max = \
            get_specific_property(df_hero_quality_growth, 'AttributeInfo', 'HeroId', _id, 'QualityLevel', _quality)[21]
        atk_max = \
            get_specific_property(df_hero_quality_growth, 'AttributeInfo', 'HeroId', _id, 'QualityLevel', _quality)[31]
        def_max = \
            get_specific_property(df_hero_quality_growth, 'AttributeInfo', 'HeroId', _id, 'QualityLevel', _quality)[41]

        hero_dict = union_dict(hero_dict,
                               calculate_properties(hp_base, atk_base, def_base, crit_base, property_dict, hp_max,
                                                    atk_max, def_max))
    # 输出最终属性
    if test_mode:
        print(hero_dict)
    return hero_dict


def get_hero_equip_property(_id, _quality, _level, _lv_enhance, _e_qua, _e_enhance):
    global id_now
    if _id != id_now:
        id_now = _id
        print('\t is handling the role: %d' % _id)

    # 角色装备属性
    property_dict = {21: 0, 22: 0, 31: 0, 32: 0, 41: 0, 42: 0, 50: 0, 60: 0, 70: 0, 140: 0, 150: 0}
    if _e_qua > 0:
        _role = get_specific_property(df_hero, 'Role', 'Id', _id)
        equip_list = get_hero_equips(_role, _e_qua)
        for equip in equip_list:
            equip_attr = get_specific_property(df_equip_property, 'AttributeInfo', 'Id', equip)

            # 默认规则：如果有强化，则默认该装备有类型加成，否则无加成
            if _e_enhance > 0:
                property_dict = union_dict(property_dict, equip_attr, 1.3 + _e_enhance / 10)
            else:
                property_dict = union_dict(property_dict, equip_attr, 1)
    return calculate_properties(0, 0, 0, 0, property_dict)


def get_hero_talent_property(_id, _quality, _level, _lv_enhance, _talent):
    global id_now
    if _id != id_now:
        id_now = _id
        print('\tProcessing role：%d' % _id)

    hp_base, atk_base, def_base, crit_base = get_hero_base_property(_id, _quality, _level, _lv_enhance)
    property_dict = {21: 0, 22: 0, 31: 0, 32: 0, 41: 0, 42: 0, 50: 0, 60: 0, 70: 0, 140: 0, 150: 0}
    if _talent >= 0:
        talent_attr = get_specific_property(df_hero_talent_growth, 'AttributeInfo', 'HeroId', _id, 'TalentLevel',
                                            _talent)
        property_dict = union_dict(property_dict, talent_attr)
    return calculate_properties(hp_base, atk_base, def_base, crit_base, property_dict)


def get_hero_core_property(_id, _quality, _level, _lv_enhance, _core):
    global id_now
    if _id != id_now:
        id_now = _id
        print('\tProcessing role：%d' % _id)

    property_dict = {21: 0, 22: 0, 31: 0, 32: 0, 41: 0, 42: 0, 50: 0, 60: 0, 70: 0, 140: 0, 150: 0}
    if _core > 0:
        core_attr = get_specific_property(df_core_property, 'AttributeInfo', 'Id', _core)
        property_dict = union_dict(property_dict, core_attr)
    return calculate_properties(0, 0, 0, 0, property_dict)


def get_hero_job_property(_id, _quality, _level, _lv_enhance, _job):
    global id_now
    if _id != id_now:
        id_now = _id
        print('\tProcessing role：%d' % _id)

    property_dict = {21: 0, 22: 0, 31: 0, 32: 0, 41: 0, 42: 0, 50: 0, 60: 0, 70: 0, 140: 0, 150: 0}
    if _job > 0:
        job = get_specific_property(df_hero, 'Job', 'Id', _id)
        job_attr = get_specific_property(df_job_property, 'AttributeInfo', 'Level', _job, 'Job', job)
        property_dict = union_dict(property_dict, job_attr)
    return calculate_properties(0, 0, 0, 0, property_dict)


def get_hero_limiter_property(_id, _quality, _level, _lv_enhance, _limiter):
    global id_now
    if _id != id_now:
        id_now = _id
        print('\tProcessing role：%d' % _id)

    property_dict = {21: 0, 22: 0, 31: 0, 32: 0, 41: 0, 42: 0, 50: 0, 60: 0, 70: 0, 140: 0, 150: 0}
    if (_limiter > 0) & (df_heroes_configs.loc[_id, 'Limiter'] == 1):
        hp_base, atk_base, def_base, crit_base = get_hero_base_property(_id, _quality, _level, _lv_enhance)
        limiter_attr = get_specific_property(df_limiter, 'AttributeInfo', 'LimiterLevel', _limiter, 'Heroid', _id)
        property_dict = union_dict(property_dict, limiter_attr)
        hp_max = \
            get_specific_property(df_hero_quality_growth, 'AttributeInfo', 'HeroId', _id, 'QualityLevel', _quality)[21]
        atk_max = \
            get_specific_property(df_hero_quality_growth, 'AttributeInfo', 'HeroId', _id, 'QualityLevel', _quality)[31]
        def_max = \
            get_specific_property(df_hero_quality_growth, 'AttributeInfo', 'HeroId', _id, 'QualityLevel', _quality)[41]
        return calculate_properties(hp_base, atk_base, def_base, crit_base, property_dict, hp_max, atk_max, def_max)
    else:
        return calculate_properties(0, 0, 0, 0, property_dict, 0, 0, 0)


def get_hero_limiter_aura(_id, _quality, _level, _lv_enhance, _limiter):
    global id_now
    if _id != id_now:
        id_now = _id
        print('\tProcessing role：%d' % _id)

    property_dict = {21: 0, 22: 0, 31: 0, 32: 0, 41: 0, 42: 0, 50: 0, 60: 0, 70: 0, 140: 0, 150: 0}
    if (_limiter > 0) & (df_heroes_configs.loc[_id, 'Limiter'] == 1):
        hp_base, atk_base, def_base, crit_base = get_hero_base_property(_id, _quality, _level, _lv_enhance)
        aura_attr = get_specific_property(df_limiter, 'AuraAttribute', 'LimiterLevel', _limiter, 'Heroid', _id)
        property_dict = union_dict(property_dict, aura_attr)
        hp_max = \
            get_specific_property(df_hero_quality_growth, 'AuraAttribute', 'HeroId', _id, 'QualityLevel', _quality)[21]
        atk_max = \
            get_specific_property(df_hero_quality_growth, 'AuraAttribute', 'HeroId', _id, 'QualityLevel', _quality)[31]
        def_max = \
            get_specific_property(df_hero_quality_growth, 'AuraAttribute', 'HeroId', _id, 'QualityLevel', _quality)[41]
        return calculate_properties(hp_base, atk_base, def_base, crit_base, property_dict, hp_max, atk_max, def_max)
    else:
        return calculate_properties(0, 0, 0, 0, property_dict, 0, 0, 0)


def get_hero_limiter_type_aura(_id, _quality, _level, _lv_enhance, _limiter):
    global id_now
    if _id != id_now:
        id_now = _id
        print('\tProcessing role：%d' % _id)

    property_dict = {21: 0, 22: 0, 31: 0, 32: 0, 41: 0, 42: 0, 50: 0, 60: 0, 70: 0, 140: 0, 150: 0}
    if (_limiter > 0) & (df_heroes_configs.loc[_id, 'Limiter'] == 1):
        hp_base, atk_base, def_base, crit_base = get_hero_base_property(_id, _quality, _level, _lv_enhance)
        aura_attr = get_specific_property(df_limiter, 'TypeAuraAttribute', 'LimiterLevel', _limiter, 'Heroid', _id)
        property_dict = union_dict(property_dict, aura_attr)
        hp_max = \
            get_specific_property(df_hero_quality_growth, 'TypeAuraAttribute', 'HeroId', _id, 'QualityLevel', _quality)[21]
        atk_max = \
            get_specific_property(df_hero_quality_growth, 'TypeAuraAttribute', 'HeroId', _id, 'QualityLevel', _quality)[31]
        def_max = \
            get_specific_property(df_hero_quality_growth, 'TypeAuraAttribute', 'HeroId', _id, 'QualityLevel', _quality)[41]
        return calculate_properties(hp_base, atk_base, def_base, crit_base, property_dict, hp_max, atk_max, def_max)
    else:
        return calculate_properties(0, 0, 0, 0, property_dict, 0, 0, 0)


def get_mechanical_property(_id, _mechanical):
    global id_now
    if _id != id_now:
        id_now = _id
        print('\tProcessing role：%d' % _id)
    property_dict = {21: 0, 22: 0, 31: 0, 32: 0, 41: 0, 42: 0, 50: 0, 60: 0, 70: 0, 140: 0, 150: 0}
    if _mechanical > 0:
        pass


def save_df(_df_o, _name, title=''):
    _df = _df_o.reset_index()
    _list_attr = _df['attribute'].values.tolist()
    _df1 = pd.DataFrame(_list_attr)
    _df = pd.concat([_df, _df1], axis=1)
    _df = _df.drop(['attribute'], axis=1)
    if title == '':
        if a_type == 'pve':
            _df.to_excel('1-500LevelPVEattributes_'+_name+'.xlsx',sheet_name=_name)
        else:
            _df.to_excel('1-500LevelPVEattributes_'+_name+'.xlsx', sheet_name=_name)
    else:
        _df.to_excel(title + _name + '.xlsx', sheet_name=_name)


def analyze_standard_bot():
    df = get_standard_bot_info()

    print('Processing base properties...')
    df['attribute'] = df.apply(lambda col: get_hero_base_property(col['_id'], col['_quality'], col['_level'], col['_lv_enhance']), axis=1)
    save_df(df, 'base')

    print('Processing equipment properties...')
    df['attribute'] = df.apply(lambda col: get_hero_equip_property(col['_id'], col['_quality'], col['_level'], col['_lv_enhance'], col['_e_qua'], col['_e_enhance']), axis=1)
    save_df(df, 'equip')

    print('Processing talent attributes...')
    df['attribute'] = df.apply(
        lambda col: get_hero_talent_property(col['_id'], col['_quality'], col['_level'], col['_lv_enhance'],
                                             col['_talent']), axis=1)
    save_df(df, 'talent')

    print('Processing the core attributes of the institute...')
    df['attribute'] = df.apply(
        lambda col: get_hero_core_property(col['_id'], col['_quality'], col['_level'], col['_lv_enhance'],
                                           col['_core']), axis=1)
    save_df(df, 'core')

    print('Processing research institute rank attributes...')
    df['attribute'] = df.apply(
        lambda col: get_hero_job_property(col['_id'], col['_quality'], col['_level'], col['_lv_enhance'],
                                          col['_job']), axis=1)
    save_df(df, 'job')

    print('Processing limiter properties...')
    df['attribute'] = df.apply(
        lambda col: get_hero_limiter_property(col['_id'], col['_quality'], col['_level'], col['_lv_enhance'],
                                              col['_limiter']), axis=1)
    save_df(df, 'limiter')

    print('Processing general attributes...')
    df['attribute'] = df.apply(
        lambda col: get_hero_property(col['_id'], col['_quality'], col['_level'], col['_lv_enhance'], col['_e_qua'],
                                      col['_e_enhance'], col['_talent'], col['_core'], col['_job'], col['_limiter']), axis=1)
    save_df(df, 'total')


def analyze_target_bot():
    df = get_standard_bot_info()

    print('Processing base properties...')
    df['attribute'] = df.apply(
        lambda col: get_hero_base_property(col['_id'], col['_quality'], col['_level'], col['_lv_enhance']), axis=1)
    df = df.loc[df['_level']==target_lv]
    save_df(df, 'base_' + str(target_lv))


def analyze_design_bot():
    """
    Run AI combat bot according to the design table
    :return:
    """
    df = get_designed_bot_info()

    print('Processing base properties...')
    df['attribute'] = df.apply(lambda col: get_hero_base_property(col['_id'], col['_quality'], col['_level'],
                                                                  col['_lv_enhance']), axis=1)
    save_df(df, a_type + '_base', 'AI combat')

    print('Processing equipment properties...')
    df['attribute'] = df.apply(
        lambda col: get_hero_equip_property(col['_id'], col['_quality'], col['_level'], col['_lv_enhance'],
                                            col['_e_qua'], col['_e_enhance']), axis=1)
    save_df(df, a_type + '_equip', 'AI combat')

    print('Processing talent attributes...')
    df['attribute'] = df.apply(
        lambda col: get_hero_talent_property(col['_id'], col['_quality'], col['_level'], col['_lv_enhance'],
                                             col['_talent']), axis=1)
    save_df(df, a_type + '_talent', 'AI combat')

    print('Processing the core attributes of the institute...')
    df['attribute'] = df.apply(
        lambda col: get_hero_core_property(col['_id'], col['_quality'], col['_level'], col['_lv_enhance'],
                                           col['_core']), axis=1)
    save_df(df, a_type + '_core', 'AI combat')

    print('Processing research institute rank attributes...')
    df['attribute'] = df.apply(
        lambda col: get_hero_job_property(col['_id'], col['_quality'], col['_level'], col['_lv_enhance'],
                                          col['_job']), axis=1)
    save_df(df, a_type + '_job', 'AI combat')

    print('Processing limiter properties...')
    df['attribute'] = df.apply(
        lambda col: get_hero_limiter_property(col['_id'], col['_quality'], col['_level'], col['_lv_enhance'],
                                              col['_limiter']), axis=1)
    save_df(df, a_type + '_limiter', 'AI combat')

    print('Processing limiter halo properties...')
    df['attribute'] = df.apply(
        lambda col: get_hero_limiter_aura(col['_id'], col['_quality'], col['_level'], col['_lv_enhance'],
                                              col['_limiter']), axis=1)
    save_df(df, a_type + '_limiter_aura', 'AI combat')

    print('Processing limiter type halo properties...')
    df['attribute'] = df.apply(
        lambda col: get_hero_limiter_type_aura(col['_id'], col['_quality'], col['_level'], col['_lv_enhance'],
                                              col['_limiter']), axis=1)
    save_df(df, a_type + '_limiter_type_aura', 'AI combat')

    print('Processing general attributes...')
    df['attribute'] = df.apply(
        lambda col: get_hero_property(col['_id'], col['_quality'], col['_level'], col['_lv_enhance'], col['_e_qua'],
                                      col['_e_enhance'], col['_talent'], col['_core'], col['_job'], col['_limiter']), axis=1)
    save_df(df, a_type + '_total', 'AI combat')


def get_design_conditions_bot():
    df = get_designed_conditions_bot_info()

    df['attribute'] = df.apply(lambda col: get_hero_base_property(col['_id'], col['_quality'], col['_level'],
                                                                  col['_lv_enhance']), axis=1)
    save_df(df, a_type, '400_280Basic attributes')
    print('The data has been stored in'+'400_280Basic attributes'+a_type+'.xlsx')


a_type = ''
id_now = 0
test_mode = False
mode = ''

while True:
    a_type = input('Analysis type(pve?pvp):\n')
    if a_type == 'pve':
        break
    elif a_type == 'pvp':
        break
    else:
        print('Please re-enter, only lowercase letters pve or pvp\n')

while True:
    mode = input('Analysis mode (all?a?b?c?d):\nall: All analysis\na: Analyze standard model attributes of levels 1-500\nb: Generate BOT for AI balance test\nc: Enter the level by yourself\nd: Generate Specific level basic attributes\ne: Generate 400-level basic attributes of each quality\n')
    if mode not in ['all', 'a', 'b', 'c', 'd', 'e']:
        print('Please re-enter, only lowercase letters pve or pvp\n')
    else:
        break

# 初始化数据
df_heroes_configs = pd.DataFrame()
df_hero = pd.DataFrame()
df_hero_lv_growth = pd.DataFrame()
df_hero_grade_growth = pd.DataFrame()
df_hero_quality_growth = pd.DataFrame()
df_hero_talent_growth = pd.DataFrame()
df_equip_property = pd.DataFrame()
df_core_property = pd.DataFrame()
df_job_property = pd.DataFrame()
df_limiter = pd.DataFrame()
df_mechanical_core = pd.DataFrame()
power_hp = 0
power_atk = 0
power_def = 0
power_crit = 0
power_crit_res = 0
power_parry = 0
power_precise = 0
power_dmg_res = 0

# Attribute analysis
path = set_version_path()
read_data_from_specs()

if mode in ['all', 'a']:
    analyze_standard_bot()
if mode in ['all', 'b']:
    analyze_design_bot()
if mode in ['c']:
    while True:
        cmd = input('Input id: quality: level: level enhancement: equipment quality: equipment level: talent: core: class: limiter\n')
        test_mode = True
        params = cmd.split(',')
        p = [int(i) for i in params]
        get_hero_property(p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8],p[9])

target_lv = 0
if mode in ['d']:
    while True:
        cmd = input('Enter hero level (1-500):')
        try:
            target_lv = int(cmd)
            if (target_lv>0) and (target_lv<=500):
                break
            print('Please enter an integer from 1-500!')
        except ValueError:
            print("That is not a valid number.")
            print('Please enter an integer from 1-500!')
    print(target_lv)
    analyze_target_bot()

if mode in ['e']:
    get_design_conditions_bot()