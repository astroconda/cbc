import os
import time
from .exceptions import IncompleteEnv
from .parsers import CBCConfigParser, ExtendedInterpolation



class Environment(object):
    def __init__(self, *args, **kwargs):
        self.environ = os.environ.copy()
        self.config = {}
        self.cbchome = None
        self.pwd = os.path.abspath(os.curdir)
        self.pkgdir = None
        self.rcpath = os.path.expanduser('~/.cbcrc')
        self.configrc = None
        
        if 'CBC_HOME' in kwargs:
            self.cbchome = kwargs['CBC_HOME']
        
        # I want the local user environment to override what is
        # passed to the class.
        if 'CBC_HOME' in self.environ:
            self.cbchome = self.environ['CBC_HOME']

        if os.path.exists(self.rcpath):
            if os.path.isfile(self.rcpath):
                self.configrc = CBCConfigParser(interpolation=ExtendedInterpolation())
                self.configrc.read(self.rcpath)
        
        if 'settings' in self.configrc.sections():
            if 'path' in self.configrc['settings']:
                self.cbchome = self.configrc['settings']['path']
                if not self.cbchome:
                    raise IncompleteEnv('.cbcrc empty path detected. Check: settings -> path')

        if self.cbchome is None:
            raise IncompleteEnv('CBC_HOME is undefined.')
        
        self.cbchome = os.path.abspath(self.cbchome)
        if not os.path.exists(self.cbchome):
            os.makedirs(self.cbchome)

        
    def _script_meta(self):
        self.config['script'] = {}
        self.config['script']['meta'] = self.join('meta.yaml')
        self.config['script']['build_linux'] = self.join('build.sh')
        self.config['script']['build_windows'] = self.join('bld.bat')
        
    def join(self, filename):
        return os.path.abspath(os.path.join(self.pkgdir, filename))
    
    def mkpkgdir(self, pkgname):
        pkgdir = os.path.join(self.cbchome, pkgname)
        
        if not pkgname:
            raise IncompleteEnv('Empty package name passed to {0}'.format(__name__))
        if not os.path.exists(pkgdir):
            os.mkdir(pkgdir)
            
        self.pkgdir = pkgdir
        self._script_meta()
        

        
