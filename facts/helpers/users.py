''' 
helper methods for getting login info and sorting users reported by the ac command

by @nathanperkins
https://github.com/nathanperkins/
'''

import sys
import subprocess


def get_users_from_ac():
    ''' return list of users reported by ac with exclusions removed '''

    exclusions = ['_mbsetupuser', 'root', 'total']

    cmd = ['ac', '-p']
    proc = subprocess.Popen(
        cmd, 
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    out, err = proc.communicate()

    output_lines = out.split('\n')
    users = [line.split()[0].strip() for line in output_lines if len(line) > 0]

    for exclusion in exclusions:
        if exclusion in users:
            users.remove(exclusion)

    return users

def get_user_connect_time(ac_output):
    ''' return the total length of time a user has been connect to a machine based on their ac -d output '''
    connect_time = 0

    output_lines = [line for line in ac_output.split('\n') if line]

    for line in output_lines:
        time_connected = float(line.split()[3])
        if time_connected > 0:
            connect_time += time_connected

    return connect_time

def get_user_num_logins(ac_output):
    ''' return the total number of times a user logged in to the machine based on their ac -d output '''
    output_lines = [line for line in ac_output.split('\n') if line]

    return len(output_lines)
    

def get_users_info(users):
    ''' return a list of users with a dict of their connect_time and num_logins '''

    users_info = {}

    for user in users:
        cmd = ['ac', '-d', user]
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        out, err = proc.communicate()

        users_info[user] = {
            'connect_time': get_user_connect_time(out),
            'num_logins': get_user_num_logins(out),
        }

    return users_info

def get_users(sorted_by='connect_time'):
    ''' return a list of users sorted by the given method (connect_time or num_logins) '''

    users = get_users_from_ac()
    users_info = get_users_info(users)

    if sorted_by == 'connect_time':
        users = sorted(users_info, key=lambda user: users_info[user]['connect_time'], reverse=True)

    elif sorted_by == 'num_logins':
        users = sorted(users_info, key=lambda user: users_info[user]['num_logins'], reverse=True)

    else:
        print("helpers/user.py error: users must be sorted by connect_time or num_logins")
        sys.exit(1)

    return users

if __name__ == '__main__':
    users = get_users_from_ac()
    print('\nget_users_info()\n' + str(get_users_info(users)) + '\n')
    print("get_users(sorted_by='num_logins')\n" + str(get_users(sorted_by='num_logins')) + '\n')
    print("get_users(sorted_by='connect_time')\n" + str(get_users(sorted_by='connect_time')) + '\n')
