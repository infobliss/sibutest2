''' generic library functions '''
import re

#urllib works different in python 2 and 3 try catch to get the correct one
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

import json
import unidecode

def load_json_from_url(url):
    #Function to load the json from url and get the parsed json
    try:
        jstring=urllib2.urlopen(url).read()
    except:
        return 1, ""
    parsed_json = json.loads(jstring)
    return 0, parsed_json


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

