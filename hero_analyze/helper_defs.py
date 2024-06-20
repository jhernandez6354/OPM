def rage(input):
    amount = input[amount]
    target = input['target']
    trigger = input['trigger']
    rounds = input['rounds']

def chance(input):
    pct=input['pct']
    defense = input['defense']
    rounds = input['rounds'],
    target = input['enemy']

def atk(input):
    amount=input['amount']
    target=input['target']

def hp(input):
    amount=input['amount']
    target=input['target']

def defense(input):
    amount=input['amount']
    target=input['target']

def if_cond():
    condition=getattr('attr',input['if_cond'])(input['chance'])

def status(input):
    condition=getattr('attr',input['if_cond'])(input['chance'])
    acc=input['acc']
    rounds=input['rounds']
    target=input['target']

def ifnot_condition(input):
    condition=getattr('attr',input['if_cond'])(input[''])
    rounds=input['rounds']

def modify(input):
    trigger = input['trigger']
    target = input['target'],
    rounds = input['rounds']
    stack = bool(input['stack']),
    rage = input['rage']

def stack(input):
    max = input['max']

def sheild(input):
    amount = input['amount']
    target = input['target']

def condition(input):
    target = input['target']
    status = input['status']

def control_immune(input):
    target = input['target']

def chase():
    type = input['type']
    trigger = input['trigger']
    atk = input['atk']