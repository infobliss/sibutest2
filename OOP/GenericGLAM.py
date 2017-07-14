from infobox_templates import photograph_template, art_photo_template


class GenericGLAM:
    def __init__(self, template_type, url):
        self.template_type = template_type
        self.url = url

    @property
    def fill_template(self, parameters):
        '''fill the template based on the values provided by the derived GLAM class'''
        if self.template_type == 'Photograph':
            # Consider that default template is photograph template
            wikitext = photograph_template.format(**parameters)
            # To be displayed to the user for editing
        else:
            wikitext = art_photo_template.format(**parameters)
        return wikitext
