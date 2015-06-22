import nose
import nose.tools
import os
import cbc
from cbc.environment import IncompleteEnv
from cbc.meta import SpecError
import sys


class TestCBC(object):
    def setUp(self):
        lookup = os.path.join(os.path.dirname(__file__), 'data')
        output = os.path.join(lookup, 'output')
        os.makedirs(output, exist_ok=True)
        os.environ['CBC_HOME'] = output
        self.env = cbc.environment.Environment()
        self.ini = os.path.join(lookup, 'test.ini')
         
    
    def tearDown(self):
        pass
    
    @nose.tools.raises(OSError)
    def test_spec_does_not_exist(self):
        '''Issue non-existent INI and see what happens.
        ''' 
        spec = cbc.meta.Spec('deadbeefcafe.ini', self.env)
    
    @nose.tools.raises(IncompleteEnv)
    def test_spec_incomplete_environment(self):
        '''Screw up the environment on purpose
        '''
        del os.environ['CBC_HOME'] 
        env = cbc.environment.Environment()
    
    @nose.tools.raises(SpecError)
    def test_spec_environment_instance(self):
        '''Issue the incorrect class instance as the environment
        '''
        env = ''
        spec = cbc.meta.Spec(self.ini, env)
        
    def test_spec_standalone_build_data(self):
        spec = cbc.meta.Spec(self.ini, self.env)
        nose.tools.assert_in('build_ext', spec.spec_metadata)
        
    def test_spec_standalone_cgi_server_data(self):
        spec = cbc.meta.Spec(self.ini, self.env)
        nose.tools.assert_in('cgi', spec.spec_metadata)
    
    def test_spec_no_ini_and_yaml_crosstalk(self):
        spec = cbc.meta.Spec(self.ini, self.env)
        nose.tools.assert_not_in('build_ext', spec.conda_metadata)
        nose.tools.assert_not_in('cgi', spec.conda_metadata)

    def test_spec_outputs_valid_conda_metadata(self):
        spec = cbc.meta.Spec(self.ini, self.env)
        spec.conda_write_meta()
        import conda_build.metadata
        meta = conda_build.metadata.MetaData(self.env.cbchome)
        nose.tools.assert_is_instance(meta, conda_build.metadata.MetaData)
        nose.tools.assert_equal(meta.dist(), 'test-1.0.0-1')
        
        
        
if __name__ == '__main__':
    sys.argv.append('--verbosity=3')
    nose.main(argv=sys.argv)