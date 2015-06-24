'''I refuse to write the same thing over and over again in meta.yaml.
And yeah, conda supports Jinja2, but ugh... No.
'''

import os
import conda_build.metadata
import yaml
from configparser import SafeConfigParser, ExtendedInterpolation, ConfigParser
from collections import OrderedDict
from .environment import Environment
from .exceptions import MetaDataError


class MetaData(object):
    def __init__(self, filename, env):
        
        if not os.path.exists(filename):
            raise OSError('"{0}" does not exist.'.format(filename));
        
        self.filename = filename
        
        if not isinstance(env, Environment):
            raise MetaDataError('Expecting instance of cbc.environment.Environment, got: "{0}"'.format(type(env)))
        
        self.env = env
        self.keywords = ['cbc_build', 'cbc_cgi']
        
        
        self.fields = self.convert_conda_fields(conda_build.metadata.FIELDS)
        #self.config = SafeConfigParser(interpolation=ExtendedInterpolation(), allow_no_value=True)
        self.config = CBCConfigParser(interpolation=ExtendedInterpolation(), allow_no_value=True)
        # Include built-in Conda metadata fields
        self.config.read_dict(self.fields)
        # Include user-defined build fields
        self.config.read(self.filename)
        
        # Convert ConfigParser -> dict
        self.local = self.as_dict(self.config)
        
        #if not self.local['requirements']['build']:
        #    raise MetaDataError('Incomplete or missing "requirements" section: self.local[\'requirements\'] ', self.local['requirements']['build'])
            
        self.local['requirements']['build'] = self.config.getlist('requirements', 'build')
        self.local['requirements']['run'] = self.config.getlist('requirements', 'run')
        
        self.local_metadata = {}
        for keyword in self.keywords:
            if keyword in self.local:
                self.local_metadata[keyword] = self.local[keyword]  

        # Convert dict to YAML-compatible dict
        self.conda_metadata = self.scrub(self.local, self.keywords)
        
    def run(self):
        self.conda_write_meta()

    def compile(self):
        compiled = {}
        compiled['meta'] = yaml.safe_dump(self.conda_metadata, default_flow_style=False, line_break=True, indent=4)
        compiled['build_linux'] = self.local_metadata['cbc_build']['linux']
        #if 'windows' in self.local_metadata['']
        compiled['build_windows'] = self.local_metadata['cbc_build']['windows']
        return compiled

    def convert_conda_fields(self, fields):
        temp = OrderedDict()
        for fkey, fval in fields.items():
            temp[fkey] = { x: '' for x in fval}

        return temp

    def scrub(self, obj, force_remove=[]):
        obj_c = obj.copy()
        if isinstance(obj_c, dict):
            for key,val in obj_c.items():
                for reserved in force_remove:
                    if reserved in key:
                        del obj[reserved]
                        continue
                if isinstance(val, dict):
                    val = self.scrub(val)
                if val is None or val == {} or not val:
                    del obj[key]

        return obj


    def as_dict(self, config):
        """
        Converts a ConfigParser object into a dictionary.

        The resulting dictionary has sections as keys which point to a dict of the
        sections options as key => value pairs.
        """
        the_dict = {}
        for section in config.sections():
            the_dict[section] = {}
            for key, val in config.items(section):
                for cast in (int, float, bool, str):
                    try:
                        the_dict[section][key] = cast(val)
                    except ValueError:
                        pass

        return the_dict


def aslist_cronly(value):
    if isinstance(value, str):
        value = filter(None, [x.strip() for x in value.splitlines()])
    return list(value)

def aslist(value, flatten=True):
    """ Return a list of strings, separating the input based on newlines
    and, if flatten=True (the default), also split on spaces within
    each line."""
    values = aslist_cronly(value)
    if not flatten:
        return values
    result = []
    for value in values:
        subvalues = value.split()
        result.extend(subvalues)
    return result

class CBCConfigParser(SafeConfigParser):
    def getlist(self,section,option):
        value = self.get(section,option)
        return list(filter(None, (x.strip() for x in value.splitlines())))

    def getlistint(self,section,option):
        return [int(x) for x in self.getlist(section,option)]