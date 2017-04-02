#!/usr/bin/python
# -*- coding: utf-8  -*-
import sys
sys.path.append("..")
from pywikibot.specialbots import UploadRobot #stated to be unresolved, but works fine
import pandas as pd
from xml.dom import minidom
from urllib2 import urlopen
import re
from unidecode import unidecode

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
    xmlstring=urlopen(url).read()
    xmldoc = minidom.parseString(xmlstring)
    itemlist = xmldoc.getElementsByTagName('channel')
    for s in itemlist :
        filelist=s.getElementsByTagName("item")
        for file in filelist:
            articletext='== {{int:filedesc}} ==\n{{Photograph\n |photographer       = '
            collection=file.getElementsByTagName("dc:isPartOf")
            creator=file.getElementsByTagName("dc:creator")[0].firstChild.data
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
                    articletext+=creator
                if isAnefo:
                    articletext+=' (Anefo)'
            articletext+='\n |title              = {{nl|'
            if file.getElementsByTagName("title")[0].firstChild:
                title=file.getElementsByTagName("title")[0].firstChild.data
            else:
                title='zonder titel'
            articletext+=title
            articletext+='}}\n |description        = {{nl|'
            if file.getElementsByTagName("description")[0].firstChild:
                description=file.getElementsByTagName("description")[0].firstChild.data
            else:
                description=title
            articletext+=description + '}}\n |depicted people    = '
            subjects=file.getElementsByTagName("dc:subject")
            for sub in subjects:
                if sub.getAttribute('rdf:about')=='http://www.gahetna.nl/dc/subject/Persoons_instellingsnaam':
                    articletext+=sub.firstChild.data + ' '
            articletext+='\n |depicted place     =\n |date               = '
            date=file.getElementsByTagName("dc:date")[0].firstChild.data
            articletext+=date + '\n |medium             = {{nl|'
            type=file.getElementsByTagName("dc:type")
            for ty in type:
                medium=ty.firstChild.data

            collectionname=collection[1].firstChild.data
            reportagename=collection[2].firstChild.data
            articletext+=medium
            articletext+='}}\n |dimensions         =\n |institution        = Nationaal Archief\n |department         = ' +collection[1].firstChild.data
            if reportagename !='[ onbekend ]':
                articletext+=', ' + reportagename
            articletext+='\n |references         =\n |object history     =\n |exhibition history =\n |credit line        = '
            articletext+= '' #add creditline +
            articletext+= '\n |inscriptions       =\n |notes              =\n |accession number   = '
            identifiers=file.getElementsByTagName("dc:identifier")
            for id in identifiers:
                identifier=id.firstChild.data
            for partof in collection:
                a=re.match('([0-9\.]+)', partof.firstChild.data)
                if a!=None:
                    archiefinventaris=a.group(0)
            articletext+=archiefinventaris + ' (archive inventory number), ' + identifier + ' (file number)\n |source             = '
            link=file.getElementsByTagName("link")[0].firstChild.data
            UUID=re.search('([\d\w\-]*)$', link).group(0)
            articletext+= 'Nationaal Archief, ' + collectionname + ', {{Nationaal Archief-source|UUID=' + UUID + '|file_share_id='+ identifier +'}}\n |permission         = '
            r=file.getElementsByTagName("right")
            for r2 in r:
                if r2.getAttribute('name')=='Public Domain':
                    if r2.firstChild.data=='TRUE':
                        permission= 'Public Domain'
                        license='{{PD-old}}'

                elif r2.getAttribute('name')=='CC BY':
                    if r2.firstChild.data=='TRUE':
                        permission='CC BY 4.0'
                        license='{{cc-by-4.0}}'

                elif r2.getAttribute('name')=='CC BY SA':
                    if r2.firstChild.data=='TRUE':
                        permission='CC BY SA 4.0'
                        license='{{cc-by-sa-4.0}}'
            articletext+=permission + '\n |other_versions     =\n }}\n\n== {{int:license-header}} ==\n{{Nationaal Archief}}\n' + license + '\n\n'
            if nocat:
                articletext+='[[Category:Images from the Nationaal Archief needing categories]]\n'

            if hasPhotographerInDict:
                articletext+='[[Category:Photographs by ' + photographerName + ']]\n'
            for category in categories:
                articletext+='[[Category:' + category + ']]\n'


            images=file.getElementsByTagName("ese:isShownBy")
            gotimage=False
            for image in images:
                if '10000x10000' in image.firstChild.data and not gotimage:
                    print(image.firstChild.data)
                    gotimage=True
                    image_url=image.firstChild.data

            if len(title)>85:
                #cut off the description if it's longer than 85 tokens at a space around 85.
                filetitle=title[:90]
                cutposition= filetitle.rfind(' ')
                if(cutposition>20):
                   filetitle=re.sub('[:/#\[\]\{\}<>\|_]', '', unidecode(filetitle[:cutposition]))
            else:
                filetitle=re.sub('[:/#\[\]\{\}<>\|_;\?]', '', unidecode(title))
            articletitle=filetitle + ' - Nationaal Archief - ' + identifier + '.jpg'
            print(articletitle.encode('utf-8'))
            print(articletext.encode('utf-8'))
            print(image_url.encode('utf-8'))
            if uploading:
                upload_file(image_url, articletext, articletitle)


def upload_file(file_location, description, filename):
    '''
    Given a description, file_location and filename this function uploads the file at the file location using the
    description using the filename given as filename on Commons.
    '''
    urls=[file_location]
    bot = UploadRobot(urls, description=description, useFilename=filename, keepFilename=True, verifyDescription=False, aborts=True) #, uploadByUrl=True
    bot.run()

def main(searchstring):
    #main function: the search-string and categories have to be manually set for each upload then the file can be run as a whole.
    #searchstring='	nederlandse%20kampioenschappen%20biljart' # %20 for space
    searchstring = searchstring.replace(" ", "%20")
    print(searchstring)
    categories=['Draughts Dutch Championship'] #categories to be added to the images
    nocat=False #true if the categories above are not sufficient, false if they are sufficient
    nrOfFiles=0
    url='http://www.gahetna.nl/beeldbank-api/opensearch/?q='+ searchstring +'&count=1&startIndex=1'
    xmlstring=urlopen(url).read()
    #print(xmlstring)
    xmldoc = minidom.parseString(xmlstring)
    itemlist = xmldoc.getElementsByTagName('channel')
    for s in itemlist :
        nrOfFiles=int(s.getElementsByTagName("opensearch:totalResults")[0].firstChild.data)
        print 'nr 	of files' + str(nrOfFiles)
    nrOfHundredFiles=int(nrOfFiles/100)
    for i in range(8,10):
        sendurl='http://www.gahetna.nl/beeldbank-api/opensearch/?q='+ searchstring +'&count=2&startIndex='+ str(i)
        print(sendurl)
        load_from_url(sendurl, categories, nocat, uploading=True)

    return nrOfFiles

if __name__ == "__main__":
    main()
