# -*- coding: utf-8 -*-
# !/usr/bin/python
from OOP.infobox_templates import photograph_template, art_photo_template
import sys
sys.path.append("..")
import urllib.request
import pywikibot
from pywikibot.specialbots import UploadRobot


class GenericGLAM:
    def __init__(self, template_type):
        self.template_type = template_type
        print("GenericGLAM __init__() called ")

    def upload_file(self, file_location, description, filename, username):
        '''
        Given a description, file_location and filename this function uploads the file at the file location
        using the description using the filename given as filename on Commons.
        '''
        print('inside upload_file()')
        print('file location is ' + file_location)
        #urls = [file_location]
        #bot = UploadRobot(urls, description=description, useFilename=filename, keepFilename=True, verifyDescription=False, aborts=True) # , uploadByUrl=True
        local_filepath, headers = urllib.request.urlretrieve(file_location)
        wiki_file_location = 'https://commons.wikimedia.org/wiki/File:' + filename
        print('Wiki file location and local path are ' + wiki_file_location + local_filepath)
        site = pywikibot.Site('commons', 'commons', user=username)
        page = pywikibot.FilePage(site, wiki_file_location)
        if page.exists():
            print('Exists')
        else:
            try:
                print('Inside try block...')   
                if not site.upload(
                    page, source_filename=local_filepath, comment='Uploaded from NA GLAM', text=description
                ):
                    print('Upload failed!')
            except pywikibot.data.api.APIError:
                # recheck
                site.loadpageinfo(page)
                if not page.exists():
                    raise    

            print('Bot was run.')

    def fill_template(self, parameters):
        print('fill_template inside GenricGLAM invoked.')     
 
        '''fill the template based on the values provided by the derived GLAM class'''
        if self.template_type == 'Photograph':
            # Consider that default template is photograph template
            wikitext = photograph_template.format(**parameters)
            # To be displayed to the user for editing
        else:
            wikitext = art_photo_template.format(**parameters)

        # upload the file if the permission is ok
        print('Outside Permission is ' + parameters['permission'])
        if parameters['permission']:
            print('Permission is ' + parameters['permission'])
            self.upload_file(parameters['file_location'], wikitext, parameters['filename'], parameters['username'])
            print('upload_file() called from GenericGLAM')
            return parameters['filename']
