import json
import sys
import inspect
from .meta import MetaData
from .exceptions import CondaBuildError
from subprocess import Popen, PIPE, STDOUT, check_output, CalledProcessError


def combine_args(args):
    if not isinstance(args, list):
        raise TypeError('Expecting a list instance, got: {0}'.format(type(args)))

    if not args:
        return ''

    return ' '.join(args)

def run_process(command, callbacks=None):
    callback_failed = False
    callback_status = None
    callback_message = ''
    process = Popen(command, stdout=PIPE, stderr=STDOUT)

    # Poll process for new output until finished
    while True:
        nextline = process.stdout.readline().decode()
        if nextline == '' and process.poll() != None:
            break
        sys.stdout.write(nextline)
        sys.stdout.flush()

    output = process.communicate()[0]
    output = output.decode()

    #Callbacks don't work yet. Sigh.
    if callbacks is not None:
        if not isinstance(callbacks, list):
            raise TypeError('Expecting a list instance, got: {0}'.format(type(command)))

        for callback in callbacks:
            callback_status, callback_message = callback(output)
            if not callback_status:
                callback_failed = True
                #Stop processing future callbacks here?

    exitCode = process.returncode

    if callback_failed:
        raise CondaBuildError(callback_message)
    elif exitCode == 0:
        return exitCode
    else:
        raise CalledProcessError(exitCode, combine_args(command))


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
        print(cpe)


def conda_reinstall(pkgname, args=[]):
    # Until I can figure out a good way to build with the conda API
    # we'll use the CLI interface:
    commands = ['conda remove --yes {0}'.format(pkgname).split(),
                'conda install --yes {0} {1}'.format(combine_args(args), pkgname).split()]
    for command in commands:
        try:
            run_process(command)
        except CalledProcessError as cpe:
            print(cpe)


def conda_builder(metadata, args=[]):
    if not isinstance(metadata, MetaData):
        raise CondaBuildError('Expecting instance of conda_build.metadata.MetaData, got: "{0}"'.format(type(metadata)))

    def check_bad_egg(output):
        bad_egg = 'UNKNOWN.egg-info'
        if bad_egg in output:
            return False, '{0}: Bad setuptools metadata produced UNKNOWN.egg-info instead of {1}*.egg-info!'.format(inspect.currentframe().f_code.co_name, metadata.local['package']['name'])
        return True, ''

    command = 'conda build {0} {1}'.format(combine_args(args), metadata.env.pkgdir).split()
    callbacks = [check_bad_egg]

    try:
        run_process(command, callbacks)
    except SystemExit:
        print('Discarding SystemExit issued by setuptools')
    except CalledProcessError as cpe:
        print(cpe)
        return False

    return True
