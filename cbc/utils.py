import json
from .meta import MetaData
from .exceptions import CondaBuildError
from subprocess import Popen, PIPE, STDOUT, check_output, CalledProcessError


def combine_args(args):
    if not isinstance(args, list):
        raise TypeError('Expecting a list instance, got: {0}'.format(type(args)))

    if not args:
        return ''

    return ' '.join(args)

def run_process(command, callback=None):
    if not isinstance(command, list):
        raise TypeError('Expecting a list instance, got: {0}'.format(type(command)))
    process = Popen(command, stdout=PIPE)
    while True:
        output = process.stdout.readline()
        output = output.decode()
        if not output and process.poll() is not None:
            break
        if output:
            print(output.strip())
            # Perform user-defined parsing of output
            if callback is not None:
                if not callback(output.strip()):
                    process.kill()

    return process.poll()


def conda_search(metadata):
    pkgname = metadata.name()
    command = ['conda', 'search', '--json', pkgname]
    proc = Popen(command, stdout=PIPE)
    out, _ = proc.communicate()

    output = out.decode('utf-8').strip()
    data = json.loads(output)
    if pkgname in data:
        for pkg in data[pkgname]:
            if pkg['installed']:
                return '-'.join([pkg['name'],
                                 pkg['version'],
                                 pkg['build']])

    return ''


def conda_install(pkgname, args=[]):
    # Until I can figure out a good way to build with the conda API
    # we'll use the CLI interface:
    command = 'conda install --yes {0} {1}'.format(combine_args(args), pkgname).split()
    try:
        run_process(command)
    except CalledProcessError as cpe:
        print('{0}\nexit={1}'.format(' '.join(cpe.cmd), cpe.returncode))


def conda_reinstall(pkgname, args=[]):
    # Until I can figure out a good way to build with the conda API
    # we'll use the CLI interface:
    commands = ['conda remove --yes {0}'.format(pkgname).split(),
                'conda install --yes {0} {1}'.format(combine_args(args), pkgname).split()]
    for command in commands:
        try:
            run_process(command)
        except CalledProcessError as cpe:
            print('{0}\nexit={1}'.format(combine_args(cpe.cmd), cpe.returncode))


def conda_builder(metadata, args=[]):
    if not isinstance(metadata, MetaData):
        raise CondaBuildError('Expecting instance of conda_build.metadata.MetaData, got: "{0}"'.format(type(metadata)))

    def check_bad_egg(output):
        bad_egg = 'UNKNOWN.egg-info'
        if bad_egg in output:
            raise CondaBuildError('Bad setuptools metadata produced UNKNOWN.egg-info instead of {0}*.egg-info!'.format(metadata.local['package']['name']))

    command = 'conda build {0} {1}'.format(combine_args(args), metadata.env.pkgdir).split()

    try:
        run_process(command, check_bad_egg)
    #OK Conda, let's play rough. stdout/stderr only, no exit for you.
    except SystemExit:
        print('Discarding SystemExit issued by setuptools')
    except CalledProcessError as cpe:
        print(cpe)
        return False

    return True
