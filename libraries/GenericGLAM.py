# -*- coding: utf-8 -*-
# !/usr/bin/python
from libraries.infobox_templates import photograph_template, art_photo_template
import sys
sys.path.append("..")
import urllib.request
import pywikibot


class GenericGLAM:
    name = ''
    brief_desc = ''
    url_prefix = ''
    home_url = ''
    sample_url = ''
    sample_id = ''

    def __init__(self, template_type):
        self.template_type = template_type

    def generate_image_information(self, categories=[]):
        """
        Main function to generate all the image information for an upload.
        Categories (as specified by uploader can be send) to be added to the article text
        The function returns: image_url, filepage_title and filepage_wikitext
        returns None by default
        """
        return None

    def license_checker(self):
        '''
        Function to check the license of a given image

        returns False if the license is not a compatible one
        else return True
        '''
        return False

    @classmethod    
    def get_thumbnail(cls, id):
        '''
        A classmethod to get a thumbnail for the image with id.
        returns a thumbnail_url string
        returns None by default
        '''
        return None

    @classmethod
    def search_to_identifiers(cls, searchterm, no_of_files=100):        
        """
        A classmethod to obtain the identifiers of images from a given search string
        Takes the search string as input
        Returns a list of identifiers of the images found as a search result
        returns None by default
        """
        return None
