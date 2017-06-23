import flask
import logging
import mwoauth
import os
import yaml
from requests_oauthlib import OAuth1
from NationaalArchief2 import main
from glamFullList import listOfGlams

#consumer_token = mwoauth.ConsumerToken(app.config['CONSUMER_KEY'], app.config['CONSUMER_SECRET'])

app = flask.Flask(__name__)

# Load configuration from YAML file
__dir__ = os.path.dirname(__file__)
app.config.update(
    yaml.safe_load(open(os.path.join(__dir__, 'config.yaml'))))

consumer_token = mwoauth.ConsumerToken(app.config['CONSUMER_KEY'], app.config['CONSUMER_SECRET'])

@app.route('/')
def index():
    greeting = app.config['GREETING']
    username = flask.session.get('username', None)
    return flask.render_template(
        'index.html', username=username, greeting=greeting)

@app.route('/login')
def login():
    print ("Consumer Key is %s " %app.config['CONSUMER_KEY'])
    print ("Consumer Secret is %s " %app.config['CONSUMER_SECRET'])
    consumer_token = mwoauth.ConsumerToken(app.config['CONSUMER_KEY'], app.config['CONSUMER_SECRET'])
    try:
        redirect, request_token = mwoauth.initiate(
            app.config['OAUTH_MWURI'], consumer_token)
    except Exception:
        app.logger.exception('mwoauth.initiate failed')
        return flask.redirect(flask.url_for('index'))
    else:
        flask.session['request_token'] = dict(zip(
            request_token._fields, request_token))
        return flask.redirect(redirect)

@app.route('/result', methods=['POST'])
def receiveData():
   # if request.method == 'POST':
    username = flask.session.get('username', None) 
    glam1 = flask.request.form['glam_name']
    id = flask.request.form['uuid']
    category1 = flask.request.form['categories']
    categories = [category1]
    f = flask.request.form
    for key in f.keys():
        if 'category' in key:
            categories.append(flask.request.form[key]) 
            print("Multiple categories exist. Appended.")  
    glam_list = listOfGlams
    
    try:
        for glam in glam_list: 
            if glam['name'] == glam1:
    	        break
    except:
        return "GLAM Not Found in our list"

    auth = OAuth1(client_key=consumer_token.key, client_secret=consumer_token.secret, resource_owner_key=flask.session['access_token_key'], resource_owner_secret=flask.session['access_token_secret'])
    #upload the image
    value, filename = main(id, categories, username, flask.session['access_token_key'], flask.session['access_token_secret'])
    print('passes main')
    if value == 0:
        return flask.render_template('results.html', glam_name=glam1, uuid=id, filename=filename)
    else:
        #returnString = 'Image: ' + id + ' not found.'
        return flask.render_template('error.html', imageId=id)
    #return returnString
# show the glam form
#return flask.render_template('glam_form.html', username=username)


@app.route('/oauth-callback')
def oauth_callback():
    """OAuth handshake callback."""
     
    if 'request_token' not in flask.session:
        flask.flash(u'OAuth callback failed. Are cookies disabled?')
        return flask.redirect(flask.url_for('index'))

    #consumer_token = mwoauth.ConsumerToken(app.config['CONSUMER_KEY'], app.config['CONSUMER_SECRET'])

    try:
        print ('URL query string is '+str(flask.request.query_string))
        access_token = mwoauth.complete(
            app.config['OAUTH_MWURI'],
            consumer_token,
            mwoauth.RequestToken(**flask.session['request_token']),
            flask.request.query_string)
        flask.session['access_token_key'], flask.session['access_token_secret'] = access_token.key, access_token.secret
        identity = mwoauth.identify(app.config['OAUTH_MWURI'], consumer_token, access_token)
    except Exception as e:
        app.logger.exception('Infobliss: '+str(e))

    else:
        flask.session['access_token'] = dict(zip(
            access_token._fields, access_token))
        flask.session['username'] = identity['username']
        username = flask.session.get('username', None)
    
    return flask.render_template('index.html', username=username) 
    #return flask.redirect(flask.url_for('index'))

@app.route('/help_page')
def help_page():
    """Show the user a help page."""
    return flask.render_template('help.html')

@app.route('/tempo')
def under_construction():
    """Show the user a help page."""
    return flask.render_template('todo.html')

@app.route('/logout')
def logout():
    """Log the user out by clearing their session."""
    flask.session.clear()
    return flask.redirect(flask.url_for('index'))

