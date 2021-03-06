''' generic library functions '''
import re

# urllib works different in python 2 and 3 try catch to get the correct one
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

import urllib.request
import pywikibot
import json
from unidecode import unidecode


def load_from_url(url):
    """
    Function which loads and parses the json from the database url.
    Input is url with json, output is dictionary with the structure from the json
    """
    # TODO: Make this code work in both python2 and 3, now it works locally in 3
    # and the py2 code is in nationaalarchief
    try:
        return json.loads(urllib2.urlopen(url).read().decode())
    except Exception as e:
        raise ValueError(str(e))


def file_title_generator(glam_filetitle, image_id, image_ext, glam_name='',
                        max_rawlength=90, order=['title', 'glam', 'id'],
                        separator=' - '):
    '''
    Function to generate a standard title for the image to be uploaded

    glam_filetitle: the name the file is given at the glam.
    image_id: an identifier for the image
    image_ext: the extension of the image
    glam_name: the name of the glam (preferably an abbreviation)
    max_rawlength: the maximum length of the glam_filetitle which will be used,
        an attempt is made to crop at a nice location.
    order: the order in which the parameters
        (glam_filetitle=0, image_id=1, glam_name=2) will be used
    separator: character to separate the title elements with
        (including spaces if you want those)
    '''
    if len(glam_filetitle) > (max_rawlength-5):
        # cut off the description if it's longer than 85 tokens
        # at a space around 85.
        worktitle = glam_filetitle[:max_rawlength]
        cutposition = worktitle.rfind(' ')
        if cutposition > 20:
            worktitle = re.sub('[:/#\[\]\{\}<>\|_]', '', unidecode(worktitle[:cutposition]))
    else:
        worktitle = re.sub('[:/#\[\]\{\}<>\|_;\?]', '', unidecode(glam_filetitle))
    elements = {
        'title': worktitle, 
        'id' : image_id, 
        'glam' : glam_name
    }
    filetitle = separator.join(elements[elmt] for elmt in order)
    filetitle += '.' + image_ext
    return filetitle


def page_generator(infobox, categories, wikilicense='', license_in_infobox=False):
    '''
    This function expects a filled infobox, a license-template and a set of 
    categories and forms this into a wikitext image_description.
    if License_in_infobox=True then the license is in the infobox and no
    license is givens
    '''
    pagetemplate = '''\
=={{{{int:filedesc}}}}==
{infobox}{wikilicense}
{categories}'''
    license_template = '''

=={{{{int:license-header}}}}==
{wikilicense}'''
    parsed_categories = ''
    for category in categories:
        parsed_categories += '\n[[Category:{category}]]'.format(category=category)
    if license_in_infobox:
        license_text = ''
    else:
        license_text = license_template.format(wikilicense=wikilicense)
    return pagetemplate.format(
        infobox=infobox, wikilicense=license_text, categories=parsed_categories)


def upload_file(file_location, description, filename, username, glam_name):
    '''
    Given a description, file_location and filename this function uploads
    the file at the file locationusing the description as wikitext and
    using the filename given as filename on Commons.
    '''
    print(username)
    local_filepath, headers = urllib.request.urlretrieve(file_location)
    wiki_file_location = 'File:' + filename
    site = pywikibot.Site('commons', 'commons', user=username)
    page = pywikibot.FilePage(site, wiki_file_location)
    if page.exists():
        raise ValueError('duplicate at https://commons.wikimedia.org/wiki/{loc}'.format(
            loc=wiki_file_location))
    else:
        try:
            if not site.upload(
                page, source_filename=local_filepath, comment='Uploaded from ' + glam_name +
                " with glam2commons tool", text=description
            ):
                raise ValueError("Upload failed")
        except pywikibot.data.api.APIError:
            # recheck
            site.loadpageinfo(page)
            if not page.exists():
                raise


def get_glam_class(glam_list, glam_name):
    '''
    Function to return a class corresponding to the glam name given
    glam_list is a list of GLAM classes
    glam_name is a string variable that is the name of the glam chosen
    '''
    for glam in glam_list:
        if glam.name == glam_name:
            return glam
    raise ValueError("GLAM not found")

def get_glam_names(glam_list):
    '''
    Function to return the names of the GLAMs supported
    glam_list is a list of GLAM classes
    '''
    glam_names = []
    for glam in glam_list:
        glam_names.append(glam.name)
    return glam_names

def get_glam_info(glam_list):
    '''
    Function to return the names of the GLAMs supported
    glam_list is a list of GLAM classes
    '''
    glam_names = []
    glam_homes = [] 
    glam_desc = []
    glam_samples = []
    glam_ids = []
    for glam in glam_list:
        glam_names.append(glam.name)
        glam_homes.append(glam.home_url)
        glam_desc.append(glam.brief_desc)
        glam_samples.append(glam.sample_url)
        glam_ids.append(glam.sample_id)
    return glam_names, glam_homes, glam_desc, glam_samples, glam_ids