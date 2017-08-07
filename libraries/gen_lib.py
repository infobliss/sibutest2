''' generic library functions '''
import re

#urllib works different in python 2 and 3 try catch to get the correct one
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

import json
from unidecode import unidecode


def load_json_from_url(url):
    #Function to load the json from url and get the parsed json
    try:
        return json.loads(urllib2.urlopen(url).read().decode())
    except Exception as e:
        raise ValueError('Bad URL given ' + e)

def load_from_url(self):
        """
        Function which loads and parses the json from the database url.
        Input is url with json, output is dictionary with the structure from the json
        """
        #TODO: Make this code work in both python2 and 3, now it works locally in 3 and the py2 code is in nationaalarchief
        jstring=urllib2.urlopen(self.url).read().decode('utf-8')
        parsed_json = json.loads(jstring)
        return parsed_json

def file_title_generator(glam_filetitle, image_id, image_ext, glam_name='', max_rawlength=90, order=[0,2,1], separator=' - '):
    '''
    Function to generate a standard title for the image to be uploaded

    glam_filetitle: the name the file is given at the glam.
    image_id: an identifier for the image
    image_ext: the extension of the image
    glam_name: the name of the glam (preferably an abbreviation)
    max_rawlength: the maximum length of the glam_filetitle which will be used,
        an attempt is made to crop at a nice location.
    order: the order in which the parameters (glam_filetitle=0, image_id=1, glam_name=2), will be used
    separator: character to separate the title elements with (including spaces if you want those)
    '''
    if len(glam_filetitle) > (max_rawlength-5):
        #cut off the description if it's longer than 85 tokens at a space around 85.
        worktitle = glam_filetitle[:max_rawlength]
        cutposition = worktitle.rfind(' ')
        if(cutposition>20):	
            worktitle = re.sub('[:/#\[\]\{\}<>\|_]', '', unidecode(worktitle[:cutposition]))
    else:
        worktitle=re.sub('[:/#\[\]\{\}<>\|_;\?]', '', unidecode(glam_filetitle))
    elements = [worktitle, image_id, glam_name]
    filetitle = "{}{}{}{}{}{}{}".format(elements[order[0]], separator, elements[order[1]], separator, elements[order[2]], '.', image_ext)
    
    return filetitle

def page_generator(infobox, categories, wikilicense='', license_in_infobox=False):
    '''
    This function expects a filled infobox, a license-template and a set of categories and forms this into a
    wikitext image_description.
    if License_in_infobox=True than the license is in the infobox and no license is givens
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
        license_text=''
    else:
        license_text = license_template.format(wikilicense=wikilicense)
    return pagetemplate.format(infobox=infobox, wikilicense=license_text,categories=parsed_categories)

def upload_file(file_location, description, filename, username, glam_name):
    '''
    Given a description, file_location and filename this function uploads the file at the file location
    using the description as wikitext and using the filename given as filename on Commons.
    '''
    print('inside upload_file() username=' + username)
    print('file location is ' + file_location)
    local_filepath, headers = urllib.request.urlretrieve(file_location)
    wiki_file_location = 'File:' + filename
    print('Wiki file location and local path are ' + wiki_file_location + local_filepath)
    site = pywikibot.Site('commons', 'commons', user=username)
    page = pywikibot.FilePage(site, wiki_file_location)
    if page.exists():
        print('Exists')
    else:
        try:
            print('Inside try block...')   
            if not site.upload(
                page, source_filename = local_filepath, comment = 'Uploaded from' + glam_name + "with g2c tool", text = description
            ):
                print('Upload failed!')
        except pywikibot.data.api.APIError:
            # recheck
            site.loadpageinfo(page)
            if not page.exists():
                raise    