# -*- coding: utf-8 -*-
"""
    Github Example
    --------------

    Shows how to authorize users with Github.
"""
import os
import json
from flask import Flask, render_template, request, g, session, flash, \
     redirect, url_for, abort
from flaskext.github import GithubAuth

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# setup flask
app = Flask(__name__)
app.config.update(
    DATABASE_URI = 'sqlite:////tmp/flask-github.db',
    SECRET_KEY = 'development key',
    DEBUG = True
)

# setup flask-github
with open(os.path.join(os.getcwd(), 'example/config.json'), 'r') as f:
    config_data = f.read()
config = json.loads(config_data)
github = GithubAuth(
    client_id=config['client_id'],
    client_secret=config['client_secret'],
    session_key='user_id'
)

# setup sqlalchemy
engine = create_engine(app.config['DATABASE_URI'])
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    Base.metadata.create_all(bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(200))
    github_access_token = Column(Integer)

    def __init__(self, github_access_token):
        self.github_access_token = github_access_token

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])

@app.after_request
def after_request(response):
    db_session.remove()
    return response

@app.route('/')
def index():
    return 'Hello!'

@github.access_token_getter
def token_getter():
    user = g.user
    if user is not None:
        return user.github_access_token

@app.route('/oauth/callback')
@github.authorized_handler
def authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        return redirect(next_url)

    token = resp['access_token']
    user = User.query.filter_by(github_access_token=token).first()
    if user is None:
        user = User(token)
        db_session.add(user)
    user.github_access_token = token
    db_session.commit()

    session['user_id'] = user.id

    return 'Success'

@app.route('/login')
def login():
    if session.get('user_id', None) is None:
        return github.authorize(callback_url=url_for('authorized'))
    else:
        return 'Already logged in'

@app.route('/orgs/<name>')
def orgs(name):
    if github.has_org_access(name):
        return 'Heck yeah he does!'
    else:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
