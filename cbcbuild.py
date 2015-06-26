import os
import cbc
import cbc.server
import conda_build
import conda_build.metadata
import conda_build.build
import argparse
import time
from cbc.exceptions import CondaBuildError

parser = argparse.ArgumentParser()
parser.add_argument('cbcfile', action='store', nargs='*', help='Build configuration file')
args = parser.parse_args()

os.environ['CBC_HOME'] = 'tests/data/build'
env = cbc.environment.Environment()

# Convert cbcfile paths to absolute paths
args.cbcfile = [ os.path.abspath(x) for x in args.cbcfile ]

# Verify we have a file that exists
for cbcfile in args.cbcfile:
    if not os.path.exists(cbcfile):
        print('{} does not exist.'.format(cbcfile))
        exit(1)
    elif not os.path.isfile(cbcfile):
        print('{} is not a file.'.format(cbcfile))
        exit(1)
    
# Perform build(s)
for cbcfile in args.cbcfile:
    # Ensure the working directory remains the same throughout.
    os.chdir(env.pwd)
    
    metadata = cbc.meta.MetaData(cbcfile, env)
    metadata.env.mkpkgdir(metadata.local['package']['name'])
    metadata.render_scripts()
    
    conda_metadata = conda_build.metadata.MetaData(env.pkgdir)
    
    if cbc.utils.conda_search(conda_metadata.name()) == conda_metadata.dist():
        print('{0} metadata matches an installed package; increment the build number to rebuild.'.format(conda_metadata.dist()))
        continue
    
    conda_build.build.build(conda_metadata, get_src=True, verbose=True)
    cbc.utils.conda_install(conda_metadata.name())
    