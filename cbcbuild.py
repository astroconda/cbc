import os
import cbc
import cbc.server
import conda_build
import conda_build.metadata
import conda_build.build
import threading
import sys


'''Emulated input here
'''
sys.argv.append('tests/data/test.ini')
if len(sys.argv) < 2:
    print("{0} {{cbc_config}}".format(sys.argv[0]))
    exit(1)

os.environ['CBC_HOME'] = os.path.abspath('tests/data/build')
cbcini = os.path.abspath(sys.argv[1])
env = cbc.environment.Environment()
metadata = cbc.meta.MetaData(cbcini, env)

# Write out conda compatible metadata and build scripts
for maskkey, maskval in env.config['script'].items():
    for metakey, metaval in metadata.compile().items():
        if metakey in maskkey:
            with open(maskval, 'w+') as metafile:
                metafile.write(metaval)

conda_metadata = conda_build.metadata.MetaData(env.cbchome)

if metadata.local_metadata['cbc_cgi']['local_server']:
    fileserver_thread = threading.Thread(target=cbc.server.FileServer,
                          args=([metadata.local_metadata['cbc_cgi']['local_port'],
                                metadata.local_metadata['cbc_cgi']['local_sources'],
                                True]),
                          daemon=True)
    fileserver_thread.start()

#conda_build.build.rm_pkgs_cache(conda_metadata.dist())
conda_build.build.build(conda_metadata, get_src=True, verbose=True)
