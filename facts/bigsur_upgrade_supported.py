'''Returns a fact to indicate if this machine can be upgraded to bigsur'''

# Based on
# https://github.com/hjuutilainen/adminscripts/blob/master/
#         check-10.12-sierra-compatibility.py

# sysctl function by Michael Lynn
# https://gist.github.com/pudquick/581a71425439f2cf8f09

# IOKit bindings by Michael Lynn
# https://gist.github.com/pudquick/
#         c7dd1262bd81a32663f0#file-get_platform-py-L22-L23


from __future__ import absolute_import, print_function

from ctypes import CDLL, c_uint, byref, create_string_buffer
from ctypes import cast, POINTER
from ctypes.util import find_library
import os

import objc

from Foundation import NSBundle, NSString, NSUTF8StringEncoding

# glue to call C and Cocoa stuff
libc = CDLL(find_library('c'))
IOKit_bundle = NSBundle.bundleWithIdentifier_('com.apple.framework.IOKit')

functions = [("IOServiceGetMatchingService", b"II@"),
             ("IOServiceMatching", b"@*"),
             ("IORegistryEntryCreateCFProperty", b"@I@@I"),
            ]

objc.loadBundleFunctions(IOKit_bundle, globals(), functions)


def io_key(keyname):
    """Gets a raw value from the IORegistry"""
    return IORegistryEntryCreateCFProperty(
        IOServiceGetMatchingService(
            0, IOServiceMatching(b"IOPlatformExpertDevice")), keyname, None, 0)


def io_key_string_value(keyname):
    """Converts NSData/CFData return value to an NSString"""
    raw_value = io_key(keyname)
    return NSString.alloc().initWithData_encoding_(
        raw_value, NSUTF8StringEncoding
    ).rstrip('\0')


def sysctl(name, output_type=str):
    '''Wrapper for sysctl so we don't have to use subprocess'''
    size = c_uint(0)
    # Find out how big our buffer will be
    libc.sysctlbyname(name, None, byref(size), None, 0)
    # Make the buffer
    buf = create_string_buffer(size.value)
    # Re-run, but provide the buffer
    libc.sysctlbyname(name, buf, byref(size), None, 0)
    if output_type in (str, 'str'):
        return buf.value.decode('UTF-8')
    if output_type in (int, 'int'):
        # complex stuff to cast the buffer contents to a Python int
        if size.value == 4:
            return cast(buf, POINTER(c_int32)).contents.value
        if size.value == 8:
            return cast(buf, POINTER(c_int64)).contents.value
    if output_type == 'raw':
        # sysctl can also return a 'struct' type; just return the raw buffer
        return buf.raw


def is_virtual_machine():
    '''Returns True if this is a VM, False otherwise'''
    cpu_features = sysctl('machdep.cpu.features').split()
    return 'VMM' in cpu_features


def is_supported_model():
    '''Returns False if model is in list of unsupported models,
    True otherwise'''
    non_supported_models = [
        u'MacBook10,1',
        u'MacBook8,1',
        u'MacBook9,1',
        u'MacBookAir6,1',
        u'MacBookAir6,2',
        u'MacBookAir7,1',
        u'MacBookAir7,2',
        u'MacBookAir8,1',
        u'MacBookAir8,2',
        u'MacBookPro11,1',
        u'MacBookPro11,2',
        u'MacBookPro11,3',
        u'MacBookPro11,4',
        u'MacBookPro11,5',
        u'MacBookPro12,1',
        u'MacBookPro13,1',
        u'MacBookPro13,2',
        u'MacBookPro13,3',
        u'MacBookPro14,1',
        u'MacBookPro14,2',
        u'MacBookPro14,3',
        u'MacBookPro15,1',
        u'MacBookPro15,2',
        u'MacBookPro15,3',
        u'MacBookPro15,4',
        u'MacPro6,1',
        u'MacPro7,1',
        u'Macmini7,1',
        u'Macmini8,1',
        u'iMac14,4',
        u'iMac15,1',
        u'iMac16,1',
        u'iMac16,2',
        u'iMac17,1',
        u'iMac18,1',
        u'iMac18,2',
        u'iMac18,3',
        u'iMac19,1',
        u'iMac19,2',
        u'iMacPro1,1',
    ]
    current_model = get_current_model()
    if not current_model or current_model in non_supported_models:
        return False
    else:
        return True


def get_minor_system_version():
    '''Returns 7 for Lion, 8 for Mountain Lion, etc'''
    darwin_version = int(os.uname()[2].split('.')[0])
    return darwin_version - 4


def is_supported_system_version():
    '''Returns True if current macOS version is 10.7 through 10.13,
    False otherwise'''
    macos_minor_version = get_minor_system_version()
    if macos_minor_version >= 16:
        return False
    elif macos_minor_version >= 7:
        return True
    else:
        return False


def get_board_id():
    '''Returns our board-id'''
    return io_key_string_value("board-id")


def get_current_model():
    '''Returns model info'''
    return io_key_string_value("model")


def is_supported_board_id():
    '''Returns True if current board_id is in list of supported board_ids,
    False otherwise'''
    platform_support_values = (
        u'Mac-226CB3C6A851A671',
        u'Mac-36B6B6DA9CFCD881',
        u'Mac-112818653D3AABFC',
        u'Mac-9394BDF4BF862EE7',
        u'Mac-AA95B1DDAB278B95',
        u'Mac-CAD6701F7CEA0921',
        u'Mac-50619A408DB004DA',
        u'Mac-7BA5B2D9E42DDD94',
        u'Mac-B809C3757DA9BB8D',
        u'Mac-F305150B0C7DEEEF',
        u'Mac-35C1E88140C3E6CF',
        u'Mac-827FAC58A8FDFA22',
        u'Mac-6FEBD60817C77D8A',
        u'Mac-7BA5B2DFE22DDD8C',
        u'Mac-827FB448E656EC26',
        u'Mac-66E35819EE2D0D05',
        u'Mac-BE0E8AC46FE800CC',
        u'Mac-5A49A77366F81C72',
        u'Mac-63001698E7A34814',
        u'Mac-937CB26E2E02BB01',
        u'Mac-FFE5EF870D7BA81A',
        u'Mac-87DCB00F4AD77EEA',
        u'Mac-A61BADE1FDAD7B05',
        u'Mac-C6F71043CEAA02A6',
        u'Mac-4B682C642B45593E',
        u'Mac-1E7E29AD0135F9BC',
        u'Mac-90BE64C3CB5A9AEB',
        u'Mac-3CBD00234E554E41',
        u'Mac-189A3D4F975D5FFC',
        u'Mac-B4831CEBD52A0C4C',
        u'Mac-E1008331FDC96864',
        u'Mac-FA842E06C61E91C5',
        u'Mac-81E3E92DD6088272',
        u'Mac-06F11FD93F0323C5',
        u'Mac-06F11F11946D27C5',
        u'Mac-F60DEB81FF30ACF6',
        u'Mac-473D31EABEB93F9B',
        u'Mac-0CFF9C7C2B63DF8D',
        u'Mac-9F18E312C5C2BF0B',
        u'Mac-E7203C0F68AA0004',
        u'Mac-65CE76090165799A',
        u'Mac-CF21D135A7D34AA6',
        u'Mac-112B0A653D3AAB9C',
        u'Mac-DB15BD556843C820',
        u'Mac-27AD2F918AE68F61',
        u'Mac-937A206F2EE63C01',
        u'Mac-77F17D7DA9285301',
        u'Mac-9AE82516C7C6B903',
        u'Mac-BE088AF8C5EB4FA2',
        u'Mac-551B86E5744E2388',
        u'Mac-564FBA6031E5946A',
        u'Mac-A5C67F76ED83108C',
        u'Mac-5F9802EFE386AA28',
        u'Mac-747B1AEFF11738BE',
        u'Mac-EE2EBD4B90B839A8',
        u'Mac-42FD25EABCABB274',
        u'Mac-2BD1B31983FE1663',
        u'Mac-7DF21CB3ED6977E5',
        u'Mac-A369DDC4E67F1C45',
        u'Mac-35C5E08120C7EEAF',
        u'Mac-E43C1C25D4880AD6',
        u'Mac-53FDB3D8DB8CA971',
    )
    board_id = get_board_id()
    return board_id in platform_support_values


def fact():
    '''Return our sierra_upgrade_supported fact'''
    if is_virtual_machine():
        return {'bigsur_upgrade_supported': True}
    if (is_supported_model() and is_supported_board_id() and
            is_supported_system_version()):
        return {'bigsur_upgrade_supported': True}
    return {'bigsur_upgrade_supported': False}


if __name__ == '__main__':
    # Debug/testing output when run directly
    print('is_virtual_machine:          %s' % is_virtual_machine())
    print('get_current_model:           %s' % get_current_model())
    print('is_supported_model:          %s' % is_supported_model())
    print('get_minor_system_version:    %s' % get_minor_system_version())
    print('is_supported_system_version: %s' % is_supported_system_version())
    print('get_board_id:                %s' % get_board_id())
    print('is_supported_board_id:       %s' % is_supported_board_id())
    print(fact())
