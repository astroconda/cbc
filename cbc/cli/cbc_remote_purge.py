#!/usr/bin/env python
'''
DANGER. THIS WILL WIPE AN ENTIRE ANACONDA.ORG REPOSITORY CHANNEL.

YOU HAVE BEEN WARNED.
'''
import argparse
from subprocess import check_output, STDOUT


def choose(answer):
    answer = answer.upper()
    if answer == 'Y' or answer == 'YES':
        return True

    return False


def prompt_user(channel):
    message = 'You about to REMOVE every package inside of: {0}'.format(channel)
    message_length = len(message)
    print('!' * message_length)
    print(message)
    print('!' * message_length)
    print('')
    print('Continue? (y/N) ', end='')
    answer = input()
    print('')

    return choose(answer)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('channel', help='Name of channel to be purged of its contents')
    args = parser.parse_args()

    channel = args.channel

    show_command = 'conda-server channel --show {0}'.format(channel).split()
    show_output = check_output(show_command, stderr=STDOUT)
    show_output = show_output.decode()

    found = []
    for line in show_output.splitlines():
        line = line.lstrip()
        if not line:
            continue
        if not line.startswith('+'):
            continue
        line = line.replace('+', '').lstrip()
        package = '/'.join(line.split('/')[:2])
        found.append(package)

    if found:
        print("Packages to remove:")
        for pkg in found:
            print(pkg)

        if not prompt_user(channel):
            print('Operation aborted by user...')
            exit(0)

        print('')
        for pkg in found:
            purge_command = 'conda-server remove -f {0}'.format(pkg).split()
            print("Removing [{0:>10s}] :: {1:>10s}".format(channel, pkg))
            purge_output = check_output(purge_command, stderr=STDOUT)
    else:
        print("No packages in channel: {0}".format(channel))

if __name__ == '__main__':
    main()
