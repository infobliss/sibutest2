# -*- coding: utf-8 -*-
# !/usr/bin/python
from libraries.infobox_templates import photograph_template, art_photo_template
import sys
sys.path.append("..")
import urllib.request
import pywikibot


class GenericGLAM:
    def __init__(self, template_type):
        self.template_type = template_type
        print("GenericGLAM __init__() called with " + template_type)

    def license_checker(self):
        '''
        Function to check the license of a given image

        returns False if the license is not a compatible one
        else return True
        '''
        return False

    def get_thumbnail(self):
        '''
        Function to get a thumbnail for the image.

        returns a thumbnail_url
        returns None by default
        '''
        return None

    def upload_file(self, file_location, description, filename, username, glam_name):
        '''
        Given a description, file_location and filename this function uploads the file at the file location
        using the description using the filename given as filename on Commons.
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

            print('Bot was run.')

    def fill_template(self, parameters):
        print('fill_template inside GenricGLAM invoked, username=' + parameters['username'])     
        '''fill the template based on the values provided by the derived GLAM class'''
        if self.template_type == 'Photograph':
            # Consider that default template is photograph template
            wikitext = photograph_template.format(**parameters)
            # To be displayed to the user for editing
        else:
            wikitext = art_photo_template.format(**parameters)

        # upload the file if the permission is ok
        print('Outside license is ' + parameters['license'])
        try:
            if parameters['license']:
                wikitext += '== {{int:license-header}} ==\n' + parameters['glam_name'] + '\n' + parameters['license'] + '\n\n'
                wikitext += parameters['category_text']
                self.upload_file(parameters['file_location'], wikitext, parameters['filename'], parameters['username'], parameters['glam_name'])
                print('upload_file() called from GenericGLAM')
        except Exception as e:
            print(e)
        return parameters['filename']
