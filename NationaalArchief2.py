#!/usr/bin/python
# -*- coding: utf-8  -*-
import sys
import json
sys.path.append("..")
import pywikibot
from pywikibot.specialbots import UploadRobot #stated to be unresolved, but works fine
from xml.dom import minidom
#from urllib2 import urlopen
#To make Python 2 code work in Python 3:
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
import re
from unidecode import unidecode
from config_copy import consumer_key, consumer_secret

def photographers_dict(photographerName):
    #Function to return a cleaned up name from a known photographer
    photographersAnefo={'Zeylemaker, Co / Anefo': 'Co Zeylemaker',
                   'Wisman, Bram / Anefo': 'Bram Wisman',
                   'Winterbergen / Anefo': 'Winterbergen',
                   'Winterbergen, […] / Anefo / Anefo': 'Winterbergen', #klopt
                   'Walta, Winfried / Anefo': 'Winfried Walta', #klopt
                   'Vollebregt, Sjakkelien / Anefo': 'Sjakkelien Vollebregt',
                   'Voets, Jan / Anefo': 'Jan Voets',
                   'Verhoeff, Bert / Anefo': 'Bert Verhoeff‎', #klopt
                   'Suyk, Koen / Anefo': 'Koen Suyk',
                   'Steinmeier, Hans / Anefo': 'Hans Steinmeier',
                   'Snikkers, […] / Anefo / Anefo': 'Snikkers', #klopt
                   'Snikkers / Anefo / Anefo': 'Snikkers',
                   'Smulders, Jean / Anefo': 'Jean Smulders',
                   'Sagers, Harry / Anefo': 'Harry Sagers',
                   'Rossem, Wim van / Anefo': 'Wim van Rossem', #klopt
                   'Renes, Dick / Anefo': 'Dick Renes',
                   'Raucamp, Koos / Anefo': 'Koos Raucamp',
                   'Punt, […] / Anefo': 'Punt', #klopt
                   'Punt / Anefo': 'Punt',
                   'Presser, Sem / Anefo': 'Sem Presser',
                   'Pot, Harry / Anefo': 'Harry Pot‎',
                   'Poll, Willem van de / Anefo': 'Willem van de Poll',
                   'Peters, Hans / Anefo': 'Hans Peters', #klopt
                   'Pereira, Fernando / Anefo': 'Fernando Pereira',
                   'Noske, Daan / Anefo': 'Daan Noske',
                   'Noske, J.D. / Anefo': 'Daan Noske', #klopt
                   'Nijs, Jack de / Anefo': 'Jack de Nijs',
                   'Nijs, Jac. de / Anefo': 'Jack de Nijs', #klopt
                   'Molendijk, Bart / Anefo': 'Bart Molendijk',
                   'Mieremet, Rob / Anefo': 'Rob Mieremet', #klopt
                   'Merk, Ben / Anefo': 'Ben Merk',
                   'Lindeboom, Henk / Anefo': 'Henk Lindeboom',
                   'Kroon, Ron / Anefo': 'Ron Kroon', #klopt
                   'Koch, Eric / Anefo': 'Eric Koch',
                   'Jongerhuis‎, Pieter / Anefo': 'Pieter Jongerhuis‎',
                   'Haren Noman, Theo van / Anefo': 'Theo van Haren Noman',
                   'Ham, Piet van der / Anefo': 'Piet van der Ham‎',
                   'Gerrits, Roland / Anefo': 'Roland Gerrits',
                   'Gelderen, Hugo van / Anefo': 'Hugo van Gelderen',
                   'Evers, Joost / Anefo': 'Joost Evers', #klopt
                   'Duinen, van / Anefo': 'van Duinen',
                   'Duinen, […] van / Anefo': 'van Duinen', #klopt
                   'Dijk, Hans van / Anefo': 'Hans van Dijk',
                   'Croes, Rob / Anefo': 'Rob Croes',
                   'Croes, Rob C. / Anefo': 'Rob Croes', #klopt
                   'Consenheim, Wim / Anefo': 'Wim Consenheim',
                   'Buiten, Klaas van / Anefo': 'Klaas van Buiten',
                   'Broers, F.N. / Anefo': 'F.N. Broers',
                   'Brinkman, Dave / Anefo': 'Dave Brinkman',
                   'Breijer, Charles / Anefo': 'Charles Breijer',
                   'Bogaerts, Rob / Anefo': 'Rob Bogaerts', #klopt
                   'Bilsen, Joop van / Anefo': 'Joop van Bilsen', #klopt
                   'Behrens, Herbert / Anefo': 'Herbert Behrens',
                   'Antonisse, Marcel / Anefo': 'Marcel Antonisse',
                   'Andriesse, Emmy / Anefo': 'Emmy Andriesse'
                   }
    photographersNotAnefo={'Harry Pot': 'Harry Pot‎',
                   'Poll, Willem van de': 'Willem van de Poll'}


    if photographerName in photographersAnefo.keys():
        return True, photographersAnefo[photographerName], True
    elif photographerName in photographersNotAnefo.keys():
        return True, photographersNotAnefo[photographerName], False
    else:
        return False, None, False


def load_from_url(url, categories, nocat=True, uploading=False):
    #The function with the metadata mapping,
    try:
        jstring=urllib2.urlopen(url).read()
    except:
        return 1
    parsed_j = json.loads(jstring.decode())    #not using decode() throws TypeError
    
    articletext='== {{int:filedesc}} ==\n{{Photograph\n |photographer       = '

    #processing to add the photographer    
    creator=parsed_j["doc"]["Vervaardiger"][0]
    if creator=='[onbekend]' or creator=='Onbekend' or creator=='Fotograaf Onbekend':
        articletext+='{{unknown}}'
        hasPhotographerInDict=False
    elif creator=='Fotograaf Onbekend / Anefo':
        articletext+='{{unknown}} (Anefo)'
        hasPhotographerInDict=False
    elif creator=='Fotograaf Onbekend / DLC':
        articletext+='{{unknown}} (Fotocollectie Dienst voor Legercontacten Indonesië)'
        hasPhotographerInDict=False
    else:
        hasPhotographerInDict, photographerName, isAnefo=photographers_dict(creator)
        if hasPhotographerInDict:
            articletext+=photographerName
        else:
            articletext+=str(creator)
        if isAnefo:
            articletext+=' (Anefo)'
    articletext+='\n |title              = {{nl|'
    
    #processing to add the title
    title=parsed_j["doc"]["Titel"]
    #check if the title is empty
    if not title:
        title='zonder titel'
    articletext+=title
    articletext+='}}\n |description        = {{nl|'
    
    #processing to add the description
    description=parsed_j["doc"]["Inhoud"]
    if not description:
        description=title
    articletext+=description + '}}\n |depicted people    = '
    articletext+='\n |depicted place     =\n |date               = '
    #processing to add the date
    date=parsed_j["doc"]["Inhoudsdatering"]
    articletext+=date + '\n |medium             = {{nl|'
    #processing to add the medium
    medium=parsed_j["doc"]["Materiaalsoort"][0]
    articletext+=medium
    #processing to add the department
    department=parsed_j["doc"]["Serie_Collectie"][0]
    reportagename=parsed_j["doc"]["Reportage_Serienaam"][0] 
    articletext+='}}\n |dimensions         =\n |institution        = Nationaal Archief\n |department         = ' + department
    if reportagename !='[ onbekend ]':
        articletext+=', ' + reportagename
    articletext+='\n |references         =\n |object history     =\n |exhibition history =\n |credit line        = '
    articletext+= '' #add creditline +
    articletext+= '\n |inscriptions       =\n |notes              =\n |accession number   = '
    #processing to add the archive inventory number and the file number
    archiefinventaris=parsed_j["doc"]["Nummer_toegang"]
    identifier=parsed_j["doc"]["Bestanddeelnummer"][0]
    articletext+=archiefinventaris + ' (archive inventory number), ' + identifier + ' (file number)\n |source             = '
    #processing to add the collectionname, UUID and file id
    collectionname=department
    UUID=parsed_j["doc"]["id"]
    articletext+= 'Nationaal Archief, ' + collectionname + ', {{Nationaal Archief-source|UUID=' + UUID + '|file_share_id='+ identifier +'}}\n |permission         = '
    isInPD = parsed_j["doc"]["auteursrechten_voorwaarde_Public_Domain"]
    isCC_BY = parsed_j["doc"]["auteursrechten_voorwaarde_CC_BY"]
    isCC_BY_SA = parsed_j["doc"]["auteursrechten_voorwaarde_CC_BY_SA"]
    if isInPD==True:
        permission= 'Public Domain'
        license='{{PD-old}}'

    elif isCC_BY==True:
        permission='CC BY 4.0'
        license='{{cc-by-4.0}}'

    elif isCC_BY_SA==True:
        permission='CC BY SA 4.0'
        license='{{cc-by-sa-4.0}}' 
  
    else:
        permission=''    
        license=''
   
    if permission:
        articletext+=permission + '\n |other_versions     =\n }}\n\n== {{int:license-header}} ==\n{{Nationaal Archief}}\n' + license + '\n\n'
    if nocat:
        articletext+='[[Category:Images from the Nationaal Archief needing categories]]\n'

    if hasPhotographerInDict:
        articletext+='[[Category:Photographs by ' + photographerName + ']]\n'
    for category in categories:
        articletext+='[[Category:' + category + ']]\n'

    images=parsed_j["doc"]["images"]
    
    #extract the key	
    [(key, URLvalues)] = images.items()

    gotimage=False
    for image in URLvalues:
        if '10000x10000' in image["url"] and not gotimage:
            gotimage=True
            image_url=image["url"]

    if len(title)>85:
        #cut off the description if it's longer than 85 tokens at a space around 85.
        filetitle=title[:90]
        cutposition= filetitle.rfind(' ')
        if(cutposition>20):
            filetitle=re.sub('[:/#\[\]\{\}<>\|_]', '', unidecode(filetitle[:cutposition]))
    else:
        filetitle=re.sub('[:/#\[\]\{\}<>\|_;\?]', '', unidecode(title))
    articletitle=filetitle + ' - Nationaal Archief - ' + identifier + '.jpg'
    print ('Permission: '+permission)
    if uploading and permission:
        upload_file(image_url, articletext, articletitle)

    return 0
    #pprint(parsed_j)

    #collection=file.getElementsByTagName("dc:isPartOf")

def upload_file(file_location, description, filename):
    '''
    Given a description, file_location and filename this function uploads the file at the file location using the
    description using the filename given as filename on Commons.
    '''
    print ('inside upload_file()')
    urls=[file_location]
    bot = UploadRobot(urls, description=description, useFilename=filename, keepFilename=True, verifyDescription=False, aborts=True) #, uploadByUrl=True
    print ('Bot was defined.')
    bot.run()
    print ('Bot was run.')


def main(uuid, category, username, a, b):
	
    print('main() NA2 begins')
    
    #consumer_key, consumer_secret are obtained from the config_copy file now	
    print('Configuring pywikibot...')
    pywikibot.config.authenticate['commons.wikimedia.org'] = (consumer_key, consumer_secret, a, b)
    pywikibot.config.usernames['commons']['commons'] = username
    pywikibot.Site('commons', 'commons', user=username).login()
    #The user will provide a valid URL and categories.
    sendurl = 'http://www.gahetna.nl/beeldbank-api/zoek/'+ uuid
    print ('Inside main of NA2')
#    req = urlopen(sendurl)
#   print 'content-type is \n'
#   print req.headers['content-type']

    #categories=['Draughts Dutch Championship'] #categories to be added to the images
    nocat=False #true if the categories above are not sufficient, false if they are sufficient
    categories=[category]
    isFine = load_from_url(sendurl, categories, nocat, uploading=True)


    return isFine

if __name__ == "__main__":
    main()
