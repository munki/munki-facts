'''Returns a fact to indicate if this machine can be upgraded to Catalina'''

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
    '''Returns False if model is in list of non_supported_models,
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
        'iMac10,1',
        'iMac11,1',
        'iMac11,2',
        'iMac11,3',
        'iMac12,1',
        'iMac12,2',
        'MacBook1,1',
        'MacBook2,1',
        'MacBook3,1',
        'MacBook4,1',
        'MacBook5,1',
        'MacBook5,2',
        'MacBook6,1',
        'MacBook7,1',
        'MacBookAir1,1',
        'MacBookAir2,1',
        'MacBookAir3,1',
        'MacBookAir3,2',
        'MacBookAir4,1',
        'MacBookAir4,2',
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
        'MacBookPro6,1',
        'MacBookPro6,2',
        'MacBookPro7,1',
        'MacBookPro8,1',
        'MacBookPro8,2',
        'MacBookPro8,3',
        'Macmini1,1',
        'Macmini2,1',
        'Macmini3,1',
        'Macmini4,1',
        'Macmini5,1',
        'Macmini5,2',
        'Macmini5,3',
        'MacPro1,1',
        'MacPro2,1',
        'MacPro3,1',
        'MacPro4,1',
        'MacPro5,1',
        'Xserve1,1',
        'Xserve2,1',
        'Xserve3,1',
        ]
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
    '''Returns True if current macOS version is 10.9 through 10.14,
    False otherwise'''
    macos_minor_version = get_minor_system_version()
    if macos_minor_version >= 15:
        return False
    elif macos_minor_version >= 9:
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
    '''Returns True if board_id is in the list of supported values;
    False otherwise'''
    platform_support_values = [
        'Mac-00BE6ED71E35EB86',
        'Mac-1E7E29AD0135F9BC',
        'Mac-2BD1B31983FE1663',
        'Mac-2E6FAB96566FE58C',
        'Mac-3CBD00234E554E41',
        'Mac-4B7AC7E43945597E',
        'Mac-4B682C642B45593E',
        'Mac-5A49A77366F81C72',
        'Mac-06F11F11946D27C5',
        'Mac-06F11FD93F0323C5',
        'Mac-6F01561E16C75D06',
        'Mac-7BA5B2D9E42DDD94',
        'Mac-7BA5B2DFE22DDD8C',
        'Mac-7DF2A3B5E5D671ED',
        'Mac-7DF21CB3ED6977E5',
        'Mac-9AE82516C7C6B903',
        'Mac-9F18E312C5C2BF0B',
        'Mac-27AD2F918AE68F61',
        'Mac-27ADBB7B4CEE8E61',
        'Mac-031AEE4D24BFF0B1',
        'Mac-031B6874CF7F642A',
        'Mac-35C1E88140C3E6CF',
        'Mac-35C5E08120C7EEAF',
        'Mac-42FD25EABCABB274',
        'Mac-53FDB3D8DB8CA971',
        'Mac-65CE76090165799A',
        'Mac-66E35819EE2D0D05',
        'Mac-66F35F19FE2A0D05',
        'Mac-77EB7D7DAF985301',
        'Mac-77F17D7DA9285301',
        'Mac-81E3E92DD6088272',
        'Mac-90BE64C3CB5A9AEB',
        'Mac-112B0A653D3AAB9C',
        'Mac-189A3D4F975D5FFC',
        'Mac-226CB3C6A851A671',
        'Mac-473D31EABEB93F9B',
        'Mac-551B86E5744E2388',
        'Mac-747B1AEFF11738BE',
        'Mac-827FAC58A8FDFA22',
        'Mac-827FB448E656EC26',
        'Mac-937A206F2EE63C01',
        'Mac-937CB26E2E02BB01',
        'Mac-9394BDF4BF862EE7',
        'Mac-50619A408DB004DA',
        'Mac-63001698E7A34814',
        'Mac-112818653D3AABFC',
        'Mac-A5C67F76ED83108C',
        'Mac-A369DDC4E67F1C45',
        'Mac-AA95B1DDAB278B95',
        'Mac-AFD8A9D944EA4843',
        'Mac-B809C3757DA9BB8D',
        'Mac-B4831CEBD52A0C4C',
        'Mac-BE0E8AC46FE800CC',
        'Mac-BE088AF8C5EB4FA2',
        'Mac-C3EC7CD22292981F',
        'Mac-C6F71043CEAA02A6',
        'Mac-CAD6701F7CEA0921',
        'Mac-CF21D135A7D34AA6',
        'Mac-DB15BD556843C820',
        'Mac-E43C1C25D4880AD6',
        'Mac-EE2EBD4B90B839A8',
        'Mac-F60DEB81FF30ACF6',
        'Mac-F65AE981FFA204ED',
        'Mac-F305150B0C7DEEEF',
        'Mac-FA842E06C61E91C5',
        'Mac-FC02E91DDD3FA6A4',
        'Mac-FFE5EF870D7BA81A',
        ]
    board_id = get_board_id()
    if board_id in platform_support_values:
        return True
    else:
        return False


def fact():
    '''Return our catalina_upgrade_supported fact'''
    if is_virtual_machine():
        return {'catalina_upgrade_supported': True}
    if (is_supported_model() and is_supported_board_id() and
            is_supported_system_version()):
        return {'catalina_upgrade_supported': True}
    return {'catalina_upgrade_supported': False}


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
