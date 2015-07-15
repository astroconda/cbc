''' NOTES:
I'm not sure how I want the build system to work yet.

Maybe I want:
    Controller -> CONFIG_FILES as Task -> Monitor each Task

* How should I reliably weigh tasks? This part may get tedious if the weights
are in the configuration files.

    * I could use the old 000filename.conf style...
    * weight= in a config
'''
import os
from configparser import SafeConfigParser, ExtendedInterpolation

class Controller(object):
    def __init__(self):
        pass


class Task(object):
    def __init__(self, filename):
        self.config = SafeConfigParser(interpolation=ExtendedInterpolation(), allow_no_value=True)
    
    def check_config(self):
        pass
    
    def run(self):
        pass
