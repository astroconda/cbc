import os
import conda_build.metadata
import conda_build.environ
import yaml
import shutil
from glob import glob
from collections import OrderedDict
from .parsers import CBCConfigParser, ExtendedInterpolation
from .environment import Environment
from .exceptions import MetaDataError


class MetaData(object):
    def __init__(self, filename, env):

        filename = os.path.abspath(filename)
        if not os.path.exists(filename):
            raise OSError('"{0}" does not exist.'.format(filename));

        self.filename = filename
        self.confdir = os.path.dirname(self.filename)

        if not isinstance(env, Environment):
            raise MetaDataError('Expecting instance of cbc.environment.Environment, got: "{0}"'.format(type(env)))

        self.env = env
        self.builtins = ['cbc_build', 'cbc_cgi', 'settings', 'environ']

        self.fields = self.convert_conda_fields(conda_build.metadata.FIELDS)
        self.config = CBCConfigParser(interpolation=ExtendedInterpolation(), allow_no_value=True, comment_prefixes='#')

        # Include built-in Conda metadata fields
        self.config.read_dict(self.fields)

        if self.env.configrc is not None:
            self.config.read_dict(self.as_dict(self.env.configrc))

        # Include user-defined build fields
        self.config.read(self.filename)
        # Assimilate conda environment variables
        self.config['environ'] = conda_build.environ.get_dict()

        # Convert ConfigParser -> generic dictionary
        self.local = self.as_dict(self.config)

        #Field list conversion table taken from conda_build.metadata:
        for field in ('source/patches', 'source/url',
                      'build/entry_points', 'build/script_env',
                      'build/features', 'build/track_features',
                      'requirements/build', 'requirements/run',
                      'requirements/conflicts', 'test/requires',
                      'test/files', 'test/commands', 'test/imports'):
            section, key = field.split('/')
            if self.local[section][key]:
                self.local[section][key] = self.config.getlist(section, key)

        self.local_metadata = {}
        for keyword in self.builtins:
            if keyword in self.local:
                self.local_metadata[keyword] = self.local[keyword]

        # Convert dict to YAML-compatible dict
        self.conda_metadata = self.scrub(self.local, self.builtins)

    def run(self):
        self.render_scripts()

    def render_scripts(self):
        '''Write all conda scripts
        '''
        for maskkey, maskval in self.env.config['script'].items():
            for metakey, metaval in self.compile().items():
                if metakey in maskkey:
                    with open(maskval, 'w+') as metafile:
                        metafile.write(metaval)

    def copy_patches(self):
        extensions = ['*.diff', '*.patch']
        for extension in extensions:
            path = os.path.join(self.confdir, extension)
            for patch in glob(path):
                shutil.copy2(patch, self.env.pkgdir)

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
                    try:
                        del obj[key]
                    except KeyError as err:
                        print(err)

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
