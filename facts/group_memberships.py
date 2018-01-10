'''
modify list of relevant groups in the search_groups list
and this fact will return any of the groups
that the top user belongs to.

designed for utilizing munki-conditions to control
package deployment with active directory groups

by @nathanperkins (GitHub)
https://github.com/nathanperkins/
'''

import subprocess

from facts.helpers.users import get_users

search_groups = [
    # enter group names here
    'SFO-MacAdmins',
]


def fact():
    likeliest_user = get_users(sorted_by='connect_time')[0]
    cmd = ['id', likeliest_user]

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()

    found_groups = []

    for group in search_groups:
        if group in out:
            found_groups.append(group)
     
    return {
        'group_memberships': found_groups,
    }

if __name__ == '__main__':
    print fact()
