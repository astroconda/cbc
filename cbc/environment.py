import os

class IncompleteEnv(Exception):
    pass

class Environment(object):
    def __init__(self, *args, **kwargs):
        self.environ = os.environ.copy()
        self.config = {}
        self.cbchome = None
        
        if 'CBC_HOME' in kwargs:
            self.cbchome = kwargs['CBC_HOME']
        if 'CBC_HOME' in self.environ:
            self.cbchome = self.environ['CBC_HOME']
        
        if self.cbchome is None:
            raise IncompleteEnv('Environment.cbchome is undefined')
        
        if not os.path.exists(self.cbchome):
            os.makedirs(self.cbchome)
            
        self.config['meta'] = self.join('meta.yaml')
        self.config['build'] = self.join('build.sh')
        self.config['build_windows'] = self.join('bld.bat')
        
    def join(self, path):
        return os.path.join(self.cbchome, path)