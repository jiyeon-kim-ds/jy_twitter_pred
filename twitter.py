from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import tweepy 
import os
from tweepy import OAuthHandler, API
from dotenv import load_dotenv
from embedding_as_service_client import EmbeddingClient
from sklearn.linear_model import LogisticRegression
import pickle 

load_dotenv()
DATABASE_URI = os.getenv("DATABASE_URI")
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# 환경변수로 넣기
API_KEY = os.getenv("TWITTER_API_KEY")
API_KEY_SECRET = os.getenv("TWITTER_API_KEY_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")


auth = OAuthHandler(API_KEY, API_KEY_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = API(auth)

class User(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    username = db.Column(db.String)
    full_name = db.Column(db.String)
    followers_count = db.Column(db.Integer)
    location = db.Column(db.String)

    def __repr__(self):
        return "< User {} {} >".format(self.id, self.username)


class Tweet(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    text = db.Column(db.String)
    # user_id = db.Column(db.BigInteger)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id')) # 외래키 연결하기..


    def __repr__(self):
        return "< Tweet {} >".format(self.id)

def parse_records(db_records):
    parsed_list = []
    for record in db_records:
        parsed_record = record.__dict__
        print(parsed_record)
        del parsed_record["_sa_instance_state"]
        parsed_list.append(parsed_record)
    return parsed_list



def get_users():
    return User.query.all()


@app.route('/')
def index():
    return 'hello twitter'


@app.route('/users')
def users():
    data = get_users()
    return render_template('index.html, data=data')

    

@app.route('/<user_name>/add')
def add_user(user_name=None):
    # 유저 추가
    user = api.get_user(screen_name=user_name)
    new_user = User(id=user.id, username=user_name, full_name=user.name, followers_count=user.followers_count, location=user.location)
    db.session.add(new_user)
    db.session.commit()
    # 트윗 추가
    tweets = api.user_timeline(screen_name=user_name, count=30)
    for tweet in tweets:
        new_tweet = Tweet(id=tweet.id, text=tweet.text, user_id=tweet.user.id)
        db.session.add(new_tweet)
        db.session.commit()
        
    return 'user added'
        

@app.route('/<user_name>/get')
def get_tweets(user_name=None):
    
    # tweets = api.user_timeline(screen_name=user_name, count=30)
    
    # for tweet in tweets:
    #     new_tweet = Tweet(id=tweet.id, text=tweet.text, user_id=tweet.author.screen_name)
    #     db.session.add(new_tweet)
    #     db.session.commit()
    # result = Tweet.query.with_entities(Tweet.id, Tweet.text, Tweet.user_id)

    # filter가 제대로 안되고 있음.
    # result = Tweet.query.filter(Tweet.user_id == 'user_name') 
    # return render_template('tweets.html', data=result)
    return 'work in progress...'


@app.route('/<user_name>/delete')
def delete_user(user_name=None):
    user = User.query.with_entities(User.id).filter_by(username=user_name).first()
    User.query.filter_by(id = user[0]).delete()
    Tweet.query.filter_by(user_id = user[0]).delete()
    db.session.commit()
    return 'user deleted'


@app.route('/<user_name>/update')
def update_user(user_name=None):

    pass


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)