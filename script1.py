import sys
sys.path.append("..")
from pywikibot.specialbots import UploadRobot #stated to be unresolved, but works fine
import pandas as pd
from xml.dom import minidom
from urllib2 import urlopen
import re
from unidecode import unidecode

def __init__(self, targetSite, url, urlEncoding=None):

def main(searchstring):
    
        categories=['Draughts Dutch Championship'] #categories to be added to the images
        nocat=False #true if the categories above are not sufficient, false if they are sufficient
        nrOfFiles=0
    
        #articletext+='[[Category:' + category + ']]\n'
    
        file_url = 'http://proxy.handle.net/10648/aeedfdda-d0b4-102d-bcf8-003048976d84'

        UploadRobot.upload_file(self, file_url, False, None, 0)
    
    
        return nrOfFiles

if __name__ == "__main__":
    main()