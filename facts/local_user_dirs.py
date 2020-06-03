'''Get a list of user home directories under /Users'''

from __future__ import absolute_import, print_function

import os


def fact():
    '''Return the list of user home directories under /Users'''
    # skip_names should include any directories you wish to ignore
    skip_names = ['Deleted Users', 'Shared', 'admin']
    user_dirs = [item for item in os.listdir('/Users')
                 if item not in skip_names and not item.startswith('.')]
    return {'local_user_dirs': user_dirs}


if __name__ == '__main__':
    print(fact())
