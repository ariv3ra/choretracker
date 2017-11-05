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
        add_amnt = round(transaction_amnt/2, 2)
        end_savings = start_savings + add_amnt
        end_balance = start_balance + add_amnt
        now = datetime.datetime.now()
        data= {'fname':first_name ,'lname':last_name, 'account':account, 'start_balance':start_balance, 'start_savings':start_savings,
        'amount':add_amnt, 'end_balance':end_balance, 'end_savings':end_savings, 'transaction_type':'credit','chore':chore_type, 'chore_date':now}
        doc_id = db.user.insert(data)
    return doc_id

def return_balance(fname):
    req = db.user.find({'lname':fname})limit(1).sort('chore_date', -1)
    bal_savings = None
    bal_balance = None
    for r in req:
        bal_savings = float(r['end_savings'])
        bal_balance = float(r['end_balance'])
    return {'credit' : bal_balance, 'savings': bal_savings}


fnames = ['Etienne','Angel','Pullova','Etienne','Pullova','Angel','Angel','Etienne','Pullova','Pullova','Etienne','Angel','Angel']
trans_amnts = [61.49, 73.76, 20.76, 70.1, 30.29, 60.2, 63.75, 57.69, 88.34, 36.88, 15.02, 30.24, 71.84]
chr_type = ['vaccuuming','trash','cleaning','vaccuuming','trash','cleaning','vaccuuming','trash','cleaning','lawn moaning']

print add_transaction('Etienne',5.00,'trash')

    #db.user.insert({})
# now = datetime.datetime.now()



# doc= {'fname' : 'Pullova', 'lname':'Feineis', 'account':'001','start_balance':0.00,'start_savings':0.00,'end_balance':10.00, 'end_savings':7.50, 'transaction_amnt': +17.50, 'transaction_type': 'credit', 'chore':'data mock up', 'chore_date': now}
# db.user.insert(doc)
# doc= {'fname' : 'Angel', 'lname':'Rivera', 'account':'001','start_balance':0.00,'start_savings':0.00,'end_balance':10.00, 'end_savings':7.50, 'transaction_amnt': +17.50, 'transaction_type': 'credit', 'chore':'data mock up', 'chore_date': now}
# db.user.insert(doc)
# db.user.insert(doc)

# db.user.find({'fname':'Martin'}).sort('chore_date', -1)
    # doc= {'fname' : 'Martin', 'lname':'Feineis', 'account':'001','start_balance':0.00,'start_savings':0.00,
    # 'end_balance':10.00, 'end_savings':7.50, 'transaction_amnt': +17.50, 'transaction_type': 'credit', 'chore':'data mock up', 'chore_date': now}