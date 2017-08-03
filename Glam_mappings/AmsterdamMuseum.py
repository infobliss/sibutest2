import re
import json
import datetime

#urllib works different in python 2 and 3 try catch to get the correct one
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

import libraries.infobox_templates as wikitemplates


def load_from_url(url):
    '''
    Function which loads and parses the json from the database url.
    Input is url with json, output is dictionary with the structure from the json
    '''
    #TODO: Make this code work in both python2 and 3, now it works locally in 3 and the py2 code is in nationaalarchief
    jstring=urllib2.urlopen(url).read().decode('utf-8')
    parsed_json = json.loads(jstring)
    return parsed_json


def priref_to_url(priref):
    '''
    Function which parses different priref-formats (identifiers) to an url in the database.
    Either a priref or (correct) url with  priref should be given.
    Examples: "5782" and "http://hdl.handle.net/11259/collection.5782"
    A link to the database json location will be returned.
    '''
    priref = str(priref)
    is_number = re.match('\d+$', priref)
    if not is_number is None:  # number in the form of 12345
        return 'http://amdata.adlibsoft.com/wwwopac.ashx?database=AMcollect&search=priref={priref}&output=json'.format(priref=priref)
    is_url = re.match('http://hdl\.handle\.net/11259/collection\.(\d+)$', priref)
    if not is_url is None:  # URL in the form of http://hdl.handle.net/11259/collection.12345
        priref = re.sub('http://hdl\.handle\.net/11259/collection\.(\d+)$', '\g<1>', priref)
        return 'http://amdata.adlibsoft.com/wwwopac.ashx?database=AMcollect&search=priref={priref}&output=json'.format(priref=priref)
    #TODO: better handling of no results
    return 'No url found'


def parse_acquisition(date, method):
    '''
    Function to parse the different types of acquisition into the ProvenanceEvent wikitemplate.
    The date of acquisition and the method are given.
    A complete list of possible values for the method within the Amsterdam Museum data can be found at:
    http://amdata.adlibsoft.com/wwwopac.ashx?command=facets&database=AMcollect&search=all&facet=acquisition.method&limit=50&output=json
    Only the most common values (75+ occurances) have been mapped here
    '''
    types = {'schenking': 'gift',
             'legaat': 'bequest',
             'aankoop': 'purchase',
             'bruikleen': 'loan',
             'onbekend': 'in collection',
             'overdracht': 'acquisition',
             'aangetroffen': 'discovery',
             'oud stadsbezit': 'transfer',
             'bruikleen / schenking': 'loan',
             'opdracht museum': 'commission',
             'onteigening': 'nationalization',
             'ruil': 'exchange',
             'bodemvondst': 'excavation'}
    acquisition_type = 'in collection' #default if not known
    if date == '0000' and method == 'onbekend':
        return ''
    if date == '0000':
        date = '{{unknown}}'
    if method in types:
        acquisition_type = types[method]
    return '{{{{ProvenanceEvent|time={date}|type={type}|newowner=Amsterdam Museum|oldowner=}}}}'\
        .format(date=date, type=acquisition_type)


def parse_dimension(dimensions):
    '''
    Function to parse the different types of dimensions into a size template.
    Unit (cm, gram, etc.) type of dimension and the value are given.
    A complete list of possible values for the type within the Amsterdam Museum data can be found at:
    http://amdata.adlibsoft.com/wwwopac.ashx?command=facets&database=AMcollect&search=all&facet=dimension.type&limit=50&output=json
    '''
    #TODO: correct mapping for multiple sizes (twice hoogte and breedte) hoogte a, etc.
    #TODO: What to do with weight (gewicht) in grams, size doesn't support this?
    types = {'hoogte': 'height',
             'breedte': 'width',
             'lengte': 'length',
             'diepte': 'depth',
             'diameter': 'diameter',
             'dikte': 'thickness'}
    size_str = '{{Size'
    unit = dimensions[0]['dimension.unit'][0]
    size_str += '|' + unit
    for dimension in dimensions:
        if dimension['dimension.type'][0] in types:
            size_str += '|' + types[dimension['dimension.type'][0]] + '|' + dimension['dimension.value'][0]
        else:
            size_str += '|' + dimension['dimension.value'][0]
    size_str += '}}'
    return size_str


def parse_artist(makers):
    '''
    first check whether an artist is given (if not return unknown-template).
    If an artist is known the date of death + birth and the role of the creator are appended behind their name.
    Possible improvements: reverse first and last name with regex; parse the dates; translate the roles into correct
    template; check the creator against existing creator templates.
    '''
    number_of_makers = len(makers)
    if number_of_makers == 1 and makers[0]['creator'][0] == 'onbekend':
        return '{{unknown|author}}'
    makertext= ''
    first = True
    for maker in makers:
        if not first:
            makertext += ', '
        makertext += maker['creator'][0]
        if maker['creator.date_of_birth'][0] != '' and maker['creator.date_of_death'][0] != '':
            makertext += (' (' + maker['creator.date_of_birth'][0] + ' - ' + maker['creator.date_of_death'][0] + ')')
        if maker['creator.qualifier'][0] != '':
            makertext += (' ({{nl|' + maker['creator.qualifier'][0] + '}})')
        if maker['creator.role'][0] != '':
            makertext += (' ({{nl|' + maker['creator.role'][0] + '}})')
        first=False
    return makertext


def parse_references(documentation):
    '''
    Parse each reference into a cite book template (assumption is made that it mostly are books/articles).
    '''
    referencestext = ''
    for document in documentation:
        referencestext+='{{Cite book|author=' + document['documentation.author'][0]\
                        + '|title=' + document['documentation.title'][0]  \
                        + '|year=' + document['documentation.sortyear'][0]  \
                        + '|page=' + document['documentation.page_reference'][0]  \
                        + '|chapter=' + document['documentation.title.article'][0] \
                        + '}}'
    return referencestext


def parse_date(start, end):
    '''
    if start and end date are the same return one date, otherwise return the dates with an '-' in between.
    Often the date is a year range. It's unclear from this data whether it was made somewhere within this time span or
    during the whole time span.
    '''
    if start == end:
        return start
    else:
        return start + '-' + end


def parse_reproduction(reproductions):
    '''
    The images in the Amsterdam Museum adlib data are not represented per image but per object.
    An object can have multiple images.
    The current procedure is to select the best image (highest resolution) as often when there are multiple images they
    show similar parts of the object.
    in order of quality the images are looked through. Then the data from the first hit is returned.
    photographer, photo date and the image location are returned.
    There is also data on the image format, reference and reference_lref (and reproduction type) these are not returned.
    '''
    quality_order = ['high-end scan', 'digitale opname', 'scan', 'low-res scan', ''] #high to low quality
    for quality in quality_order:
        for reproduction in reproductions:
            if reproduction['reproduction.type'][0] == quality or quality == '': # if we're at the '' (empty) quality then just go for any reproduction.
                photographer = reproduction['reproduction.creator'][0]
                photo_date = reproduction['reproduction.date'][0]
                #replace the internal url for an external url per https://www.amsterdammuseum.nl/open-data
                photo_url = 'http://ahm.adlibsoft.com/ahmimages/' + reproduction['reproduction.identifier_URL'][0][27:]
                return photographer, photo_date, photo_url


def artwork_license(data):
    '''
    This function tries to determine the correct (PD-old) license based on the authors date of death and date the work
    was created.
    '''
    currentyear = datetime.datetime.now().year
    known_author = False #check whether there are any known authors, initialize as false

    if 'maker' in data:
        most_recent_death = -99999 #everything should be larger
        for author in data['maker']:
            if len(author['creator.date_of_death'][0]) > 4: #some cases are '', for a year we need 4 chars.
                death = int(author['creator.date_of_death'][0][:4])
                if death > most_recent_death:
                    most_recent_death = death
            if(author['creator'] != 'onbekend' and author['creator'] != ''):
                known_author = True #not anonymous
        if most_recent_death == -99999:
            None #No date given so go out of the loop (mostly anonymous case) to check date of creation
        elif most_recent_death < 1923:
            return '{{{{PD-old-auto-1923|deathyear={year}}}}}'.format(year=most_recent_death)
        elif most_recent_death < 1926:
            return '{{{{PD-old-auto-1996|deathyear={year}}}}}'.format(year=most_recent_death)
        elif most_recent_death < (currentyear-70):
            return '{{PD-old-70}}'
        else:
            #author died less than 70 year ago, no pd-old applicable
            return False #can't determine a valid license, needs a check after upload.

    if not known_author:
        if 'production.date.end' in data:
            date = data['production.date.end'][0]
            if date < 1923:
                return '{{PD-anon-1923}}'
            elif date < (currentyear-70):
                return '{{PD-anon-70-EU}}'
    if known_author:
        if 'production.date.end' in data:
            date = data['production.date.end'][0]
            if date < (currentyear-150):
                #if the work was created more than 150 years ago we assume the author died more than 70 years ago.
                return '{{PD-old-70}}'
    return False #can't determine a valid license, needs a check after upload.


def json_to_wikitemplate(data):
    '''
    This function receives a dictionary which is the resulting parsed json from a given object in the Amsterdam Museum
    database e.g. http://amdata.adlibsoft.com/wwwopac.ashx?database=AMcollect&search=priref=346&output=json
    The function then get's the parameters for the art photo infobox template and maps the values from the glams data
    into these parameters.
    '''
    parameters=wikitemplates.art_photo_parameters
    categories = ['Images from the Amsterdam Museum']
    if 'copyright' in data:
        if data['copyright'][0] == 'Public Domain':
            parameters['photo_license'] = '{{PD-because|Released into the Public Domain by the copyright holder, the Amsterdam Museum}}'
            license = artwork_license(data)
            if license:
                parameters['artwork_license'] = license
            else:
                parameters['artwork_license'] = '{{PD-because|Released into the Public Domain by the copyright holder, the Amsterdam Museum}}'
                categories.append('Images from the Amsterdam Museum needing license check')
        else:
            return False #not under a free license
    else:
        return False #not under a free license
    if 'reproduction' in data:
        parameters['photographer'], parameters['photo_date'], image_url = parse_reproduction(data['reproduction'])
    else:
        return False #does not have any images so return false
    if 'acquisition.date' in data:
        parameters['object_history'] = parse_acquisition(data['acquisition.date'][0], data['acquisition.method'][0])
    if 'credit_line' in data:
        parameters['credit_line'] = '{{nl|' + data['credit_line'][0] + '}}'
    if 'dimension' in data:
        parameters['dimensions'] = parse_dimension(data['dimension'])
    if 'title' in data:
        parameters['title'] = data['title'][0]
    if 'maker' in data:
        parameters['artist'] = parse_artist(data['maker'])
    if 'documentation' in data:
        parameters['references'] = parse_references(data['documentation'])
    if 'material' in data:
        parameters['method'] = '{{nl|materiaal: ' + ', '.join(data['material']) + '}}'
    if 'object_name' in data:
        parameters['method'] += '{{nl|type object: ' + ', '.join(data['object_name']) + '}}'
    if 'technique' in data:
        parameters['method'] += '{{nl|techniek: ' + ', '.join(data['technique']) + '}}'
    if 'object_number' in data:
        parameters['accession_number'] = data['object_number'][0]
    if 'priref' in data:
        parameters['source'] = 'Collection of the Amsterdam Museum under: ['+ data['persistent_ID'][0] + ' ' + data['priref'][0] + ']'
    if 'production.date.end' in data and 'production.date.start' in data:
        parameters['date'] = parse_date(data['production.date.start'][0], data['production.date.end'][0])
    parameters['institution'] = '{{Institution:Amsterdam Museum}}'

    print(parameters)
    #TODO: parse descriptions
    #TODO: check license and parse template, maybe make some GLAM specific templates on commons.
    title = create_title(parameters)
    return parameters, image_url, title, categories


def main(priref, categories=[]):
    database_url = priref_to_url(priref)
    data = load_from_url(database_url)
    if 'recordList' in data['adlibJSON']:
        if 'record' in data['adlibJSON']['recordList']:
            if 'copyright' in data['adlibJSON']['recordList']['record'][0]:
                infobox_parameters, image_url, title, categories =\
                    json_to_wikitemplate(data['adlibJSON']['recordList']['record'][0])
            else:
                return False, 'no copyright information for the specified file'
        else:
            return False, 'no object found (record)'
    else:
        return False, 'no object found (recordlist)'

main('http://hdl.handle.net/11259/collection.5782', 'Foto')