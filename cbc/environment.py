import os
from .exceptions import IncompleteEnv
from tempfile import TemporaryDirectory
import time


class Environment(object):
    def __init__(self, *args, **kwargs):
        self.environ = os.environ.copy()
        self.config = {}
        self.cbchome = None
        
        if 'CBC_HOME' in kwargs:
            self.cbchome = kwargs['CBC_HOME']
        
        # I want the local user environment to override what is
        # passed to the class.
        if 'CBC_HOME' in self.environ:
            self.cbchome = self.environ['CBC_HOME']
        
        if self.cbchome is None:
            raise IncompleteEnv('Environment.cbchome is undefined')
        
        if not os.path.exists(self.cbchome):
            os.makedirs(self.cbchome)
        
        self.config['script'] = {}
        self.config['script']['meta'] = self.join('meta.yaml')
        self.config['script']['build_linux'] = self.join('build.sh')
        self.config['script']['build_windows'] = self.join('bld.bat')
        
    def join(self, path):
        return os.path.join(self.cbchome, path)
    
    '''
    def local_temp(self):
        temp_prefix = os.path.basename(os.path.splitext(__name__)[0])
        return TemporaryDirectory(prefix=temp_prefix, dir=self.cbchome)        
    '''     
        