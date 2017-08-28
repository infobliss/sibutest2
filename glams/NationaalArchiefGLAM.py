# -*- coding: utf-8 -*-
# !/usr/bin/python

import json
import re
import sys
sys.path.append("..")
from unidecode import unidecode
from xml.dom import minidom
import json
import re
import libraries.utils as library
import libraries.infobox_templates as wikitemplates
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

from glams import register_glam
from libraries.GenericGLAM import GenericGLAM
from libraries.infobox_templates import photograph_parameters
from libraries.utils import load_from_url


@register_glam
class NationaalArchiefGLAM(GenericGLAM):
    name = 'Nationaal Archief'
    brief_desc = 'The national archive of the Netherlands, located in The Hague'
    home_url = 'http://www.gahetna.nl'
    url_prefix = 'http://proxy.handle.net/10648/'
    sample_url = 'http://proxy.handle.net/10648/aa704164-d0b4-102d-bcf8-003048976d84'
    sample_id = 'aa704164-d0b4-102d-bcf8-003048976d84'

    def __init__(self, id):
        """
        initializer which should receive an image identifier or url (unique identifier for an object/image)
        """
        self.uuid = self.extractUUID(id)
        self.url = 'http://www.gahetna.nl/beeldbank-api/zoek/{uuid}'.format(uuid=self.uuid)
        try:
            self.data = load_from_url(self.url)
        except Exception:
            raise ValueError("Invalid image id " + id) 
        self.parameters=wikitemplates.photograph_parameters
        if not self.license_checker():
            raise ValueError("Invalid license for the image") # no valid license
        self.image_url = None
        self.categories = []
        self.categories.append('Images from Nationaal Archief')
        print("categories init")
        self.title = None

    def extractUUID(self, id):
        """
        Function to extract the identifier from a given URL
        id : the identifier or the URL for an image (e.g., http://proxy.handle.net/10648/a9946ea0-d0b4-102d-bcf8-003048976d84)
        returns the identifier of the image (e.g., a9946ea0-d0b4-102d-bcf8-003048976d84)
        """
        uuid = id
        if uuid.startswith('http://proxy.handle.net/10648/'):
            i = -1
            while not uuid[i] == '/':
                i = i-1
            uuid = uuid[i+1:len(uuid)]        
        return uuid

    def generate_image_information(self, categories=[]):
        """
        Main function to generate all the image information for an upload.
        Categories (as specified by uploader can be send) to be added to the article text
        The function returns: image_url, filepage_title and filepage_wikitext
        """
        if categories:
            for category in categories:
                self.categories.append(category)
        else:
            self.categories.append('Images from Nationaal Archief needing categories')
        if not self.get_infobox_parameters():
            return False
        image_id = self.data['doc']['Bestanddeelnummer'][0]
        infobox = wikitemplates.photograph_template.format(**self.parameters)
        wikitext = library.page_generator(infobox, self.categories, wikilicense=self.parameters['license'])
        self.title = library.file_title_generator(self.parameters['title'], image_id, 'jpg', 'NA', 
                                                    order=['title', 'glam', 'id'])
        return self.title, wikitext, self.image_url

    @classmethod
    def get_thumbnail(cls, id):
        """
        This is a classmethod so that it can be called without creating an object
        Retrieves the smallest avaiable thumbnail for the current object
        It can not be given a resolution since all sizes are not available in NA
        """
        url = 'http://www.gahetna.nl/beeldbank-api/zoek/{uuid}'.format(uuid=id)
        data = load_from_url(url)
        images = data["doc"]["images"]
        # take the first image only if more than one images are given by the identifier
        image_key = next(iter(images))
        print(image_key)
        URLvalues = images[image_key]
        
        res_min = 20000
        for image in URLvalues:
            res = re.findall(r'(\d+)x\d+/', image["url"])
            if(int(res[0]) < res_min):
                res_min = int(res[0])
                thumb_url = image["url"]
        return thumb_url

    def license_checker(self):
        """
        Function to find out the license info
        returns True if the license is permissible for upload to Commons
        """
        if self.data['doc']['auteursrechten_voorwaarde_Public_Domain']:
            self.parameters['license'] = '{{cc-0}}'
            return True
        elif self.data['doc']['auteursrechten_voorwaarde_CC_BY']:
            self.parameters['license'] = '{{cc-by-4.0}}'
            return True
        elif self.data['doc']['auteursrechten_voorwaarde_CC_BY_SA']:
            self.parameters['license'] = '{{cc-by-sa-4.0}}'
            return True
        else:
            return False
        return False
        
    def get_infobox_parameters(self):
        """
        The function that performs the metadata-mapping from the parsed json already stored at self.data
        It maps the values from the glams data into the photograph parameters.
        """

        creator = self.data['doc']['Vervaardiger'][0]

        if 'onbekend' in creator.lower():
            photographer = '{{unknown}}'
            if creator.endswith(' / Anefo'):
                photographer += ' (Anefo)'
            elif creator.endswith(' / DLC'):
                photographer += ('(Fotocollectie Dienst voor '
                                 'Legercontacten Indonesië)')
        else:
            photographer = re.sub(r'( / Anefo)+$', '', creator)
            isAnefo = photographer != creator
            photographer = re.sub(r'(, )?\[…\](?(1)$| ?)', '', photographer)
            photographer = re.sub(
                r'^([^,]+), ([^,]+)$', r'\2 \1', photographer)
            if isAnefo:
                photographer += ' (Anefo)'

        self.parameters['photographer'] = photographer

        # check if the title is empty
        self.parameters['title'] = self.data['doc']['Titel'] or 'zonder titel'
        # TODO: Add the language tag by guessing the language
        # of the title and description
        self.parameters['description'] = self.data['doc']['Inhoud'] or self.parameters['title']

        self.parameters['date'] = self.data['doc']['Inhoudsdatering']
        self.parameters['medium'] = self.data['doc']['Materiaalsoort'][0]
        self.parameters['institution'] = 'Nationaal Archief'
        self.parameters['department'] = self.data['doc']['Serie_Collectie'][0]

        self.parameters['accession_number'] = (
            '{} (archive inventory number), '
            '{} (file number)'
        ).format(
            self.data['doc']['Nummer_toegang'],
            self.data['doc']['Bestanddeelnummer'][0]
        )
        self.parameters['source'] = (
            'Nationaal Archief, {} '
            '{{{{Nationaal Archief-source|UUID = {} '
            '|file_share_id = {} }}}}'
        ).format(
            self.data['doc']['Serie_Collectie'][0],
            self.data['doc']['id'],
            self.data['doc']['Bestanddeelnummer'][0]
        )

        if (self.data['doc']['auteursrechten_voorwaarde_Public_Domain'] or
            'CC0' in self.data['doc']['auteursrechten_auteursrechthebbende']):
            self.parameters['license'] = '{{CC-0}}'
        elif self.data['doc']['auteursrechten_voorwaarde_CC_BY']:
            self.parameters['license'] = '{{cc-by-4.0}}'
        elif self.data['doc']['auteursrechten_voorwaarde_CC_BY_SA']:
            self.parameters['license'] = '{{cc-by-sa-4.0}}'
        else:
            self.parameters['license'] = ''

        self.parameters['glam_name'] = 'Nationaal Archief'
        
        # Obtain the location of the largest resolution image for upload
        images = self.data["doc"]["images"]
        [(key, URLvalues)] = images.items()
        res_max = 0
        for image in URLvalues:
            res = re.findall(r'(\d+)x\d+/', image["url"])
            if(int(res[0]) > res_max):
                res_min = int(res[0])
                image_url = image["url"]
        self.image_url = image_url
        self.parameters['file_location'] = image_url
        return True

    @classmethod
    def search_to_identifiers(cls, searchterm, no_of_files=100):        
        """
        A classmethod to obtain the identifiers of images from a given search string
        Takes the search string as input
        Returns a list of identifiers of the images found as a search result
        """
        ids = []
        searchterm = searchterm.replace(" ", "+")
        url = 'http://www.gahetna.nl/beeldbank-api/zoek/?q={search}&count={count}'.format(search=searchterm, count=no_of_files)
        parsed_json = load_from_url(url)
        docs = parsed_json['response']['docs']
        for doc in docs:
            ids.append(doc['id'])
        return ids