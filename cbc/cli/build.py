#!/usr/bin/env python
import argparse
import os
import traceback
import sys
import conda_build.metadata
import cbc
from cbc.exceptions import CondaBuildError

def main():
    no_upload = ''
    use_local = ''
    python_version = ''

    parser = argparse.ArgumentParser()
    parser.add_argument('--force-rebuild',
                        action='store_true',
                        help='Do not stop if package already installed')
    parser.add_argument('--no-build',
                        action='store_true',
                        help='Generate metadata from cbc configuration (useful for manual building)')
    parser.add_argument('--no-upload',
                        action='store_true',
                        help='Do not upload to anaconda.org (aka. binstar)')
    parser.add_argument('--use-local',
                        action='store_true',
                        help='Install built package from [...]/conda-bld/pkgs repository')
    parser.add_argument('--python',
                        help='Coerce build to use a specific version of python.')
    parser.add_argument('cbcfile',
                        nargs='+',
                        help='CBC metadata')
    args = parser.parse_args()

    # Initialize cbc internal environment
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

    if args.no_upload:
        no_upload = '--no-binstar-upload'

    if args.use_local:
        use_local = '--use-local'

    if args.python:
        python_version = ' '.join(['--python', args.python])

    print('CBC_HOME={0}'.format(env.cbchome))
    # Perform build(s)
    for cbcfile in args.cbcfile:
        # Ensure the working directory remains the same throughout.
        os.chdir(env.pwd)

        metadata = cbc.meta.MetaData(cbcfile, env)
        metadata.env.mkpkgdir(metadata.local['package']['name'])
        metadata.render_scripts()
        metadata.copy_patches()

        print('-> {0}'.format(metadata.env.pkgdir))

        if args.no_build:
            continue

        print('Generating Conda metadata...')
        conda_metadata = conda_build.metadata.MetaData(env.pkgdir)

        python_version_ours = '.'.join([ str(sys.version_info.major), str(sys.version_info.minor) ])
        python_version_want = '.'.join(python_version.split()[1:])

        if python_version_want != python_version_ours:
            args.force_rebuild = True

        if not args.force_rebuild:
            if cbc.utils.conda_search(conda_metadata) == conda_metadata.dist():
                print('{0} matches an installed package; increment the build number to rebuild or use --force-rebuild.'.format(conda_metadata.dist()))
                continue

        conda_builder_args = [no_upload, use_local, python_version]
        try:
            print('Initializing Conda build...')
            built = cbc.utils.conda_builder(metadata, conda_builder_args)
            if not built:
                print('Failure occurred building: {0}'.format(conda_metadata.dist()))
                continue
        except CondaBuildError as cbe:
            print(traceback.format_exc())
            continue

        print('Installing Conda package...')
        package_exists = cbc.utils.conda_search(conda_metadata)

        if not package_exists:
            cbc.utils.conda_install(conda_metadata.name())
        elif package_exists:
            if args.force_rebuild:
                cbc.utils.conda_reinstall(conda_metadata.name())

        print('')


if __name__ == '__main__':
    main()
