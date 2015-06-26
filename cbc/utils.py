from subprocess import Popen, PIPE, check_output, CalledProcessError


def conda_search(pkgname):
    command = ['conda', 'list', pkgname]
    proc = Popen(command, stdout=PIPE)
    out, _ = proc.communicate()    
    
    for line in out.decode('utf-8').splitlines():
        if line.startswith('#'):
            continue
        line = line.split();
        break
    
    if not line:
        return ''
    
    return '-'.join(line)


def conda_install(pkgname):
    # Until I can figure out a good way to build with the conda API
    # we'll use the CLI interface:
    command = 'conda install --use-local --yes {0}'.format(pkgname).split()
    try:
        for line in (check_output(command).decode('utf-8').splitlines()):
            print(line)
    except CalledProcessError as cpe:
        print('{0}\nexit={1}'.format(' '.join(cpe.cmd), cpe.returncode))
        