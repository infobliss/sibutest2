import pkgutil

glam_list = []

def register_glam(c):
	glam_list.append(c)
	return c
	

for loader, module_name, is_pkg in  pkgutil.walk_packages(__path__):
    module = loader.find_module(module_name).load_module(module_name)