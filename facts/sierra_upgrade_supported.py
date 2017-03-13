'''Returns a fact to indicate if this machine can be upgraded to Sierra'''

# Based on
# https://github.com/hjuutilainen/adminscripts/blob/master/
#         check-10.12-sierra-compatibility.py

# sysctl function by Michael Lynn
# https://gist.github.com/pudquick/581a71425439f2cf8f09

# IOKit bindings by Michael Lynn
# https://gist.github.com/pudquick/
#         c7dd1262bd81a32663f0#file-get_platform-py-L22-L23

import os
import re
import subprocess

from ctypes import CDLL, c_uint, byref, create_string_buffer
from ctypes.util import find_library
libc = CDLL(find_library('c'))

import objc
from Foundation import NSBundle

IOKit_bundle = NSBundle.bundleWithIdentifier_('com.apple.framework.IOKit')

functions = [("IOServiceGetMatchingService", b"II@"),
             ("IOServiceMatching", b"@*"),
             ("IORegistryEntryCreateCFProperty", b"@I@@I"),
            ]

objc.loadBundleFunctions(IOKit_bundle, globals(), functions)


def io_key(keyname):
    return IORegistryEntryCreateCFProperty(
        IOServiceGetMatchingService(0, 
            IOServiceMatching("IOPlatformExpertDevice")), keyname, None, 0)


def sysctl(name, is_string=True):
    '''Wrapper for sysctl so we don't have to use subprocess'''
    size = c_uint(0)
    # Find out how big our buffer will be
    libc.sysctlbyname(name, None, byref(size), None, 0)
    # Make the buffer
    buf = create_string_buffer(size.value)
    # Re-run, but provide the buffer
    libc.sysctlbyname(name, buf, byref(size), None, 0)
    if is_string:
        return buf.value
    else:
        return buf.raw


def is_virtual_machine():
    '''Returns True if this is a VM, False otherwise'''
    cpu_features = sysctl('machdep.cpu.features').split()
    return 'VMM' in cpu_features


def get_current_model():
    '''Returns model info'''
    return sysctl('hw.model')


def is_supported_model():
    '''Returns False if model is in list of unsupported models,
    True otherwise'''
    non_supported_models = [
        'iMac4,1',
        'iMac4,2',
        'iMac5,1',
        'iMac5,2',
        'iMac6,1',
        'iMac7,1',
        'iMac8,1',
        'iMac9,1',
        'MacBook1,1',
        'MacBook2,1',
        'MacBook3,1',
        'MacBook4,1',
        'MacBook5,1',
        'MacBook5,2',
        'MacBookAir1,1',
        'MacBookAir2,1',
        'MacBookPro1,1',
        'MacBookPro1,2',
        'MacBookPro2,1',
        'MacBookPro2,2',
        'MacBookPro3,1',
        'MacBookPro4,1',
        'MacBookPro5,1',
        'MacBookPro5,2',
        'MacBookPro5,3',
        'MacBookPro5,4',
        'MacBookPro5,5',
        'Macmini1,1',
        'Macmini2,1',
        'Macmini3,1',
        'MacPro1,1',
        'MacPro2,1',
        'MacPro3,1',
        'MacPro4,1',
        'Xserve1,1',
        'Xserve2,1',
        'Xserve3,1']
    current_model = get_current_model()
    if current_model in non_supported_models:
        return False
    else:
        return True


def get_minor_system_version():
    '''Returns 7 for Lion, 8 for Mountain Lion, etc'''
    darwin_version = int(os.uname()[2].split('.')[0])
    return darwin_version - 4


def is_supported_system_version():
    '''Returns True if current macOS version is 10.7 through 10.11,
    False otherwise'''
    macos_minor_version = get_minor_system_version()
    if macos_minor_version >= 12:
        return False
    elif macos_minor_version >= 7:
        return True
    else:
        return False


def get_board_id():
    '''Returns our board-id'''
    return io_key("board-id").bytes().tobytes()[0:-1]


def is_supported_board_id():
    '''Returns True if current board_id is in list of supported board_ids,
    False otherwise'''
    platform_support_values = [
        'Mac-00BE6ED71E35EB86',
        'Mac-031AEE4D24BFF0B1',
        'Mac-031B6874CF7F642A',
        'Mac-06F11F11946D27C5',
        'Mac-06F11FD93F0323C5',
        'Mac-189A3D4F975D5FFC',
        'Mac-27ADBB7B4CEE8E61',
        'Mac-2BD1B31983FE1663',
        'Mac-2E6FAB96566FE58C',
        'Mac-35C1E88140C3E6CF',
        'Mac-35C5E08120C7EEAF',
        'Mac-3CBD00234E554E41',
        'Mac-42FD25EABCABB274',
        'Mac-473D31EABEB93F9B',
        'Mac-4B7AC7E43945597E',
        'Mac-4BC72D62AD45599E',
        'Mac-4BFBC784B845591E',
        'Mac-50619A408DB004DA',
        'Mac-65CE76090165799A',
        'Mac-66E35819EE2D0D05',
        'Mac-66F35F19FE2A0D05',
        'Mac-6F01561E16C75D06',
        'Mac-742912EFDBEE19B3',
        'Mac-77EB7D7DAF985301',
        'Mac-7BA5B2794B2CDB12',
        'Mac-7DF21CB3ED6977E5',
        'Mac-7DF2A3B5E5D671ED',
        'Mac-81E3E92DD6088272',
        'Mac-8ED6AF5B48C039E1',
        'Mac-937CB26E2E02BB01',
        'Mac-942452F5819B1C1B',
        'Mac-942459F5819B171B',
        'Mac-94245A3940C91C80',
        'Mac-94245B3640C91C81',
        'Mac-942B59F58194171B',
        'Mac-942B5BF58194151B',
        'Mac-942C5DF58193131B',
        'Mac-9AE82516C7C6B903',
        'Mac-9F18E312C5C2BF0B',
        'Mac-A369DDC4E67F1C45',
        'Mac-A5C67F76ED83108C',
        'Mac-AFD8A9D944EA4843',
        'Mac-B809C3757DA9BB8D',
        'Mac-BE0E8AC46FE800CC',
        'Mac-C08A6BB70A942AC2',
        'Mac-C3EC7CD22292981F',
        'Mac-DB15BD556843C820',
        'Mac-E43C1C25D4880AD6',
        'Mac-F2208EC8',
        'Mac-F221BEC8',
        'Mac-F221DCC8',
        'Mac-F222BEC8',
        'Mac-F2238AC8',
        'Mac-F2238BAE',
        'Mac-F22586C8',
        'Mac-F22589C8',
        'Mac-F2268CC8',
        'Mac-F2268DAE',
        'Mac-F2268DC8',
        'Mac-F22C89C8',
        'Mac-F22C8AC8',
        'Mac-F305150B0C7DEEEF',
        'Mac-F60DEB81FF30ACF6',
        'Mac-F65AE981FFA204ED',
        'Mac-FA842E06C61E91C5',
        'Mac-FC02E91DDD3FA6A4',
        'Mac-FFE5EF870D7BA81A']
    board_id = get_board_id()
    return board_id in platform_support_values


def fact():
    '''Return our sierra_upgrade_supported fact'''
    if is_virtual_machine():
        return {'sierra_upgrade_supported': True}
    if (is_supported_model() and is_supported_board_id() and
            is_supported_system_version()):
        return {'sierra_upgrade_supported': True}
    return {'sierra_upgrade_supported': False}


if __name__ == '__main__':
    # Debug/testing output when run directly
    print 'is_virtual_machine:          %s' % is_virtual_machine()
    print 'get_current_model:           %s' % get_current_model()
    print 'is_supported_model:          %s' % is_supported_model()
    print 'get_minor_system_version:    %s' % get_minor_system_version()
    print 'is_supported_system_version: %s' % is_supported_system_version()
    print 'get_board_id:                %s' % get_board_id()
    print 'is_supported_board_id:       %s' % is_supported_board_id()
    print fact()
