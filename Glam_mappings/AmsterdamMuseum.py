import re
import json
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

import libraries.infobox_templates as wikitemplates


def load_from_url(url):
    '''
    function which loads and parses the json from the database url
    '''
    #TODO: Make this code work in both python2 and 3, now it works locally in 3 and the py2 code is in nationaalarchief
    jstring=urllib2.urlopen(url).read().decode('utf-8')
    parsed_json = json.loads(jstring)
    return parsed_json


def priref_to_url(priref):
    '''
    function which parses different priref-formats (identifiers) to an url in the database
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
    function to parse the different types of acquisition into a provenanceevent template
    '''
    types = {'schenking': 'gift', 'overdracht': 'acquisition', 'legaat': 'inheritance', 'aankoop': 'purchase'
        , 'bruikleen': 'loan'}
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
    function to parse the different types of dimensions into a size template
    '''
    types = {'hoogte': 'height', 'breedte': 'width', 'lengte': 'length', 'diepte': 'depth'
        , 'diameter': 'diameter', 'dikte': 'thickness'}
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
    if start == end:
        return start
    else:
        return start + '-' + end

def json_to_wikitemplate(data):
    parameters=wikitemplates.get_art_photo_parameters()
    print(data)
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
    #TODO: parse descriptions
    #TODO: how to handle duplicate images
    #TODO: parse photograph info
    #TODO: check license and parse template, maybe make some GLAM specific templates on commons.

def main(priref, categories=[]):
    database_url = priref_to_url(priref)
    data = load_from_url(database_url)
    if 'recordList' in data['adlibJSON']:
        if 'record' in data['adlibJSON']['recordList']:
            if 'copyright' in data['adlibJSON']['recordList']['record'][0]:
                json_to_wikitemplate(data['adlibJSON']['recordList']['record'][0])
                print('object found')
            else:
                print('no copyright information')
        else:
            print('no object found (record)')
    else:
        print('no object found (recordlist)')

main('http://hdl.handle.net/11259/collection.5782', 'Foto')