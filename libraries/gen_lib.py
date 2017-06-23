''' generic library functions '''

def load_json_from_url(url):
    #Function to load the json from url and get the parsed json
    try:
        jstring=urllib2.urlopen(url).read()
    except:
        return 1, ""
    parsed_json = json.loads(jstring)
    return 0, parsed_json

def file_title_generator(rawtitle, glam_name, image_id, image_ext):
    #Function to genrate a standard title for the image to be uploaded
    if len(rawtitle)>85:
        #cut off the description if it's longer than 85 tokens at a space around 85.
        title = rawtitle[:90]
        cutposition = title.rfind(' ')
        if(cutposition>20):	
            title = re.sub('[:/#\[\]\{\}<>\|_]', '', unidecode(title[:cutposition]))
    else:
        title=re.sub('[:/#\[\]\{\}<>\|_;\?]', '', unidecode(rawtitle))

    filetitle = "{}{}{}{}{}{}{}".format(title, ' - ', glam_name, ' - ',  image_id, '.', image_ext)
    
    return filetitle


def photograph_template_builder(metadata) : 
    #metadata is a dictionary with keys creator, title, description, date, medium, department, reportagename, archiefinventaris, identifier, UUID, permission, license, nocat, categories
    #The function that builds the wiki metadata from the given values of the parameters
    articletext="{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}".format('== {{int:filedesc}} ==\n{{Photograph\n |photographer       = ', metadata['creator'], '\n |title              = {{nl|', metadata['title'], '}}\n |description        = {{nl|', metadata['description'], '}}\n |depicted people    = ', '\n |depicted place     =\n |date               = ', metadata['date'], '\n |medium             = {{nl|', metadata['medium'], '}}\n |dimensions         =\n |institution        = Nationaal Archief\n |department         = ', metadata['department'], ', ', metadata['reportagename'], '\n |references         =\n |object history     =\n |exhibition history =\n |credit line        = ', '\n |inscriptions       =\n |notes              =\n |accession number   = ', metadata['archiefinventaris'], ' (archive inventory number), ', metadata['identifier'], ' (file number)\n |source             = ', 'Nationaal Archief, ', metadata['department'], ', {{Nationaal Archief-source|UUID=', metadata['UUID'], '|file_share_id=', metadata['identifier'], '}}\n |permission         = ', metadata['permission'], '\n |other_versions     =\n }}\n\n== {{int:license-header}} ==\n{{Nationaal Archief}}\n' , metadata['license'], '\n\n')

    #collectionname=department
    
    if metadata['nocat']:
        articletext="{}{}".format(articletext, '[[Category:Images from the Nationaal Archief needing categories]]\n')

    if hasPhotographerInDict:
        articletext="{}{}{}{}".format(articletext, '[[Category:Photographs by ',  metadata['photographerName'],  ']]\n')
 
    for category in metadata['categories']:
        articletext="{}{}{}{}".format(articletext, '[[Category:', category , ']]\n')

def upload_file(image_location, description, filename):
    '''
    Given a description, image_location and filename this function uploads the file at the file location using the
    description using the filename given as filename on Commons.
    '''
    url=[image_location]
    bot = UploadRobot(url, description=description, useFilename=filename, keepFilename=True, verifyDescription=False, aborts=True)
    bot.run()

