# -*- coding: utf-8 -*-
# !/usr/bin/python

import json
import re
import sys
sys.path.append("..")
from unidecode import unidecode
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

print("Sys path is " + str(sys.path))
from OOP.GenericGLAM import GenericGLAM


class NationaalArchiefGLAM(GenericGLAM):
    glam_name = 'Nationaal Archief'

    def __init__(self, infobox_type):
        print('hello from NA subclass __init__')
        super(NationaalArchiefGLAM, self).__init__(infobox_type)

    def choose_correct_template(self, url):
        print("Url from choose_correct_template() " + url)
        parsed_j = json.loads(urllib2.urlopen(url).read().decode())

        # For NA Glam 'Photograph' infobox type applies to all the images
        return 'Photograph', parsed_j

    def fill_template(self, uuid, username):
        print('fill_template inside NA_GLAM invoked.')
        # Form the url if (glam + uuid) is given
        url = 'http://www.gahetna.nl/beeldbank-api/zoek/' + uuid
        try:
            infobox_type, parsed_j = self.choose_correct_template(url)
        except Exception:
            raise ValueError('Incorrect URL given')  # FIXME: raise, don't print

        # perform the glam specific metadata mapping here
        # and form the dictionary
        mapping = {
            'depicted_people': '',
            'depicted_place': '',
            'dimensions': '',
            'references': '',
            'object_history': '',
            'exhibition_history': '',
            'credit_line': '',
            'inscriptions': '',
            'notes': '',
            'other_versions': '',
            'wikidata': '',
            'camera_coord': ''
        }

        creator = parsed_j['doc']['Vervaardiger'][0]

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

        mapping['photographer'] = photographer

        # check if the title is empty
        mapping['title'] = parsed_j['doc']['Titel'] or 'zonder titel'
        # TODO: Add the language tag by guessing the language
        # of the title and description
        mapping['description'] = parsed_j['doc']['Inhoud'] or mapping['title']

        mapping['date'] = parsed_j['doc']['Inhoudsdatering']
        mapping['medium'] = parsed_j['doc']['Materiaalsoort'][0]
        mapping['institution'] = 'Nationaal Archief'
        mapping['department'] = parsed_j['doc']['Serie_Collectie'][0]

        mapping['accession_number'] = (
            '{} (archive inventory number), '
            '{} (file number)'
        ).format(
            parsed_j['doc']['Nummer_toegang'],
            parsed_j['doc']['Bestanddeelnummer'][0]
        )
        mapping['source'] = (
            'Nationaal Archief, {} '
            '{{{{Nationaal Archief-source|UUID = {} '
            '|file_share_id = {} }}}}'
        ).format(
            parsed_j['doc']['Serie_Collectie'][0],
            parsed_j['doc']['id'],
            parsed_j['doc']['Bestanddeelnummer'][0]
        )

        if parsed_j['doc']['auteursrechten_voorwaarde_Public_Domain']:
            mapping['permission'] = 'Public Domain'
            mapping['license'] = '{{CC-0}}'
        elif parsed_j['doc']['auteursrechten_voorwaarde_CC_BY']:
            mapping['permission'] = 'CC BY 4.0'
            mapping['license'] = '{{cc-by-4.0}}'
        elif parsed_j['doc']['auteursrechten_voorwaarde_CC_BY_SA']:
            mapping['permission'] = 'CC BY SA 4.0'
            mapping['license'] = '{{cc-by-sa-4.0}}'
        else:
            mapping['permission'] = ''
            mapping['license'] = ''

        mapping['glam_name'] = 'Nationaal Archief'

        # TODO: Solve category redirects?
        categories = ['[[Category:Images from the '
                      'Nationaal Archief needing categories]]']
        if '{{unknown' not in photographer.lower():
            categories.append(
                '[[Category:Photographs by {}]]'.format(photographer))
        mapping['category_text'] = '\n'.join(categories)

        # generate filename and find the image url
        images = parsed_j["doc"]["images"]
        # extract the key
        [(key, URLvalues)] = images.items()

        gotimage = False
        for image in URLvalues:
            if '10000x10000' in image["url"] and not gotimage:
                gotimage = True
                image_url = image["url"]

        if len(mapping['title']) > 85:
            # cut off the description if it's longer than 85 tokens at a space around 85.
            filetitle = mapping['title'][:90]
            cutposition = filetitle.rfind(' ')
            if(cutposition > 20):
                filetitle = re.sub('[:/#\[\]\{\}<>\|_]', '', unidecode(filetitle[:cutposition]))
        else:
            filetitle = re.sub('[:/#\[\]\{\}<>\|_;\?]', '', unidecode(mapping['title']))
        articletitle = (
            '{} - Nationaal Archief - '
            '{}.jpg').format(
                filetitle,
                parsed_j['doc']['Bestanddeelnummer'][0]

            )

        mapping['file_location'] = image_url
        mapping['filename'] = articletitle
        mapping['username'] = username
        # call the fill_template method of the GenericGLAM (later return)
        super(NationaalArchiefGLAM, self).fill_template(mapping)
