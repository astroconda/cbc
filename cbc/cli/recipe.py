#!/usr/bin/env python
import argparse
import os
from cbc.parsers import CBCConfigParser, ExtendedInterpolation


RECIPE_TYPES = ['python',
               'make',
               'gnu',
               'scons',
               'cmake']

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--style', default='python')
    parser.add_argument('--name', default='')
    parser.add_argument('--version', default='')
    parser.add_argument('--build-number', default='0')
    parser.add_argument('--license', default='')
    parser.add_argument('--homepage', default='http://')
    parser.add_argument('--d2to1-hack', action='store_true', default=False)
    parser.add_argument('--use-git', action='store_true', default=False)
    parser.add_argument('--meta-package', action='store_true', default=False)
    parser.add_argument('recipe', default='generic.ini')
    args = parser.parse_args()

    NAME = args.name
    VERSION = args.version
    BUILD_NUMBER = args.build_number
    HOMEPAGE = args.homepage
    LICENSE = args.license
    D2TO1_HACK = {
        'active': False,
        'linux': '',
        'windows': ''
    }
    METAPACKAGE = args.meta_package
    STYLE = args.style
    RECIPE = args.recipe

    if args.use_git:
        VERSION = '{{ environ.get("GIT_DESCRIBE_TAG", "0.0.0") }}.git'
        BUILD_NUMBER = '{{ environ.get("GIT_DESCRIBE_NUMBER", 0) }}'

    if args.d2to1_hack:
        D2TO1_HACK['active'] = True


    if D2TO1_HACK['active']:
        D2TO1_HACK['linux'] = '''
#d2to1 hack active
pip install --no-deps --upgrade --force d2to1 || exit 1
    '''
        D2TO1_HACK['windows'] = '''
# d2to1 hack active
pip install --no-deps --upgrade --force d2to1
if errorlevel 1 exit 1
    '''

    config = CBCConfigParser(interpolation=ExtendedInterpolation(),
                                allow_no_value=True, delimiters=(':','='))

    config['package'] = {}
    config['package']['name'] = NAME
    config['package']['version'] = VERSION

    config['about'] = {}
    config['about']['home'] = HOMEPAGE
    config['about']['license'] = LICENSE
    config['about']['summary'] = '${package:name}'

    if not METAPACKAGE:
        config['source'] = {}
        config['source']['fn'] = '${package:name}-${package:version}.tar.gz'
        config['source']['url'] = '${package:home}/${fn}'
        if args.use_git:
            config['source']['git_url'] = ''
            config['source']['git_tag'] = ''

    config['build'] = {}
    config['build']['number'] = BUILD_NUMBER

    config['requirements'] = {}
    config['requirements']['build'] = ''
    config['requirements']['run'] = ''

    build_req = ['\n']
    run_req = ['\n']

    if STYLE in RECIPE_TYPES and STYLE == 'python':
        build_req.append('setuptools')
        build_req.append('python')
        run_req.append('python')

        if D2TO1_HACK['active']:
            build_req.append('d2to1')
    # Other requirement styles don't exist, I think...?
    config['requirements']['build'] = '\n'.join(build_req)
    config['requirements']['run'] = '\n'.join(run_req)

    if not METAPACKAGE:
        config['test'] = {}
        config['test']['imports'] = '\n'
        config['test']['commands'] = '\n'

    config['cbc_build'] = {}
    config['cbc_build']['linux'] = ''
    config['cbc_build']['windows'] = ''

    build_linux = ['\n']
    build_windows = ['\n']

    if STYLE in RECIPE_TYPES and STYLE == 'python':
        if D2TO1_HACK['active']:
            build_linux.append(D2TO1_HACK['linux'])
            build_windows.append(D2TO1_HACK['windows'])

        build_linux.append('python setup.py install || exit 1')
        build_windows.append('python setup.py install')
        build_windows.append('if errorlevel 1 exit 1')

    elif STYLE in RECIPE_TYPES and STYLE == 'gnu':
        build_linux.append('./configure --prefix=$$PREFIX')
        build_linux.append('make -j$$CPU_COUNT')
        build_linux.append('make install')

        build_windows.append('# Probably unsupported...')
        build_windows.append('#./configure --prefix=%PREFIX%')
        build_windows.append('# make -j%CPU_COUNT%')
        build_windows.append('# make install')

    elif STYLE in RECIPE_TYPES and STYLE == 'make':
        build_linux.append('make -j$$CPU_COUNT PREFIX=$$PREFIX')
        build_linux.append('make install')

        build_windows.append('make -j%CPU_COUNT% PREFIX=%PREFIX%')
        build_windows.append('make install')

    elif STYLE in RECIPE_TYPES and STYLE == 'cmake':
        build_linux.append('mkdir BUILD_DIR && cd BUILD_DIR')
        build_linux.append('cd BUILD_DIR')
        build_linux.append('cmake -DCMAKE_INSTALL_PREFIX=$$PREFIX ..')

        build_windows.append('mkdir BUILD_DIR && cd BUILD_DIR')
        build_windows.append('cd BUILD_DIR')
        build_windows.append('cmake -DCMAKE_INSTALL_PREFIX=%PREFIX% ..')

    elif STYLE in RECIPE_TYPES and STYLE == 'scons':
        build_linux.append('scons')
        build_windows.append('scons')

    else:
        pass

    config['cbc_build']['linux'] = '\n'.join(build_linux)
    config['cbc_build']['windows'] = '\n'.join(build_windows)

    if not os.path.splitext(RECIPE)[1]:
        RECIPE += '.ini'

    with open(RECIPE, 'w+') as recipe:
        config.write(recipe)


if __name__ == '__main__':
    main()

