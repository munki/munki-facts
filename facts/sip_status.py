'''Get the current SIP status for the startup disk'''

import subprocess

def fact():
    '''Return the current SIP status for the startup disk'''
    try:
        proc = subprocess.Popen(['/usr/bin/csrutil', 'status'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, _ = proc.communicate()
    except (IOError, OSError):
        stdout = 'Unknown'

    return {'sip_status': stdout.strip()}
