import re
import json
import datetime
import sys

# urllib works different in python 2 and 3 try catch to get the correct one
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

sys.path.append("..")
import libraries.infobox_templates as wikitemplates
import libraries.utils as library
from libraries.GenericGLAM import GenericGLAM


class AmsterdamMuseumGLAM(GenericGLAM):
    
    name = 'Amsterdam Museum'
    url_prefix = 'http://hdl.handle.net/11259/collection.'

    def __init__(self, priref):
        """
        initializer which should receive a priref or url with priref (unique identifier for an object/image)
        """
        self.url=self.priref_to_url(priref)
        if not self.url == False:
            #a correctly formatted identifier
            self.data = self.load_from_url()
            if self.parse_data():  # self.parse_data() changes the self.data object if there is data on the object
                # finds data on the object
                if self.license_checker():
                    # valid license
                    self.parameters=wikitemplates.art_photo_parameters
                    self.image_url = None
                    self.categories = []
                    self.categories.append('Images from the Amsterdam Museum')
                    self.title = None
                else:
                    raise ValueError("Invalid license for the image")
            else:
                raise ValueError("No data found on the object")
        else:
            raise ValueError("Invalid image id " + str(priref))


    def generate_image_information(self, categories=[]):
        """
        Main function to generate all the image information for an upload.
        Categories (as specified by uploader can be send) to be added to the article text
        The function returns: image_url, filepage_title and filepage_wikitext
        """

        for category in categories:
            self.categories.append(category)
        if not self.get_infobox_parameters(self.data):
            return False

        infobox = wikitemplates.art_photo_template.format(**self.parameters)
        wikitext = library.page_generator(infobox, self.categories, license_in_infobox=True)
        self.title = library.file_title_generator(self.parameters['title'], self.data['priref'][0], 'jpg',
                                                    'AM', order=['title', 'glam', 'id'])
        return self.title, wikitext, self.image_url

    def priref_to_url(self, priref):
        """
        Function which parses different priref-formats (identifiers) to an url in the database.
        Either a priref or (correct) url with  priref should be given.
        Examples: "5782" and "http://hdl.handle.net/11259/collection.5782"
        A link to the database json location will be returned.
        """
        priref = str(priref)
        is_number = re.match('\d+$', priref)
        if not is_number is None:  # number in the form of 12345
            return 'http://amdata.adlibsoft.com/wwwopac.ashx?database=AMcollect&search=priref={priref}&output=json'.format(priref=priref)
        is_url = re.match('http://hdl\.handle\.net/11259/collection\.(\d+)$', priref)
        if not is_url is None:  # URL in the form of http://hdl.handle.net/11259/collection.12345
            priref = re.sub('http://hdl\.handle\.net/11259/collection\.(\d+)$', '\g<1>', priref)
            return 'http://amdata.adlibsoft.com/wwwopac.ashx?database=AMcollect&search=priref={priref}&output=json'.format(priref=priref)
        # TODO: better handling of no results
        return False

    def load_from_url(self):
        """
        Function which loads and parses the json from the database url.
        Input is url with json, output is dictionary with the structure from the json
        """
        # TODO: Make this code work in both python2 and 3, now it works locally in 3 and the py2 code is in nationaalarchief
        jstring=urllib2.urlopen(self.url).read().decode('utf-8')
        parsed_json = json.loads(jstring)
        return parsed_json

    def parse_data(self):
        """
        validates whether the returned data contains an object/record.
        If this is not the case the object/identifier is not in the (public) database
        """
        if not 'recordList' in self.data['adlibJSON']:
            return False  # no recordlist found (identifier doesn't exist)
        if not 'record' in self.data['adlibJSON']['recordList']:
            return False  # no record found (identifier doesn't exist)
        self.data = self.data['adlibJSON']['recordList']['record'][0]
        return True

    def license_checker(self):
        """
        Checks whether the object has a valid (free) license
        """
        if 'copyright' in self.data:
            if self.data['copyright'][0] in ('Public Domain', 'CC0'):
                return True
            else:
                return False  # not under a free license
        else:
            return False  # not under a free license

    @classmethod
    def get_thumbnail(cls, priref, resolution='150'):
        """
        Retrieves a thumbnail version for the current object
        can also be given a resolution, default is 150x150 pixels
        """
        url = 'http://amdata.adlibsoft.com/wwwopac.ashx?database=AMcollect&search=priref={priref}&output=json'.format(priref=priref)
        data = library.load_from_url(url)
        data = data['adlibJSON']['recordList']['record'][0]
        if 'reproduction' in data:
            _, _, image_url = cls.parse_reproduction_copy(data)
        else:
            return False  # Does not have any images so return false
        image_name= image_url[35:]
        return 'https://am-web.adlibhosting.com/wwwopacx_images/wwwopac.ashx?command=getcontent&server=images&value=' \
               '{image}&width={resolution}&height={resolution}&imageformat=jpg&scalemode=' \
               'fit'.format(image=image_name, resolution=resolution)

    def parse_acquisition(self, date, method):
        """
        Function to parse the different types of acquisition into the ProvenanceEvent wikitemplate.
        The date of acquisition and the method are given.
        A complete list of possible values for the method within the Amsterdam Museum data can be found at:
        http://amdata.adlibsoft.com/wwwopac.ashx?command=facets&database=AMcollect&search=all&facet=acquisition.method&limit=50&output=json
        Only the most common values (75+ occurances) have been mapped here
        """
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
        acquisition_type = 'in collection'  # default if not known
        if date == '0000' and method == 'onbekend':
            return ''
        if date == '0000':
            date = '{{unknown}}'
        if method in types:
            acquisition_type = types[method]
        return '{{{{ProvenanceEvent|time={date}|type={type}|newowner=Amsterdam Museum|oldowner=}}}}'\
            .format(date=date, type=acquisition_type)

    def parse_dimension(self, dimensions):
        """
        Function to parse the different types of dimensions into a size template.
        Unit (cm, gram, etc.) type of dimension and the value are given.
        A complete list of possible values for the type within the Amsterdam Museum data can be found at:
        http://amdata.adlibsoft.com/wwwopac.ashx?command=facets&database=AMcollect&search=all&facet=dimension.type&limit=50&output=json
        """
        # TODO: correct mapping for multiple sizes (twice hoogte and breedte) hoogte a, etc.
        # TODO: What to do with weight (gewicht) in grams, size doesn't support this?
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
                size_str += '|' + types[dimension['dimension.type'][0]] + '=' + dimension['dimension.value'][0]
            else:
                size_str += '|' + dimension['dimension.value'][0]
        size_str += '}}'
        return size_str

    def parse_artist(self, makers):
        """
        first check whether an artist is given (if not return unknown-template).
        If an artist is known the date of death + birth and the role of the creator are appended behind their name.
        Possible improvements: reverse first and last name with regex; parse the dates; translate the roles into correct
        template; check the creator against existing creator templates.
        """
        number_of_makers = len(makers)
        if number_of_makers == 1 and makers[0]['creator'][0] == 'onbekend':
            return '{{unknown|author}}'
        makertext = ''
        first = True
        for maker in makers:
            if not first:
                makertext += ', '
            makertext += maker['creator'][0]
            if maker['creator.date_of_birth'][0] != '' and maker['creator.date_of_death'][0] != '':
                makertext += (' (' + maker['creator.date_of_birth'][0] + ' - ' + maker['creator.date_of_death'][0] + ')')
            if maker['creator.qualifier'][0] != '':
                makertext += (' ({{nl|' + maker['creator.qualifier'][0] + '}})')
            if 'creator.role' in maker:
                if maker['creator.role'][0] != '':
                    makertext += (' ({{nl|' + maker['creator.role'][0] + '}})')
            first=False
        return makertext

    def parse_references(self, documentation):
        """
        Parse each reference into a cite book template (assumption is made that it mostly are books/articles).
        """
        referencestext = ''
        for document in documentation:
            referencestext += '{{Cite book|author=' + document['documentation.author'][0]\
                            + '|title=' + document['documentation.title'][0]  \
                            + '|year=' + document['documentation.sortyear'][0]  \
                            + '|page=' + document['documentation.page_reference'][0]  \
                            + '|chapter=' + document['documentation.title.article'][0] \
                            + '}}'
        return referencestext

    def parse_date(self, start, end):
        """
        if start and end date are the same return one date, otherwise return the dates with an '-' in between.
        Often the date is a year range. It's unclear from this data whether it was made somewhere within this time span
        or during the whole time span.
        """
        if start == end:
            return start
        else:
            return start + '-' + end

    @classmethod
    def parse_reproduction_copy(cls, data):
        """
        A copy of the parse_reproduction method
        To be used when calling the classmethod get_thumbnail()
        """
        quality_order = ['high-end scan', 'digitale opname', 'scan', 'low-res scan', ''] # high to low quality

        reproductions = data['reproduction']
        for quality in quality_order:
            for reproduction in reproductions:
                # if we're at the '' (empty) quality then just go for any reproduction.
                if 'reproduction.type' in reproduction:
                    if reproduction['reproduction.type'][0] == quality or quality == '':
                        photographer = reproduction['reproduction.creator'][0]
                        photo_date = reproduction['reproduction.date'][0]
                        # replace the internal url for an external url per https://www.amsterdammuseum.nl/open-data
                        photo_url = 'http://ahm.adlibsoft.com/ahmimages/' + reproduction['reproduction.identifier_URL'][0][27:]
                        return photographer, photo_date, photo_url

    def parse_reproduction(self):
        """
        The images in the Amsterdam Museum adlib data are not represented per image but per object.
        An object can have multiple images.
        The current procedure is to select the best image (highest resolution) as often when there are multiple images they
        show similar parts of the object.
        in order of quality the images are looked through. Then the data from the first hit is returned.
        photographer, photo date and the image location are returned.
        There is also data on the image format, reference and reference_lref (and reproduction type) these are not returned.
        """
        quality_order = ['high-end scan', 'digitale opname', 'scan', 'low-res scan', ''] # high to low quality

        reproductions = self.data['reproduction']
        for quality in quality_order:
            for reproduction in reproductions:
                # if we're at the '' (empty) quality then just go for any reproduction.
                if 'reproduction.type' in reproduction:
                    if reproduction['reproduction.type'][0] == quality or quality == '':
                        photographer = reproduction['reproduction.creator'][0]
                        photo_date = reproduction['reproduction.date'][0]
                        # replace the internal url for an external url per https://www.amsterdammuseum.nl/open-data
                        photo_url = 'http://ahm.adlibsoft.com/ahmimages/' + reproduction['reproduction.identifier_URL'][0][27:]
                        return photographer, photo_date, photo_url

    def artwork_license(self, data):
        """
        This function tries to determine the correct (PD-old) license based on the authors date of death and date the work
        was created.
        """
        currentyear = datetime.datetime.now().year
        known_author = False  # check whether there are any known authors, initialize as false

        if 'maker' in data:
            most_recent_death = -99999  # everything should be larger
            for author in data['maker']:
                if len(author['creator.date_of_death'][0]) > 4:  # some cases are '', for a year we need 4 chars.
                    death = int(author['creator.date_of_death'][0][:4])
                    if death > most_recent_death:
                        most_recent_death = death
                if author['creator'] != 'onbekend' and author['creator'] != '':
                    known_author = True  # not anonymous
            if most_recent_death == -99999:
                None  # No date given so go out of the loop (mostly anonymous case) to check date of creation
            elif most_recent_death < 1923:
                return '{{{{PD-old-auto-1923|deathyear={year}}}}}'.format(year=most_recent_death)
            elif most_recent_death < 1926:
                return '{{{{PD-old-auto-1996|deathyear={year}}}}}'.format(year=most_recent_death)
            elif most_recent_death < (currentyear-70):
                return '{{PD-old-70}}'
            else:
                # author died less than 70 year ago, no pd-old applicable
                return False  # can't determine a valid license, needs a check after upload.

        if not known_author:
            if 'production.date.end' in data:
                date = data['production.date.end'][0]
                if date < 1923:
                    return '{{PD-anon-1923}}'
                elif date < (currentyear-70):
                    return '{{PD-anon-70-EU}}'
        if known_author:
            if 'production.date.end' in data:
                date = int(data['production.date.end'][0])
                if date < (currentyear-150):
                    # if the work was created more than 150 years ago we assume the author died more than 70 years ago.
                    return '{{PD-old-70}}'
        return False  # can't determine a valid license, needs a check after upload.

    def parse_description(self, descriptions):
        """
        function to parse descriptions from AM to wikidescription
        mainly select language template
        currently just selects the first description (as there is a lot of overlap)
        """
        lang_long = descriptions[0]['AHM.texts.type'][0]['value'][0]
        language = ''
        if lang_long[-2:] == 'NL':
            language = 'nl'
        if lang_long[-3:] == 'ENG':
            language = 'en'
        if language == '':
            return descriptions[0]['AHM.texts.tekst'][0]
        return '{{{{{lang}|{text}}}}}'.format(lang=language, text=descriptions[0]['AHM.texts.tekst'][0])

    def get_infobox_parameters(self, data):
        """
        This function receives a dictionary which is the resulting parsed json from a given object in the
        Amsterdam Museum database e.g.
        http://amdata.adlibsoft.com/wwwopac.ashx?database=AMcollect&search=priref=346&output=json
        The function then gets the parameters for the art photo infobox template and maps the values from the
        glams data into these parameters.
        """
        self.parameters['photo_license'] = '{{PD-because|Released into the Public Domain by the copyright holder, the Amsterdam Museum}}'
        wiki_license = self.artwork_license(data)
        if wiki_license:
            self.parameters['artwork_license'] = wiki_license
        else:
            self.parameters['artwork_license'] = '{{PD-because|Released into the Public Domain by the copyright holder, the Amsterdam Museum}}'
            self.categories.append('Images from the Amsterdam Museum needing license check')

        if 'reproduction' in data:
            self.parameters['photographer'], self.parameters['photo_date'], self.image_url = self.parse_reproduction()
        else:
            return False  # does not have any images so return false
        if 'acquisition.date' in data:
            self.parameters['object_history'] = self.parse_acquisition(data['acquisition.date'][0], data['acquisition.method'][0])
        if 'credit_line' in data:
            self.parameters['credit_line'] = '{{nl|' + data['credit_line'][0] + '}}'
        if 'dimension' in data:
            self.parameters['dimensions'] = self.parse_dimension(data['dimension'])
        if 'title' in data:
            self.parameters['title'] = data['title'][0]
        if 'maker' in data:
            self.parameters['artist'] = self.parse_artist(data['maker'])
        if 'documentation' in data:
            self.parameters['references'] = self.parse_references(data['documentation'])
        if 'material' in data:
            self.parameters['method'] = '{{nl|materiaal: ' + ', '.join(data['material']) + '}}'
        if 'object_name' in data:
            self.parameters['method'] += '{{nl|type object: ' + ', '.join(data['object_name']) + '}}'
        if 'technique' in data:
            self.parameters['method'] += '{{nl|techniek: ' + ', '.join(data['technique']) + '}}'
        if 'object_number' in data:
            self.parameters['accession_number'] = data['object_number'][0]
        if 'priref' in data:
            self.parameters['source'] = 'Collection of the Amsterdam Museum under: ['+ data['persistent_ID'][0] + ' ' + data['priref'][0] + ']'
        if 'production.date.end' in data and 'production.date.start' in data:
            self.parameters['date'] = self.parse_date(data['production.date.start'][0], data['production.date.end'][0])
        if 'AHMteksten' in data:
            self.parameters['description'] = self.parse_description(data['AHMteksten'])

        self.parameters['institution'] = '{{Institution:Amsterdam Museum}}'
        return True

    @classmethod
    def search_to_identifiers(cls, searchterm):
        ids = []
        searchstring = 'http://amdata.adlibsoft.com/wwwopac.ashx?database=AMcollect&q={search}&limit=100&output=json'.format(search=searchterm)
        results = library.load_from_url(searchstring)
        nr_of_results = int(results['adlibJSON']['diagnostic']['hits'])
        if nr_of_results == 0:
            return ids  # no results
        elif nr_of_results < 101:
            records = results['adlibJSON']['recordList']['record']
            for record in records:
                ids.append(record['priref'][0])
        else:
            # TODO: build a loop supporting looping to the next pages of results
            records = results['adlibJSON']['recordList']['record']
            for record in records:
                ids.append(record['priref'][0])
        return ids

