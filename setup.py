import os
from setuptools import setup, find_packages
from cbc.extern.version import get_git_version

entry_points = {}
package_data = {}

entry_points['console_scripts'] = [
    'cbc_build = cbc.cli.build:main',
    'cbc_server = cbc.cli.server:main',
    'cbc_recipe = cbc.cli.recipe:main',
    'cbc_remote_purge = cbc.cli.remote_purge:main',
]

package_data[''] = ['*.txt', '*.md']
test_suite = 'cbc.tests:main'

cbcpkg = os.path.join('cbc', 'version.py')

#Omit git hash and let setuptools add a valid build number
git_version = get_git_version()
git_version = git_version[:git_version.rfind('-')]

with open(cbcpkg, 'w+') as version_data:
    version_data.write('__version__ = "{0}"\n'.format(git_version))

NAME = 'cbc'
VERSION = git_version

setup(
    name=NAME,
    version=VERSION,
    description='Conda Build Controller',
    requires=['conda_build', 'binstar_client'],
    provides=[NAME],
    author='Joseph Hunkeler',
    author_email='jhunk@stsci.edu',
    license='BSD',
    url='http://bitbucket.org/jhunkeler/cbc',
    download_url='',
    use_2to3=False,
    packages=find_packages(),
    entry_points=entry_points,
    package_data=package_data,
    test_suite=test_suite,
)
