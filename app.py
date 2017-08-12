import flask
import mwoauth
import os
import yaml
from requests_oauthlib import OAuth1
import pywikibot
from glamFullList import listOfGlams
from glams.NationaalArchiefGLAM import NationaalArchiefGLAM
from glams.AmsterdamMuseumGLAM import AmsterdamMuseumGLAM
from libraries.gen_lib import upload_file

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
    pywikibot.config.authenticate['commons.wikimedia.org'] = (
        app.config['CONSUMER_KEY'],
        app.config['CONSUMER_SECRET'],
        flask.session['access_token_key'],
        flask.session['access_token_secret'])
    pywikibot.config.usernames['commons']['commons'] = username
    pywikibot.Site('commons', 'commons', user=username).login()
    glam_list = listOfGlams
    glam1 = flask.request.form['glam_name']
    searchstring = flask.request.form['searchstring']
    id = flask.request.form['uuid']
    category1 = flask.request.form['categories']
    categories = [category1]
    if not (searchstring or id):
        return flask.render_template('index.html', username=username)
    elif not searchstring:      # if searchstring is empty
        f = flask.request.form
        for key in f.keys():
            if 'category' in key:
                categories.append(flask.request.form[key])

    # instantiate a proper GLAM class object which in turn instantiates
    # a GenericGLAM class object to form the wikitext
        for glam in glam_list:
            if glam['name'] == glam1:
                obj = glam['class'](id)
                if not obj == None:
                    wiki_filename, wikitext, image_url = obj.generate_image_information(categories)
                    upload_file(image_url, wikitext, wiki_filename, username, glam1)
                    return flask.render_template('results.html', glam_name = glam1, uuid = id, filename = wiki_filename)
                else:
                    return flask.render_template('error.html', imageId=id)
                break

    else:
        # store the categories in the session to be accessed in /multiUpload
        if categories:
            flask.session['categories'] = categories
        # obtain the thumbs without instantiating any objects
        for glam in glam_list:
            if glam['name'] == glam1:
                ids = glam['class'].search_to_identifiers(searchstring)
                image_list = []
                for id in ids:
                    image_loc = glam['class'].get_thumbnail(id)
                    image_list.append(image_loc)
                prefix = glam['urlPrefix']
                return flask.render_template('image_gallery.html', glam_name = glam['name'], uuid_list = ids,
                 image_list = image_list, prefix = prefix)


@app.route('/multiUpload', methods=['POST'])
def multiUpload():
    glam_list = listOfGlams
    glam_name = flask.request.args.get('glam', None)
    categories = flask.session.get('categories')
    username = flask.session.get('username', None)
    f = flask.request.form
    ids = f.getlist('selected')
    wiki_filename_list = []
    for glam in glam_list:
        if glam['name'] == glam_name:
            for identifier in ids:
                obj = glam['class'](identifier)
                if not obj == None:
                    wiki_filename, wikitext, image_url = obj.generate_image_information()
                    upload_file(image_url, wikitext, wiki_filename, username, glam_name)
    return flask.render_template('results.html', username = username, filenames = wiki_filename_list)


@app.route('/oauth-callback')
def oauth_callback():
    """OAuth handshake callback."""

    if 'request_token' not in flask.session:
        flask.flash(u'OAuth callback failed. Are cookies disabled?')
        return flask.redirect(flask.url_for('index'))

    try:
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
    # return flask.redirect(flask.url_for('index'))


@app.route('/help_page')
def help_page():
    """Show the user a help page."""
    return flask.render_template('help.html')

@app.route('/batch')
def batch_upload():
    """Show the user a help page."""
    return flask.render_template('batch.html')

@app.route('/tempo')
def under_construction():
    """Show the user a help page."""
    return flask.render_template('todo.html')


@app.route('/logout')
def logout():
    """Log the user out by clearing their session."""
    flask.session.clear()
    return flask.redirect(flask.url_for('index'))
