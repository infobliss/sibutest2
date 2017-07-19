# -*- coding: utf-8 -*-
# !/usr/bin/python
from infobox_templates import photograph_template, art_photo_template
import sys
sys.path.append("..")
import pywikibot
from pywikibot.specialbots import UploadRobot


class GenericGLAM:
    def __init__(self, template_type):
        self.template_type = template_type
        print("GenericGLAM __init__() called ")

    def upload_file(file_location, description, filename):
        '''
        Given a description, file_location and filename this function uploads the file at the file location
        using the description using the filename given as filename on Commons.
        '''
        print('inside upload_file()')
        urls = [file_location]
        bot = UploadRobot(urls, description=description, useFilename=filename, keepFilename=True, verifyDescription=False, aborts=True) # , uploadByUrl=True
        print('Bot was defined.')
        bot.run()
        print('Bot was run.')

    def fill_template(self, parameters):
        '''fill the template based on the values provided by the derived GLAM class'''
        if self.template_type == 'Photograph':
            # Consider that default template is photograph template
            wikitext = photograph_template.format(**parameters)
            # To be displayed to the user for editing
        else:
            wikitext = art_photo_template.format(**parameters)
        # return wikitext
        # upload the file if the permission is ok
        if parameters['permission']:
            self.upload_file(parameters['file_location'], wikitext, parameters['filename'])
            return parameters['filename']
