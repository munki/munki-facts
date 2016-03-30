'''Get the current Gatekeeper status'''

import subprocess

def fact():
    '''Return the current Gatekeeper status'''
    try:
        proc = subprocess.Popen(['/usr/sbin/spctl', '--status'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, _ = proc.communicate()
    except (IOError, OSError):
        stdout = 'Unknown'

    return {'gatekeeper_status': stdout.strip()}
