from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pprint import pprint


import csv
import pandas as pd
import tweepy
import time
import numpy as np  
from textblob import TextBlob
import matplotlib.pyplot as plt


import os
file_path = os.path.abspath(os.getcwd())+"database.db"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+file_path
db = SQLAlchemy(app)


class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    username = db.Column(db.String, nullable=False)
    tweet = db.Column(db.Integer, default=0)
    def __repr__(self):
        return '<Task %r>' % self.id

# class Tweet(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     content = db.Column(db.String(200), nullable=False)
#     completed = db.Column(db.String, default=0)
#     date_created = db.Column(db.DateTime, default=datetime.utcnow)
#     def __repr__(self):
#         return '<Task %r>' % self.id

#twitter api key env 
api_key ="AbyvtiguFlUdXaV89ezG7cVV5"
api_secretkey ="5oZ7HHT1rdtDO1vYNUkb2ujgi5Qp8tmHEOdceDBxxoqlu9paJp"
access_token ="1382920208822673409-yDKO0c09zQ4Hs0qHAvmX0CCvhSTiNT"
access_secretoken ="JbCknojYQjTbTnXujPm2kNQ2bIYRfiHWQT4TErmVUb21a"

auth = tweepy.OAuthHandler(api_key,api_secretkey)
auth.set_access_token(access_token,access_secretoken)
api = tweepy.API(auth,wait_on_rate_limit=True)




# @app.route('/', methods=['POST', 'GET'])
# def index():
#     if request.method == 'POST':
#         task_content = request.form['content']
#         new_task = Todo(content=task_content)
#         try:
#             db.session.add(new_task)
#             db.session.commit()
#             return redirect('/')
#         except:
#             return 'Something went wrong'

#     else:
#         tasks = Todo.query.order_by(Todo.date_created).all()
#         return render_template("index.html", tasks=tasks)


@app.route('/', methods=['GET'])
def index():
    return render_template("testemplate.html")


@app.route('/getcomment',methods=['GET'])
def getComment():
    comment = request.args.get('comment')
    tweets = tweepy.Cursor(api.search, q=comment,count=100).items(5)
    data_list=[]

    db.session.query(Tweet).delete()
    for tweet in tweets:
        new_task = Tweet(date=tweet.created_at,username=tweet.user.screen_name,tweet=tweet.text)
        db.session.add(new_task)
        db.session.commit()
        db.session.close()
        data_list.append([tweet.created_at, tweet.user.screen_name, tweet.text])
    return jsonify({"data":data_list})

if __name__ == "__main__":
    app.run(debug=True)
