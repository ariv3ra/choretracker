import datetime, json, pymongo, requests, os, sys


try:
    pathname = os.path.dirname(sys.argv[0])
    config_file = os.path.abspath(pathname)+'/config.json'
    with open(config_file) as data_file:
        data = json.load(data_file)
    # Service Creds
    MONGO_URI = data['MONGO_URI']
except IOError as err:
    print "[error] "+err.message

client = pymongo.MongoClient(MONGO_URI)
db = client.choretracker    

def create_acc(name):
    """creating account"""
    payload = json.dumps({'team_name':name})
    rest = 'https://3hkaob4gkc.execute-api.us-east-1.amazonaws.com/prod/au-hackathon/accounts'
    req = requests.post(rest, data=payload)
    return req.text

def list_acc(acc_id):
    """listing account"""
    payload = json.dumps({'account_id':acc_id})
    rest = 'https://3hkaob4gkc.execute-api.us-east-1.amazonaws.com/prod/au-hackathon/accounts'
    req = requests.post(rest, data=payload)
    return req.text

def add_authed_user(acc_id=None,team_name=None):
    """add a user to an account"""
    if acc_id == None and team_name == None:
        raise ValueError("account id or team_name must be defined")
    if acc_id == None:
        pass #get account by team_name
    if team_name == None:
        pass # get account by account id

    payload = json.dumps({'team_name': team_name, 'account_id': acc_id})
    rest = 'https://3hkaob4gkc.execute-api.us-east-1.amazonaws.com/prod/au-hackathon/accounts'
    req = requests.post(rest, data=payload)
    return req.text

def add_chore(type):
    pass

def close_chore(type):
    pass

def create_chore(type):
    pass

def add_transaction(fname,transaction_amnt,chore_type):
    results = db.user.find({'fname':fname}).limit(1).sort('chore_date', -1)
    data = None
    doc_id = None
    for result in results:
        last_name = result['lname']
        first_name = result['fname']
        account = result['account']
        start_balance = result['end_balance']
        start_savings = result['end_savings']
        add_amnt = None
        end_savings =None
        end_balance = None
        now = datetime.datetime.now()
        if transaction_amnt < 0:
            trans_type = 'debit'
        else:
            trans_type = 'credit'
        data = {'fname':first_name, 'lname':last_name, 'account':account, 
                'start_balance':start_balance, 'start_savings':start_savings, 
                'amount':add_amnt, 'end_balance':end_balance, 'end_savings':end_savings, 
                'transaction_type':trans_type, 'chore':chore_type, 'chore_date':now}
        doc_id = db.user.insert(data)
        data['_id'] = doc_id
    return data

def get_balance(fname):
    req = db.user.find({'fname':fname}).limit(1).sort('chore_date', -1)
    bal_savings = None
    bal_balance = None
    for r in req:
        bal_savings = r['end_savings']
        bal_balance = r['end_balance']
    return {'credit' : bal_balance, 'savings': bal_savings}

def get_wishlist():
    results = db.wishlist.find({'purchased':False}).limit(1).sort('ranking',1)
    wlist =None
    for result in results:
        wlist = result
    return wlist



# print add_transaction('Etienne',5.00,'trash')
print get_balance('Etienne')
