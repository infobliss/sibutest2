# -*- coding: utf-8 -*-

from GenericGLAM import GenericGLAM
import json
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2


def photographers_dict(photographerName):
    '''Function to return a cleaned up name from a known photographer'''
    photographersAnefo = {
        'Zeylemaker, Co / Anefo': 'Co Zeylemaker',
        'Wisman, Bram / Anefo': 'Bram Wisman',
        'Winterbergen / Anefo': 'Winterbergen',
        'Winterbergen, […] / Anefo / Anefo': 'Winterbergen',
        'Walta, Winfried / Anefo': 'Winfried Walta',
        'Vollebregt, Sjakkelien / Anefo': 'Sjakkelien Vollebregt',
        'Voets, Jan / Anefo': 'Jan Voets',
        'Verhoeff, Bert / Anefo': 'Bert Verhoeff‎',
        'Suyk, Koen / Anefo': 'Koen Suyk',
        'Steinmeier, Hans / Anefo': 'Hans Steinmeier',
        'Snikkers, […] / Anefo / Anefo': 'Snikkers',
        'Snikkers / Anefo / Anefo': 'Snikkers',
        'Smulders, Jean / Anefo': 'Jean Smulders',
        'Sagers, Harry / Anefo': 'Harry Sagers',
        'Rossem, Wim van / Anefo': 'Wim van Rossem',
        'Renes, Dick / Anefo': 'Dick Renes',
        'Raucamp, Koos / Anefo': 'Koos Raucamp',
        'Punt, […] / Anefo': 'Punt',
        'Punt / Anefo': 'Punt',
        'Presser, Sem / Anefo': 'Sem Presser',
        'Pot, Harry / Anefo': 'Harry Pot‎',
        'Poll, Willem van de / Anefo': 'Willem van de Poll',
        'Peters, Hans / Anefo': 'Hans Peters',
        'Pereira, Fernando / Anefo': 'Fernando Pereira',
        'Noske, Daan / Anefo': 'Daan Noske',
        'Noske, J.D. / Anefo': 'Daan Noske',
        'Nijs, Jack de / Anefo': 'Jack de Nijs',
        'Nijs, Jac. de / Anefo': 'Jack de Nijs',
        'Molendijk, Bart / Anefo': 'Bart Molendijk',
        'Mieremet, Rob / Anefo': 'Rob Mieremet',
        'Merk, Ben / Anefo': 'Ben Merk',
        'Lindeboom, Henk / Anefo': 'Henk Lindeboom',
        'Kroon, Ron / Anefo': 'Ron Kroon',
        'Koch, Eric / Anefo': 'Eric Koch',
        'Jongerhuis‎, Pieter / Anefo': 'Pieter Jongerhuis‎',
        'Haren Noman, Theo van / Anefo': 'Theo van Haren Noman',
        'Ham, Piet van der / Anefo': 'Piet van der Ham‎',
        'Gerrits, Roland / Anefo': 'Roland Gerrits',
        'Gelderen, Hugo van / Anefo': 'Hugo van Gelderen',
        'Evers, Joost / Anefo': 'Joost Evers',
        'Duinen, van / Anefo': 'van Duinen',
        'Duinen, […] van / Anefo': 'van Duinen',
        'Dijk, Hans van / Anefo': 'Hans van Dijk',
        'Croes, Rob / Anefo': 'Rob Croes',
        'Croes, Rob C. / Anefo': 'Rob Croes',
        'Consenheim, Wim / Anefo': 'Wim Consenheim',
        'Buiten, Klaas van / Anefo': 'Klaas van Buiten',
        'Broers, F.N. / Anefo': 'F.N. Broers',
        'Brinkman, Dave / Anefo': 'Dave Brinkman',
        'Breijer, Charles / Anefo': 'Charles Breijer',
        'Bogaerts, Rob / Anefo': 'Rob Bogaerts',
        'Bilsen, Joop van / Anefo': 'Joop van Bilsen',
        'Behrens, Herbert / Anefo': 'Herbert Behrens',
        'Antonisse, Marcel / Anefo': 'Marcel Antonisse',
        'Andriesse, Emmy / Anefo': 'Emmy Andriesse'
    }
    photographersNotAnefo = {
        'Harry Pot': 'Harry Pot‎',
        'Poll, Willem van de': 'Willem van de Poll'
    }

    if photographerName in photographersAnefo:
        return True, photographersAnefo[photographerName], True
    elif photographerName in photographersNotAnefo:
        return True, photographersNotAnefo[photographerName], False
    else:
        return False, None, False


class NationaalArchief(GenericGLAM):

    glam_name = 'Nationaal Archief'

    def choose_correct_template(url):
        parsed_j = json.loads(urllib2.urlopen(url).read())

        '''TODO: do some processing to choose the right template,
               return 1 if unable to decide'''
        return 'Photograph', parsed_j

    def fill_template(self, url, category):
        categories = [category]
        try:
            right_template, parsed_j = self.choose_correct_template(url)
        except Exception:
            print('Incorrect URL given')

        # perform the glam specific metadata mapping here
        # and form the dictionary
        diction = {
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

        if creator in ['[onbekend]', 'Onbekend', 'Fotograaf Onbekend']:
            photographer = '{{unknown}}'
            hasPhotographerInDict = False
        elif creator == 'Fotograaf Onbekend / Anefo':
            photographer = '{{unknown}} (Anefo)'
            hasPhotographerInDict = False
        elif creator == 'Fotograaf Onbekend / DLC':
            photographer = '''
                           '{{unknown}} (Fotocollectie Dienst voor
                            Legercontacten Indonesië)'
                           '''
            hasPhotographerInDict = False
        else:
            hasPhotographerInDict, photographerName, isAnefo = photographers_dict(creator)
            if hasPhotographerInDict:
                photographer = photographerName
            else:
                photographer = str(creator)
            if isAnefo:
                photographer += ' (Anefo)'
        diction['photographer'] = photographer
        # check if the title is empty
        diction['title'] = parsed_j['doc']['Titel'] or 'zonder titel'
        # TODO: Add the language tag by guessing the language
        # of the title and description
        diction['description'] = parsed_j['doc']['Inhoud'] or parsed_j["doc"]["Titel"]
        diction['date'] = parsed_j['doc']['Inhoudsdatering']
        diction['medium'] = parsed_j['doc']['Materiaalsoort'][0]
        diction['institution'] = 'Nationaal Archief'
        diction['department'] = parsed_j['doc']['Serie_Collectie'][0]
        dict['accession_number'] = (
            '{} (archive inventory number), '
            '{} (file number)'
        ).format(
            parsed_j['doc']['Nummer_toegang'],
            parsed_j['doc']['Bestanddeelnummer'][0]
        )
        diction['source'] = (
            'Nationaal Archief, '
            '{} {{Nationaal Archief-source|UUID = '
            '{} |file_share_id = '
            '{} }}'
            ).format(
                parsed_j['doc']['Serie_Collectie'][0],
                parsed_j['doc']['id'],
                parsed_j['doc']['Bestanddeelnummer'][0]
            )

        if parsed_j['doc']['auteursrechten_voorwaarde_Public_Domain']:
            permission = 'Public Domain'
            license = '{{CC-0}}'

        elif parsed_j['doc']['auteursrechten_voorwaarde_CC_BY']:
            permission = 'CC BY 4.0'
            license = '{{cc-by-4.0}}'

        elif parsed_j['doc']['auteursrechten_voorwaarde_CC_BY_SA']:
            permission = 'CC BY SA 4.0'
            license = '{{cc-by-sa-4.0}}'

        else:
            permission = ''
            license = ''
        diction['license'] = license
        diction['permission'] = permission
        diction['glam_name'] = 'Nationaal Archief'

        if categories[0]:
            category_text = '''
                             [[Category:Images from the Nationaal Archief
                             needing categories]]\n
                            '''

        elif hasPhotographerInDict:
            category_text = '[[Category:Photographs by ' \
                + photographerName + ']]\n'
            for category in categories:
                category_text += '[[Category:' + category + ']]\n'
        diction['category_text'] = category_text
        # call the fill_template method of the GenericGLAM
        return super(NationaalArchief, self).fill_template(diction, right_template)
