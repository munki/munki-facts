'''Get the current FileVault status for the startup disk'''

import subprocess


def fact():
    '''Return the current FileVault status for the startup disk'''
    try:
        proc = subprocess.Popen(['/usr/bin/fdesetup', 'status'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, _ = proc.communicate()
    except (IOError, OSError):
        stdout = 'Unknown'

    return {'filevault_status': stdout.strip()}


if __name__ == '__main__':
    print fact()
