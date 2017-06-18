import re
import json
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2


def load_from_url(url):
    '''
    function which loads and parses the json from the database url
    '''
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

def main(priref, categories=[]):
    database_url = priref_to_url(priref)
    data = load_from_url(database_url)
    print(data['adlibJSON']['recordList']['record'])

main('http://hdl.handle.net/11259/collection.23524', 'Foto')