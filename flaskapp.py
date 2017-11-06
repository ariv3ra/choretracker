#-*- coding: utf-8 -*-
#from __future__ import unicode_literals
import logging
import os,sys
import time
import datetime
import pymongo
import json
from pymongo import MongoClient
from flask import Flask, json, render_template
from flask_ask import Ask, request, session, question, statement
from twilio.rest import Client
from bson import BSON
from bson import json_util

app = Flask(__name__)
app.config.from_pyfile('flaskapp.cfg')  
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)

first_name = 'Etienne'
last_name = 'Rivera'

# Your Account Sid and Auth Token from twilio.com/user/account
account_sid = ""
auth_token  = ""

try:
    pathname = os.path.dirname(sys.argv[0])
    config_file = os.path.abspath(pathname)+'/config.json'
    with open(config_file) as data_file:
        data = json.load(data_file)
    # Service Creds
    MONGO_URI = data['MONGO_URI']
except IOError as err:
    print "[error] "+err.message

# Use this when auth is required
muri = MONGO_URI+"?authMechanism=SCRAM-SHA-1"

mconn = MongoClient(muri)
db = mconn['choretracker']

def zero_out_steps():
    db.steps.update_one({},{'$set':{"current_step":"0"}}, upsert=False)

def zero_out_errors():
    db.errors.remove({})

def zero_out_all():
    zero_out_errors()
    zero_out_steps()

def update_step(step):
    db.steps.update_one({},{'$set':{'current_step':str(step)}}, upsert=True)

def add_error(step):
    db.errors.insert({'error_step':str(step)})

def generate_speak(text):
    text = text.replace('&', 'and')
    text = text.strip()
    return '<speak>{0}</speak>'.format(text)

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
            add_amnt = round(transaction_amnt, 2)
            end_savings = start_savings
            end_balance = start_balance + add_amnt
        else:
            trans_type = 'credit'
            add_amnt = round(transaction_amnt/2, 2)
            end_savings = start_savings + add_amnt
            end_balance = start_balance + add_amnt
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
    print 'Start Wishlist'
    wlist =None
    for result in results:
        wlist = result
    print str(wlist)
    return wlist

def conv_dollars(amount):
    amt = '${:,.2f}'.format(amount)
    return amt

@ask.launch
def launch():
    card_title = render_template('card_title').encode('utf-8')
    question_text = render_template('welcome').encode('utf-8')
    reprompt_text = render_template('welcome_reprompt').encode('utf-8')
    return question(question_text).reprompt(reprompt_text).simple_card(card_title, question_text)

@ask.intent('CompleteChore')
def completed_chore():
    # db.steps.update_one({},{'$set':{"current_step":"0"}}, upsert=False)
    chore_amount = 5.00
    card_title = 'Chore Tracker'
    # db.entries.update({'current_step':1})
    trans = add_transaction(first_name,chore_amount,'trash')
    chore_amount = conv_dollars(chore_amount)
    amount = conv_dollars(trans['amount'])
    question_text = render_template('complete_chore',chore_amount=chore_amount, amount=amount).encode('utf-8')
    
    return question(generate_speak(question_text)).simple_card(card_title, question_text)

@ask.intent('AskForWishList')
def askforwishlist():
    wl = get_wishlist()
    item_name = wl['item'].format()
    item_price = '${:,.2f}'.format(wl['price'])
    item_url = wl['url']
    bal = get_balance(first_name)
    end_balance = '${:,.2f}'.format(float(bal['credit']))
    alexa_resp = None
    card_title = 'Chore Tracker'
    if bal['credit'] >= wl['price']:
        alexa_resp = 'yay_get_wishlist'
        question_text = render_template(alexa_resp,item_name=item_name,item_price=item_price,end_balance=end_balance).encode('utf-8')
        return question(generate_speak(question_text)).simple_card(card_title, question_text)
    else:
        alexa_resp = 'nay_get_wishlist'
        statement_text = render_template(alexa_resp,item_name=item_name,item_price=item_price,end_balance=end_balance).encode('utf-8')
        return statement(generate_speak(statement_text)).simple_card(card_title, statement_text)

@ask.intent('OrderWishlistItem')
def orderwishlistitem():
    wl = get_wishlist()
    item_name = wl['item'].format()
    item_price = '${:,.2f}'.format(wl['price'])
    item_url = wl['url']
    bal = get_balance(first_name)
    end_balance = '${:,.2f}'.format(float(bal['credit']))
    alexa_resp = None
    card_title = 'Chore Tracker'
    if bal['credit'] >= wl['price']:
        alexa_resp = 'yay_order_wishlist_item'
        data = add_transaction('Etienne',-wl['price'],'purchase')
        end_balance = conv_dollars(data['end_balance'])
        statement_text = render_template(alexa_resp,item_name=item_name,item_price=item_price,end_balance=end_balance).encode('utf-8')
        return statement(generate_speak(statement_text)).simple_card(card_title, statement_text)
    else:
        alexa_resp = 'nay_order_wishlist_item'
        question_text = render_template(alexa_resp).encode('utf-8')
        return question(generate_speak(question_text)).simple_card(card_title, question_text)


@ask.intent('AMAZON.StopIntent')
def stop():
    zero_out_all()
    bye_text = render_template('bye')
    return statement(bye_text)

@ask.intent('AMAZON.CancelIntent')
def cancel():
    zero_out_all()
    bye_text = render_template('bye')
    return statement(bye_text)
    
@ask.session_ended
def session_ended():
    return "", 200

if __name__ == '__main__':
    app.run(debug=True)