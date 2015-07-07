from .meta import MetaData
from .exceptions import CondaBuildError
from subprocess import Popen, PIPE, STDOUT, check_call, check_output, CalledProcessError


def conda_search(pkgname):
    command = ['conda', 'list', pkgname]
    proc = Popen(command, stdout=PIPE)
    out, _ = proc.communicate()    
    
    found = ''
    for line in out.decode('utf-8').splitlines():
        if line.startswith('#'):
            continue

        line = line.split()
        
        if line[0] == pkgname:
            found = line[:3]
        
    if not line:
        return ''
    
    return '-'.join(found)


def conda_install(pkgname):
    # Until I can figure out a good way to build with the conda API
    # we'll use the CLI interface:
    command = 'conda install --use-local --yes {0}'.format(pkgname).split()
    try:
        for line in (check_output(command).decode('utf-8').splitlines()):
            print(line)
    except CalledProcessError as cpe:
        print('{0}\nexit={1}'.format(' '.join(cpe.cmd), cpe.returncode))


def conda_reinstall(pkgname):
    # Until I can figure out a good way to build with the conda API
    # we'll use the CLI interface:
    commands = ['conda remove --yes {0}'.format(pkgname).split(),
                'conda install --use-local --yes {0}'.format(pkgname).split()]
    for command in commands:
        try:
            for line in (check_output(command).decode('utf-8').splitlines()):
                print(line)
        except CalledProcessError as cpe:
            print('{0}\nexit={1}'.format(' '.join(cpe.cmd), cpe.returncode))


def conda_builder(metadata, args):
    if not isinstance(metadata, MetaData):
        raise CondaBuildError('Expecting instance of conda_build.metadata.MetaData, got: "{0}"'.format(type(metadata)))

    bad_egg = 'UNKNOWN.egg-info'
    command = ['conda', 'build', metadata.env.pkgdir ]

    try:
        for line in (check_output(command, stderr=STDOUT).decode('utf-8').splitlines()):
            if line.startswith('#'):
                continue
            print(line)
            
            if bad_egg in line:
                raise CondaBuildError('Bad setuptools metadata produced UNKNOWN.egg-info instead of {0}*.egg-info!'.format(metadata.local['package']['name']))          
    #OK Conda, let's play rough. stdout/stderr only, no exit for you.
    except SystemExit:
        print('Discarding SystemExit issued by setuptools')
    except CalledProcessError as cpe:
        print(cpe)
        return False
    
    return True
