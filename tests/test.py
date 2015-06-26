import nose
import nose.tools
import os
import cbc
from cbc.exceptions import IncompleteEnv, MetaDataError
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
        spec = cbc.meta.MetaData('deadbeefcafe.ini', self.env)
    
    @nose.tools.raises(IncompleteEnv)
    def test_spec_incomplete_environment(self):
        '''Screw up the environment on purpose
        '''
        del os.environ['CBC_HOME'] 
        env = cbc.environment.Environment()
    
    @nose.tools.raises(MetaDataError)
    def test_spec_environment_instance(self):
        '''Issue the incorrect class instance as the environment
        '''
        env = ''
        cbc_meta = cbc.meta.MetaData(self.ini, env)
        
    def test_spec_standalone_build_data(self):
        cbc_meta = cbc.meta.MetaData(self.ini, self.env)
        nose.tools.assert_in('cbc_build', cbc_meta.local_metadata)
        
    def test_spec_standalone_cgi_server_data(self):
        cbc_meta = cbc.meta.MetaData(self.ini, self.env)
        nose.tools.assert_in('cbc_cgi', cbc_meta.local_metadata)
    
    def test_spec_no_ini_and_yaml_crosstalk(self):
        cbc_meta = cbc.meta.MetaData(self.ini, self.env)
        nose.tools.assert_not_in('cbc_build', cbc_meta.conda_metadata)
        nose.tools.assert_not_in('cbc_cgi', cbc_meta.conda_metadata)

    def test_spec_outputs_valid_conda_metadata(self):
        import conda_build.metadata
        cbc_meta = cbc.meta.MetaData(self.ini, self.env)
        #cbc_meta.conda_write_meta()
        
        # Test against conda's build system
        conda_meta = conda_build.metadata.MetaData(self.env.cbchome)
        nose.tools.assert_is_instance(conda_meta, conda_build.metadata.MetaData)
        nose.tools.assert_equal(conda_meta.dist(), 'test-1.0.0-1')
        
        
        
if __name__ == '__main__':
    sys.argv.append('--verbosity=3')
    nose.main(argv=sys.argv)