'''Get the current Gatekeeper status'''

from __future__ import absolute_import, print_function

import subprocess


def fact():
    '''Return the current Gatekeeper status'''
    try:
        proc = subprocess.Popen(['/usr/sbin/spctl', '--status'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text="UTF-8")
        stdout, _ = proc.communicate()
    except (IOError, OSError):
        stdout = 'Unknown'

    return {'gatekeeper_status': stdout.strip()}


if __name__ == '__main__':
    print(fact())
