'''Get the list of admin users'''

from __future__ import absolute_import, print_function

import grp


def fact():
    '''Return the list of admin users for this machine'''
    return {'admin_users': grp.getgrgid(80).gr_mem}


if __name__ == '__main__':
    print(fact())
