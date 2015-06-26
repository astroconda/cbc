import os
import cbc
import cbc.server
import conda_build
import conda_build.metadata
import conda_build.build
import argparse
import time
from subprocess import check_output, CalledProcessError

parser = argparse.ArgumentParser()
parser.add_argument('cbcfile', action='store', nargs='*', help='Build configuration file')

input_test = ['tests/data/astropy-helpers.ini', 'tests/data/astropy.ini']
#input_test = ['tests/data/d2to1.ini']
args = parser.parse_args(input_test)

os.environ['CBC_HOME'] = 'tests/data/build'
env = cbc.environment.Environment()


for cbcfile in args.cbcfile:
    # Ensure the working directory remains stable per build.
    os.chdir(env.pwd)
    
    metadata = cbc.meta.MetaData(cbcfile, env)
    metadata.env.mkpkgdir(metadata.local['package']['name'])   
    metadata.render_scripts()
    
    conda_metadata = conda_build.metadata.MetaData(env.pkgdir)
    
    if 'cbc_cgi' in metadata.local_metadata:    
        if metadata.local_metadata['cbc_cgi']['local_server']:
            fileserver = cbc.server.FileServer(metadata.local_metadata['cbc_cgi']['local_port'],
                                  metadata.local_metadata['cbc_cgi']['local_sources'],
                                  run=True)
    
    conda_build.build.build(conda_metadata, get_src=True, verbose=True)
    
    # Until I can figure out a good way to build with the conda API
    # we'll use the CLI:
    command = 'conda install --use-local --yes {0}'.format(conda_metadata.name()).split()
    try:
        for line in (check_output(command).decode('utf-8').splitlines()):
            print(line)
    except CalledProcessError as cpe:
        print('{0} exit={1}'.format(cpe.cmd, cpe.returncode))
    