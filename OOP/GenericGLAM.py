from infobox_templates import photograph_template, art_photo_template


class GenericGLAM:
    def __init__(self, template):
        self.template = template

    def fill_template(parameters, right_template):
        '''fill the template based on the values provided by the derived GLAM class'''
        if right_template == 'Photograph':
            # Consider that default template is photograph template
            wikitext = photograph_template.format(**parameters)
            # To be displayed to the user for editing
        else:
            wikitext = art_photo_template.format(**parameters)
        return wikitext
