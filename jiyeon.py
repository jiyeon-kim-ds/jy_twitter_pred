from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import tweepy 
import os
from tweepy import OAuthHandler, API
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///twitter.sqlite3'
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
    # user_id = db.Column(db.BigInteger, db.ForeignKey('user.id')) # 외래키
    # user = db.relationship("User", backref=db.backref('tweets', lazy=True))

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


def get_data():
    return User.query.all()

@app.route('/')
def index():
    return 'hello twitter'


@app.route('/users')
def users():
    data = get_data()
    return render_template('index.html, data=data')

    




@app.route('/<user_name>/add')
def add_user(user_name=None):
    user = api.get_user(screen_name=user_name)
    new_user = User(id=user.id, username=user_name, full_name=user.name, followers_count=user.followers_count, location=user.location)
    db.session.add(new_user)
    db.session.commit()
    return 'user added'
        

@app.route('/<user_name>/get')
def get_twits(user_name=None):
    public_tweets = api.user_timeline(user_name, count=30)
    for tweet in public_tweets:
        print(tweet.text)

@app.route('/<user_name>/delete')
def delete_user(user_name=None):
    user = api.get_user(screen_name=user_name)
    old_user = User(username=user_name, full_name=user.name, followers_count=user.followers_count, location=user.location)
    db.session.delete(old_user)
    db.session.commit()
    return 'user deleted'


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)