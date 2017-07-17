art_photo_parameters = {
      'artist': '',
      'title': '',
      'description': '',
      'date': '',
      'medium': '',
      'dimensions': '',
      'institution': '',
      'location': '',
      'references': '',
      'object_history': '',
      'exhibition_history': '',
      'credit_line': '',
      'inscriptions': '',
      'notes': '',
      'accession_number': '',
      'artwork_license': '',
      'place_of_creation': '',
      'photo_description': '',
      'photo_date': '',
      'photographer': '',
      'source': '',
      'photo_license': '',
      'other_versions': ''
}

art_photo_template = '''\
{{{{Art Photo
 |artist             = {artist}
 |title              = {title}
 |description        = {description}
 |date               = {date}
 |medium             = {medium}
 |dimensions         = {dimensions}
 |institution        = {institution}
 |location           = {location}
 |references         = {references}
 |object history     = {object_history}
 |exhibition history = {exhibition_history}
 |credit line        = {credit_line}
 |inscriptions       = {inscriptions}
 |notes              = {notes}
 |accession number   = {accession_number}
 |artwork license    = {artwork_license}
 |place of creation  = {place_of_creation}
 |photo description  = {photo_description}
 |photo date         = {photo_date}
 |photographer       = {photographer}
 |source             = {source}
 |photo license      = {photo_license}
 |other_versions     = {other_versions}
}}}}
'''

photograph_parameters = {
      'photographer': '',
      'title': '',
      'description': '',
      'depicted people': '',
      'depicted place': '',
      'date': '',
      'medium': '',
      'dimensions': '',
      'institution': '',
      'department': '',
      'references': '',
      'object_history': '',
      'exhibition_history': '',
      'credit_line': '',
      'inscriptions': '',
      'notes': '',
      'accession_number': '',
      'source': '',
      'permission': '',
      'other_versions': '',
      'wikidata': '',
      'camera coord': ''
 }

photograph_template = '''\
{{{{Photograph
 |photographer       = {photographer}
 |title              = {title}
 |description        = {description}
 |depicted people    = {depicted_people}
 |depicted place     = {depicted_place}
 |date               = {date}
 |medium             = {medium}
 |dimensions         = {dimensions}
 |institution        = {institution}
 |department         = {department}
 |references         = {references}
 |object history     = {object_history}
 |exhibition history = {exhibition_history}
 |credit line        = {credit_line}
 |inscriptions       = {inscriptions}
 |notes              = {notes}
 |accession number   = {accession_number}
 |source             = {source}
 |permission         = {permission}
 |other versions     = {other_versions}
 |wikidata           = {wikidata}
 |camera coord       = {camera_coord}

}}}}
'''
