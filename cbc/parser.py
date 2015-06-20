'''I refuse to write the same thing over and over again in meta.yaml.
And yeah, conda supports Jinja2, but ugh... No.
'''

import os
import conda_build
import conda_build.metadata

import configparser
from configparser import ConfigParser, ExtendedInterpolation
from pprint import pprint
import yaml

def convert_conda_fields(fields):
    temp = {}
    for fkey, fval in fields.items():
        temp[fkey] = { x: '' for x in fval}
            #fields[field] = dict(value)
    return temp


class Specfile(object):
    def __init__(self, filename):
        if not os.path.exists(filename):
            print('"{0}" does not exist.'.format(filename));
            return
            
        self.filename = filename
        fields = convert_conda_fields(conda_build.metadata.FIELDS)
        
        config = ConfigParser(interpolation=ExtendedInterpolation(), allow_no_value=True)
        config.read_dict(fields)
        config.read(self.filename)
        
        with open('../../test.ini.out', 'w+') as testfile:
            config.write(testfile)
        
        y = yaml.load(fields)
        md = conda_build.metadata.MetaData()
        
        #for section in config.sections():
        #    for sub in config[section]:
        #        print('{0}:{1}:{2}'.format(section, sub, config[section][sub]))

if __name__ == '__main__':
    spec = Specfile('../../test.spec')
    #pprint()
    