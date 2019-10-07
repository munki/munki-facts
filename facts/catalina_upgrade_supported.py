'''Returns a fact to indicate if this machine can be upgraded to catalina'''
# Mofified for Catalina from here
# https://github.com/munki/munki-facts/tree/master/facts
#         check-10.12-sierra-compatibility.py

# Based on
# https://github.com/hjuutilainen/adminscripts/blob/master/
#         mojave_upgrade_supported.py

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
        u'MacBookPro4,1',
        u'MacPro2,1',
        u'Macmini5,2',
        u'Macmini5,1',
        u'MacBookPro5,1',
        u'MacBookPro1,1',
        u'MacBookPro5,3',
        u'MacBookPro5,2',
        u'iMac8,1',
        u'MacBookPro5,4',
        u'MacBookAir4,2',
        u'Macmini2,1',
        u'iMac5,2',
        u'iMac11,3',
        u'MacBookPro8,2',
        u'MacBookPro3,1',
        u'Macmini5,3',
        u'MacBookPro1,2',
        u'Macmini4,1',
        u'iMac9,1',
        u'iMac6,1',
        u'Macmini3,1',
        u'Macmini1,1',
        u'MacBookPro6,1',
        u'MacBookPro2,2',
        u'MacBookPro2,1',
        u'iMac12,2',
        u'MacBook3,1',
        u'MacPro3,1',
        u'MacBook5,1',
        u'MacBook5,2',
        u'iMac11,1',
        u'iMac10,1',
        u'MacBookPro7,1',
        u'MacBook2,1',
        u'MacBookAir4,1',
        u'MacPro4,1',
        u'MacBookPro6,2',
        u'iMac12,1',
        u'MacBook1,1',
        u'MacBookPro5,5',
        u'iMac11,2',
        u'iMac4,2',
        u'Xserve2,1',
        u'MacBookAir3,1',
        u'MacBookAir3,2',
        u'MacBookAir1,1',
        u'Xserve3,1',
        u'iMac4,1',
        u'MacBookAir2,1',
        u'Xserve1,1',
        u'iMac5,1',
        u'MacBookPro8,1',
        u'MacBook7,1',
        u'MacBookPro8,3',
        u'iMac7,1',
        u'MacBook6,1',
        u'MacBook4,1',
        u'MacPro1,1',
        u'MacPro5,1',
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
    '''Returns True if current macOS version is 10.7 through 10.14,
    False otherwise'''
    macos_minor_version = get_minor_system_version()
    if macos_minor_version >= 15:
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
        u'Mac-9AE82516C7C6B903',
        u'Mac-031B6874CF7F642A',
        u'Mac-112818653D3AABFC',
        u'Mac-9394BDF4BF862EE7',
        u'Mac-AA95B1DDAB278B95',
        u'Mac-CAD6701F7CEA0921',
        u'Mac-50619A408DB004DA',
        u'Mac-7BA5B2D9E42DDD94',
        u'Mac-B809C3757DA9BB8D',
        u'Mac-AFD8A9D944EA4843',
        u'Mac-27ADBB7B4CEE8E61',
        u'Mac-F305150B0C7DEEEF',
        u'Mac-35C1E88140C3E6CF',
        u'Mac-827FAC58A8FDFA22',
        u'Mac-77EB7D7DAF985301',
        u'Mac-2E6FAB96566FE58C',
        u'Mac-827FB448E656EC26',
        u'Mac-66E35819EE2D0D05',
        u'Mac-031AEE4D24BFF0B1',
        u'Mac-00BE6ED71E35EB86',
        u'Mac-4B7AC7E43945597E',
        u'Mac-5A49A77366F81C72',
        u'Mac-63001698E7A34814',
        u'Mac-937CB26E2E02BB01',
        u'Mac-FFE5EF870D7BA81A',
        u'Mac-53FDB3D8DB8CA971',
        u'Mac-226CB3C6A851A671',
        u'Mac-C6F71043CEAA02A6',
        u'Mac-4B682C642B45593E',
        u'Mac-1E7E29AD0135F9BC',
        u'Mac-90BE64C3CB5A9AEB',
        u'Mac-7BA5B2DFE22DDD8C',
        u'Mac-66F35F19FE2A0D05',
        u'Mac-189A3D4F975D5FFC',
        u'Mac-B4831CEBD52A0C4C',
        u'Mac-FA842E06C61E91C5',
        u'Mac-FC02E91DDD3FA6A4',
        u'Mac-06F11FD93F0323C5',
        u'Mac-06F11F11946D27C5',
        u'Mac-6F01561E16C75D06',
        u'Mac-F60DEB81FF30ACF6',
        u'Mac-473D31EABEB93F9B',
        u'Mac-3CBD00234E554E41',
        u'Mac-BE0E8AC46FE800CC',
        u'Mac-9F18E312C5C2BF0B',
        u'Mac-81E3E92DD6088272',
        u'Mac-65CE76090165799A',
        u'Mac-CF21D135A7D34AA6',
        u'Mac-F65AE981FFA204ED',
        u'Mac-112B0A653D3AAB9C',
        u'Mac-DB15BD556843C820',
        u'Mac-27AD2F918AE68F61',
        u'Mac-937A206F2EE63C01',
        u'Mac-77F17D7DA9285301',
        u'Mac-E43C1C25D4880AD6',
        u'Mac-BE088AF8C5EB4FA2',
        u'Mac-551B86E5744E2388',
        u'Mac-A5C67F76ED83108C',
        u'Mac-747B1AEFF11738BE',
        u'Mac-EE2EBD4B90B839A8',
        u'Mac-42FD25EABCABB274',
        u'Mac-7DF2A3B5E5D671ED',
        u'Mac-2BD1B31983FE1663',
        u'Mac-7DF21CB3ED6977E5',
        u'Mac-A369DDC4E67F1C45',
        u'Mac-35C5E08120C7EEAF',
        u'Mac-C3EC7CD22292981F',
    )
    board_id = get_board_id()
    return board_id in platform_support_values


def fact():
    '''Return our Mojave_upgrade_supported fact'''
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
