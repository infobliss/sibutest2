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


def json_to_wikitemplate(data):
    parameters=wikitemplates.get_art_photo_parameters()
    print(data)
    if 'acquisition.date' in data:
        parameters['object_history'] = parse_acquisition(data['acquisition.date'][0], data['acquisition.method'][0])
    if 'credit_line' in data:
        parameters['credit_line'] = '{{nl|' + data['credit_line'][0] + '}}'




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

main('http://hdl.handle.net/11259/collection.1524', 'Foto')