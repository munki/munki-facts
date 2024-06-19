'''Returns an array of hashtables that represents the current system extensions'''

# Example NSPredicate query to query multiple properties to determine if Symantec endpoint protections extensions are not activated:
# system_extensions != NULL AND
# SUBQUERY(
#     system_extensions,
#     $s,
#     $s.state BEGINSWITH 'activated' AND
#     $s.bundleID IN {'com.broadcom.mes.systemextension', 'com.symantec.mes.systemextension'}
# ).@count == 0

from __future__ import absolute_import, print_function

import subprocess
import re

def fact():
    try:
        proc = subprocess.Popen(['/usr/bin/systemextensionsctl', 'list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text="UTF-8")
        stdout, _ = proc.communicate()
    except (IOError, OSError):
        stdout = 'Unknown'
    
    regex = re.compile(r"^(\t|\*\t\*|\t\*)\t(?P<teamID>\S*)\t(?P<bundleID>\S*)\s*\((?P<version>\S*)\)\t(?P<name>.*)\b\t\[(?P<state>.*)\]", re.MULTILINE)
    exts = [match.groupdict() for match in regex.finditer(stdout)]
    
    return {'system_extensions': exts}

if __name__ == '__main__':
    print(fact())
