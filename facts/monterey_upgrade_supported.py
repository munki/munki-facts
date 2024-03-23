'''Returns a fact to indicate if this machine can be upgraded to macOS 12 Monterey'''

# Based on
# https://github.com/hjuutilainen/adminscripts/blob/master/
#         check-10.12-sierra-compatibility.py

# sysctl function by Michael Lynn
# https://gist.github.com/pudquick/581a71425439f2cf8f09

# IOKit bindings by Michael Lynn
# https://gist.github.com/pudquick/
#         c7dd1262bd81a32663f0#file-get_platform-py-L22-L23

# Information on what boardIDs and Models that are supported is buried in the installer found here:
#   Install macOS Monterey/Contents/SharedSupport/SharedSupport.dmg - mount this
#       /Volumes/Shared Support/com_apple_MobileAsset_MacSoftwareUpdate/bc70a04218e8e8bd40d2472aecbb2a06773ba42b.zip - decompress this, the name of the zip will most likely change with every OS update.
#           bc70a04218e8e8bd40d2472aecbb2a06773ba42b/AssetData/boot/PlatformSupport.plist
#
#
# device_support_values are harvested from the full installer Distribution file. 
# The macOS 12.0.1 Distribution from ProductID 002-23774 was found at http://swcdn.apple.com/content/downloads/39/60/002-23774-A_KNETE2LDIN/4ll6ahj3st7jhqfzzjt1bjp1nhwl4p4zx7/002-23774.English.dist

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
    if isinstance(name, str):
        name = name.encode('utf-8')
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
    '''Returns True if model is in list of supported models,
    False otherwise'''
    supported_models = [
        u'MacBook10,1',
        u'MacBook9,1',
        u'MacBookAir7,1',
        u'MacBookAir7,2',
        u'MacBookAir8,1',
        u'MacBookAir8,2',
        u'MacBookAir9,1',
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
        u'MacBookPro16,1',
        u'MacBookPro16,2',
        u'MacBookPro16,3',
        u'MacBookPro16,4',
        u'MacPro6,1',
        u'MacPro7,1',
        u'Macmini7,1',
        u'Macmini8,1',
        u'iMac16,1',
        u'iMac16,2',
        u'iMac17,1',
        u'iMac18,1',
        u'iMac18,2',
        u'iMac18,3',
        u'iMac19,1',
        u'iMac19,2',
        u'iMac20,1',
        u'iMac20,2',
        u'iMacPro1,1'
    ]
    current_model = get_current_model()
    if not current_model:
        return False
    elif current_model in supported_models:
        return True
    else:
        return False

def is_supported_board_id():
    '''Returns True if current board_id is in list of supported board_ids,
    False otherwise'''
    platform_support_values = (
        u'Mac-06F11F11946D27C5',
        u'Mac-06F11FD93F0323C5',
        u'Mac-0CFF9C7C2B63DF8D',
        u'Mac-112818653D3AABFC',
        u'Mac-1E7E29AD0135F9BC',
        u'Mac-226CB3C6A851A671',
        u'Mac-27AD2F918AE68F61',
        u'Mac-35C5E08120C7EEAF',
        u'Mac-473D31EABEB93F9B',
        u'Mac-4B682C642B45593E',
        u'Mac-53FDB3D8DB8CA971',
        u'Mac-551B86E5744E2388',
        u'Mac-5F9802EFE386AA28',
        u'Mac-63001698E7A34814',
        u'Mac-65CE76090165799A',
        u'Mac-66E35819EE2D0D05',
        u'Mac-77F17D7DA9285301',
        u'Mac-7BA5B2D9E42DDD94',
        u'Mac-7BA5B2DFE22DDD8C',
        u'Mac-827FAC58A8FDFA22',
        u'Mac-827FB448E656EC26',
        u'Mac-937A206F2EE63C01',
        u'Mac-937CB26E2E02BB01',
        u'Mac-9AE82516C7C6B903',
        u'Mac-9F18E312C5C2BF0B',
        u'Mac-A369DDC4E67F1C45',
        u'Mac-A5C67F76ED83108C',
        u'Mac-A61BADE1FDAD7B05',
        u'Mac-AA95B1DDAB278B95',
        u'Mac-AF89B6D9451A490B',
        u'Mac-B4831CEBD52A0C4C',
        u'Mac-B809C3757DA9BB8D',
        u'Mac-BE088AF8C5EB4FA2',
        u'Mac-CAD6701F7CEA0921',
        u'Mac-CFF7D910A743CAAF',
        u'Mac-DB15BD556843C820',
        u'Mac-E1008331FDC96864',
        u'Mac-E43C1C25D4880AD6',
        u'Mac-E7203C0F68AA0004',
        u'Mac-EE2EBD4B90B839A8',
        u'Mac-F60DEB81FF30ACF6',
        u'Mac-FFE5EF870D7BA81A',
        u'VMM-x86_64'
        )       
    board_id = get_board_id()
    return board_id in platform_support_values

def is_supported_device_id():
    '''Returns True if current device_id is in list of supported device_ids,
    False otherwise'''
    device_support_values = (
        u'J132AP', 
        u'J137AP', 
        u'J140AAP', 
        u'J140KAP', 
        u'J152FAP', 
        u'J160AP', 
        u'J174AP', 
        u'J185AP', 
        u'J185FAP', 
        u'J213AP', 
        u'J214AP', 
        u'J214KAP', 
        u'J215AP', 
        u'J223AP', 
        u'J230AP', 
        u'J230KAP', 
        u'J274AP', 
        u'J293AP', 
        u'J313AP', 
        u'J314cAP', 
        u'J314sAP', 
        u'J316cAP', 
        u'J316sAP'
        u'J456AP', 
        u'J457AP', 
        u'J680AP', 
        u'J780AP', 
        u'VMA2MACOSAP', 
        u'VMM-x86_64', 
        u'X589AMLUAP', 
        u'X86LEGACYAP' 
        )
    device_support_values = [deviceid.lower() for deviceid in device_support_values]
    device_id = get_device_id()
    return device_id in device_support_values


def get_minor_system_version():
    '''Returns 20 for Big Sur, 21 for Monterey, etc'''
    darwin_version = int(os.uname()[2].split('.')[0])
    return darwin_version - 4


def is_supported_system_version():
    '''Returns True if current macOS version is 10.9 through 13.x,
    False otherwise'''
    macos_minor_version = get_minor_system_version()
    if macos_minor_version >= 17:
        return False
    elif macos_minor_version >= 9:
        return True
    else:
        return False

def get_board_id():
    '''Returns our board-id'''
    return io_key_string_value("board-id")

def get_device_id():
    '''Returns our device-id'''
    deviceid = sysctl("hw.target")
    return deviceid.lower()

def get_current_model():
    '''Returns model info'''
    return io_key_string_value("model")

def fact():
    '''Return our monterey_upgrade_supported fact'''
    if is_virtual_machine():
        return {'monterey_upgrade_supported': True}
    if ((is_supported_model() or is_supported_board_id() or is_supported_device_id()) and
            is_supported_system_version()):
        return {'monterey_upgrade_supported': True}
    return {'monterey_upgrade_supported': False}


if __name__ == '__main__':
    # Debug/testing output when run directly
    print('is_virtual_machine:          %s' % is_virtual_machine())
    print('get_current_model:           %s' % get_current_model())
    print('is_supported_model:          %s' % is_supported_model())
    print('get_minor_system_version:    %s' % get_minor_system_version())
    print('is_supported_system_version: %s' % is_supported_system_version())
    print('get_board_id:                %s' % get_board_id())
    print('is_supported_board_id:       %s' % is_supported_board_id())
    print('get_device_id:               %s' % get_device_id())
    print('is_supported_device_id:       %s' % is_supported_device_id())
    print(fact())
