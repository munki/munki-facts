'''Get the current SIP status for the startup disk'''

from __future__ import absolute_import, print_function

import subprocess


def fact():
    '''Return the current SIP status for the startup disk'''
    try:
        proc = subprocess.Popen(['/usr/bin/csrutil', 'status'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text="UTF-8")
        stdout, _ = proc.communicate()
    except (IOError, OSError):
        stdout = 'Unknown'

    return {'sip_status': stdout.strip()}


if __name__ == '__main__':
    print(fact())
