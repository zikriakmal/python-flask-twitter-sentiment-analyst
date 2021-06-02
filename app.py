from flask import Flask, render_template, url_for, request, Response, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pprint import pprint


from bs4 import BeautifulSoup
from google_trans_new import google_translator  
from textblob import TextBlob
from datetime import datetime


import csv
import pandas as pd
import tweepy
import time
import numpy as np
import matplotlib.pyplot as plt
import re
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
        return '<Tweet %r>' % self.id

class TweetCleanTranslate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    username = db.Column(db.String, nullable=False)
    tweet = db.Column(db.Integer, default=0)
    clean_html = db.Column(db.String)
    clean_mention = db.Column(db.String)
    english = db.Column(db.String)

    def __repr__(self):
        return '<TweetCleanTranslate %r>' % self.id

class TweetSentiment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    username = db.Column(db.String, nullable=False)
    tweet = db.Column(db.Integer, default=0)
    clean_html = db.Column(db.String)
    clean_mention = db.Column(db.String)
    english = db.Column(db.String)
    sentiment_analyst = db.Column(db.String)
    polarity = db.Column(db.String)

    def __repr__(self):
        return '<TweetSentiment %r>' % self.id



# class Tweet(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     content = db.Column(db.String(200), nullable=False)
#     completed = db.Column(db.String, default=0)
#     date_created = db.Column(db.DateTime, default=datetime.utcnow)
#     def __repr__(self):
#         return '<Task %r>' % self.id


# twitter api key env
api_key = "AbyvtiguFlUdXaV89ezG7cVV5"
api_secretkey = "5oZ7HHT1rdtDO1vYNUkb2ujgi5Qp8tmHEOdceDBxxoqlu9paJp"
access_token = "1382920208822673409-yDKO0c09zQ4Hs0qHAvmX0CCvhSTiNT"
access_secretoken = "JbCknojYQjTbTnXujPm2kNQ2bIYRfiHWQT4TErmVUb21a"

auth = tweepy.OAuthHandler(api_key, api_secretkey)
auth.set_access_token(access_token, access_secretoken)
api = tweepy.API(auth, wait_on_rate_limit=True)

@app.route('/', methods=['GET'])
def index():
    return render_template("testemplate.html")


@app.route('/getcomment', methods=['GET'])
def getComment():
    comment = request.args.get('comment')
    tweets = tweepy.Cursor(api.search, q=comment, count=100).items(5)
    data_list = []

    db.session.query(Tweet).delete()
    for tweet in tweets:
        new_task = Tweet(date=tweet.created_at,
                         username=tweet.user.screen_name, tweet=tweet.text)
        db.session.add(new_task)
        db.session.commit()
        db.session.close()
        data_list.append(
            [tweet.created_at, tweet.user.screen_name, tweet.text])
    return jsonify({"data": data_list})


@app.route('/cleanhtmlmention', methods=['GET'])
def cleanHtml():
    data_list = []
    tableTweet = Tweet.query.all()
    for data in tableTweet:
        data_list.append([data.date, data.username, data.tweet])

    telkomsel_data = pd.DataFrame(data_list)
    headers = ['Date', 'Username', 'tweet']
    telkomsel_data.columns = headers

    i = 0
    jlhkarakter = []
    for column in telkomsel_data.tweet:
        jlhkarakter.insert(i, len(telkomsel_data["tweet"][i]))
        i += 1

    telkomsel_data["karakter"] = jlhkarakter

    cleanHTML = []
    i = 0
    for column in telkomsel_data.tweet:
        # menghilangkan text field as ‘&amp’,’&quot’,etc
        clean = BeautifulSoup(telkomsel_data.tweet[i], 'lxml')
        cleanHTML.insert(i, clean.get_text())
        i += 1

    telkomsel_data["cleanHTML"] = cleanHTML

    cleanMention = []
    i = 0
    for column in telkomsel_data.cleanHTML:
        # menghilangkan tanda @ mention
        clean = re.sub(r'@[A-Za-z0-9_]+', '', telkomsel_data.cleanHTML[i])
        cleanMention.insert(i, clean)
        i += 1

    telkomsel_data["cleanMention"] = cleanMention
    translator = google_translator()  
    telkomsel_data['English'] = telkomsel_data['cleanMention'].apply(translator.translate, lang_src='id', lang_tgt='en')

    newdatalist = []
    db.session.query(TweetCleanTranslate).delete()
    for data in telkomsel_data.to_numpy():
        new_task = TweetCleanTranslate(date=data[0],username=data[1],tweet = data[3],clean_html=data[2],clean_mention=data[5],english=data[6] )
        db.session.add(new_task)
        db.session.commit()
        db.session.close()
        newdatalist.append([data[0].strftime('%B-%d-%Y %I:%M %p'),data[1],data[3],data[2],data[5],data[6]])
        
    # return pprint(telkomsel_data)
    return jsonify({"data":newdatalist}) 


@app.route('/sentimentanalyst',methods=['GET'])
def sentimentAnalyst():
     tableTweet = TweetSentiment.query.all()
     for data in tableTweet:
        analysis = TextBlob(clean_tweet(data.english))
        if analysis.sentiment.polarity > 0:
            new_task = TweetSentiment(date=data.date,username=data.username,tweet = data.tweet,clean_html=data.clean_html,clean_mention=data.clean_mention,english=data.english,sentimet_analyst="positif",polarity=data.polarity )
        elif analysis.sentiment.polarity == 0:
            new_task = TweetSentiment(date=data.date,username=data.username,tweet = data.tweet,clean_html=data.clean_html,clean_mention=data.clean_mention,english=data.english,sentimet_analyst="positif",polarity=data.polarity )
        else:
            new_task = TweetSentiment(date=data.date,username=data.username,tweet = data.tweet,clean_html=data.clean_html,clean_mention=data.clean_mention,english=data.english,sentimet_analyst="positif",polarity=data.polarity )
        db.session.add(new_task)
        db.session.commit()
        db.session.close()
       
       
if __name__ == "__main__":
    app.run(debug=True)


def clean_tweet(tweet):
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())