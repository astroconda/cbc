#!/usr/bin/env python
import argparse
import os
import sys
import cbc
import conda_build.metadata




os.environ['CBC_HOME'] = os.path.abspath(os.path.join(os.path.dirname(cbc.__file__), 'tests/data/build'))
#sys.argv.append('--force-rebuild')
#sys.argv.append('tests/data/aprio.ini')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--force-rebuild', 
                        action='store_true', 
                        help='Do not stop if package already installed')
    parser.add_argument('--no-build', 
                        action='store_true',
                        help='Generate metadata from cbc configuration (useful for manual building)')
    parser.add_argument('cbcfile',
                        nargs='+', 
                        help='CBC metadata')
    args = parser.parse_args()
    
    # Initialize internal environment
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
        print('Using cbc build configuration: {0}'.format(cbcfile))
        # Ensure the working directory remains the same throughout.
        os.chdir(env.pwd)
        
        metadata = cbc.meta.MetaData(cbcfile, env)
        metadata.env.mkpkgdir(metadata.local['package']['name'])
        metadata.render_scripts()
        
        if args.no_build:
            continue
        
        conda_metadata = conda_build.metadata.MetaData(env.pkgdir)
        
        if not args.force_rebuild:
            if cbc.utils.conda_search(conda_metadata.name()) == conda_metadata.dist():
                print('{0} metadata matches an installed package; increment the build number to rebuild or use --force-rebuild.'.format(conda_metadata.dist()))
                continue
        
        conda_builder_args = {'get_src': True, 'verbose': False}
        
        try:
            built = cbc.utils.conda_builder(metadata, conda_builder_args)
            if not built:
                print('Failure occurred while building: {0}'.format(conda_metadata.dist()))
                continue
        except cbc.exceptions.CondaBuildError as cbe:
            print(cbe)
            continue
        
        package_exists = cbc.utils.conda_search(conda_metadata.name())
        if not package_exists:
            cbc.utils.conda_install(conda_metadata.name())
        elif package_exists and args.force_rebuild:
            cbc.utils.conda_reinstall(conda_metadata.name())
        
        print('')
        
        
            