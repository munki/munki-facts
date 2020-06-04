'''Get the current FileVault status for the startup disk'''

from __future__ import absolute_import, print_function

import subprocess


def fact():
    '''Return the current FileVault status for the startup disk'''
    try:
        proc = subprocess.Popen(['/usr/bin/fdesetup', 'status'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, _ = proc.communicate()
    except (IOError, OSError):
        stdout = 'Unknown'

    return {'filevault_status': stdout.strip().decode('utf-8')}


if __name__ == '__main__':
    print(fact())
