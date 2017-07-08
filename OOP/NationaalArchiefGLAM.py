# -*- coding: utf-8 -*-

from libraries import *
from GenericGLAM import GenericGLAM
import json
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2


def load_json_from_url(url):
    '''Function to load the json from url and get the parsed json'''
    try:
        jstring = urllib2.urlopen(url).read()
    except:
        return 1, ""
    parsed_json = json.loads(jstring)
    return 0, parsed_json


def photographers_dict(photographerName):
    '''Function to return a cleaned up name from a known photographer'''
    photographersAnefo = {'Zeylemaker, Co / Anefo': 'Co Zeylemaker',
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
    photographersNotAnefo = '''
                            {'Harry Pot': 'Harry Pot‎',
                             'Poll, Willem van de': 'Willem van de Poll'}
                            '''

    if photographerName in photographersAnefo.keys():
        return True, photographersAnefo[photographerName], True
    elif photographerName in photographersNotAnefo.keys():
        return True, photographersNotAnefo[photographerName], False
    else:
        return False, None, False


class NationaalArchief(GenericGLAM):

    glam_name = 'Nationaal Archief'
    url = 'http://proxy.handle.net/10648/a9deaf60-d0b4-102d-bcf8-003048976d84'

    def choose_correct_template(url):
        val, parsed_j = load_json_from_url(url)
        if val == 0:
            return 0, ''
        else:
            '''ToDo: do some processing to choose the right template,
               return 1 if unable to decide'''
            return 1, parsed_j

    def fill_template(self, url, category):
        categories = [category]
        right_template, parsed_j = self.choose_correct_template(url)
        if right_template == 0:
            print("Incorrect URL given")
        else:
            '''perform the glam specific metadata mapping here
               and form the dictionary'''
            creator = parsed_j["doc"]["Vervaardiger"][0]

            if creator == '[onbekend]' or creator == 'Onbekend' or creator == 'Fotograaf Onbekend':
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
                    photographer = ' (Anefo)'
            dict['photographer'] = photographer
            title = parsed_j["doc"]["Titel"]
            '''check if the title is empty'''
            if not title:
                dict['title'] = 'zonder titel'
            else:
                dict['title'] = title
            '''ToDo: Add the language tag by guessing the language
               of the title and description'''
            description = parsed_j["doc"]["Inhoud"]
            if not description:
                dict['description'] = title
            else:
                dict['description'] = description
            dict['depicted_people'] = ''
            dict['depicted_place'] = ''
            dict['date'] = parsed_j["doc"]["Inhoudsdatering"]
            dict['medium'] = parsed_j["doc"]["Materiaalsoort"][0]
            dict['dimensions'] = ''
            dict['institution'] = 'Nationaal Archief'
            dict['department'] = parsed_j["doc"]["Serie_Collectie"][0]
            dict['references'] = ''
            dict['object_history'] = ''
            dict['exhibition_history'] = ''
            dict['credit_line'] = ''
            dict['inscriptions'] = ''
            dict['notes'] = ''
            archiefinventaris = parsed_j["doc"]["Nummer_toegang"]
            identifier = parsed_j["doc"]["Bestanddeelnummer"][0]
            dict['accession_number'] = archiefinventaris + \
                ' (archive inventory number), ' \
                + identifier + ' (file number)'
            collectionname = parsed_j["doc"]["Serie_Collectie"][0]
            UUID = parsed_j["doc"]["id"]
            dict['source'] = 'Nationaal Archief, ' + collectionname \
                             + ', {{Nationaal Archief-source|UUID = ' + UUID \
                             + '|file_share_id = ' + identifier
            isInPD = parsed_j["doc"]["auteursrechten_voorwaarde_Public_Domain"]
            isCC_BY = parsed_j["doc"]["auteursrechten_voorwaarde_CC_BY"]
            isCC_BY_SA = parsed_j["doc"]["auteursrechten_voorwaarde_CC_BY_SA"]
            if isInPD is True:
                permission = 'Public Domain'
                license = '{{CC-0}}'

            elif isCC_BY is True:
                permission = 'CC BY 4.0'
                license = '{{cc-by-4.0}}'

            elif isCC_BY_SA is True:
                permission = 'CC BY SA 4.0'
                license = '{{cc-by-sa-4.0}}'

            else:
                permission = ''
                license = ''
        dict['license'] = license
        dict['permission'] = permission
        dict['other_versions'] = ''
        dict['wikidata'] = ''
        dict['camera_coord'] = ''
        dict['glam_name'] = 'Nationaal Archief'

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
        '''call the fill_template method of the GenericGLAM'''
        super(NationaalArchief, self).fill_template(dict, right_template)
