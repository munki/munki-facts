'''Returns facts that indicate if this machine can be upgraded to macOS 13 or newer'''

# Based on
# https://github.com/hjuutilainen/adminscripts/blob/master/
#         check-10.12-sierra-compatibility.py

# sysctl function by Michael Lynn
# https://gist.github.com/pudquick/581a71425439f2cf8f09

# IOKit bindings by Michael Lynn
# https://gist.github.com/pudquick/
#         c7dd1262bd81a32663f0#file-get_platform-py-L22-L23

# Information on supported models is buried in the installer found here:
#   Install macOS Sequoia.app/Contents/SharedSupport/SharedSupport.dmg - mount this
#       /Volumes/Shared Support/com_apple_MobileAsset_MacSoftwareUpdate/LONG_HEX_STRING.zip 
#        - decompress this, the name of the zip will most likely change with every OS update.
#           - Combining, sorting, and de-duping values from the following result in a list of supported models 
#                    - 'SupportedProductTypes' from LONG_HEX_STRING/AssetData/boot/Restore.plist
#                    - 'SupportedModelProperties' from LONG_HEX_STRING/AssetData/boot/PlatformSupport.plist


MACOS_RELEASES = [
    {
        "name": "sequoia",
        "version": 15,
        "supported_models": [
            'iMac19,1',
            'iMac19,2',
            'iMac20,1',
            'iMac20,2',
            'iMac21,1',
            'iMac21,2',
            'iMacPro1,1',
            'Mac13,1',
            'Mac13,2',
            'Mac14,10',
            'Mac14,12',
            'Mac14,13',
            'Mac14,14',
            'Mac14,15',
            'Mac14,2',
            'Mac14,3',
            'Mac14,5',
            'Mac14,6',
            'Mac14,7',
            'Mac14,8',
            'Mac14,9',
            'Mac15,10',
            'Mac15,11',
            'Mac15,12',
            'Mac15,13',
            'Mac15,3',
            'Mac15,4',
            'Mac15,5',
            'Mac15,6',
            'Mac15,7',
            'Mac15,8',
            'Mac15,9',
            'MacBookAir10,1',
            'MacBookAir9,1',
            'MacBookPro15,1',
            'MacBookPro15,2',
            'MacBookPro15,3',
            'MacBookPro15,4',
            'MacBookPro16,1',
            'MacBookPro16,2',
            'MacBookPro16,3',
            'MacBookPro16,4',
            'MacBookPro17,1',
            'MacBookPro18,1',
            'MacBookPro18,2',
            'MacBookPro18,3',
            'MacBookPro18,4',
            'Macmini8,1',
            'Macmini9,1'
            'MacPro7,1',
            'VirtualMac2,1',
        ]
    },
    {
        "name": "sonoma",
        "version": 14,
        "supported_models": [
            'iMac19,1',
            'iMac19,2',
            'iMac20,1',
            'iMac20,2',
            'iMac21,1',
            'iMac21,2',
            'iMacPro1,1',
            'iSim1,1',
            'Mac13,1',
            'Mac13,2',
            'Mac14,10',
            'Mac14,12',
            'Mac14,13',
            'Mac14,14',
            'Mac14,15',
            'Mac14,2',
            'Mac14,3',
            'Mac14,5',
            'Mac14,6',
            'Mac14,7',
            'Mac14,8',
            'Mac14,9',
            'Mac15,3',
            'Mac15,4',
            'Mac15,5',
            'Mac15,6',
            'Mac15,7',
            'Mac15,8',
            'Mac15,9',
            'MacBookAir10,1',
            'MacBookAir8,1',
            'MacBookAir8,2',
            'MacBookAir9,1',
            'MacBookPro15,1',
            'MacBookPro15,2',
            'MacBookPro15,3',
            'MacBookPro15,4',
            'MacBookPro16,1',
            'MacBookPro16,2',
            'MacBookPro16,3',
            'MacBookPro16,4',
            'MacBookPro17,1',
            'MacBookPro18,1',
            'MacBookPro18,2',
            'MacBookPro18,3',
            'MacBookPro18,4',
            'Macmini8,1',
            'Macmini9,1',
            'MacPro7,1',
            'VirtualMac2,1'
        ]
    },
    {
        "name": "ventura",
        "version": 13,
        "supported_models": [
            'iMac18,1',
            'iMac18,2',
            'iMac18,3',
            'iMac19,1',
            'iMac19,2',
            'iMac20,1',
            'iMac20,2',
            'iMac21,1',
            'iMac21,2',
            'iMacPro1,1',
            'iSim1,1',
            'Mac13,1',
            'Mac13,2',
            'Mac14,2',
            'Mac14,7',
            'MacBook10,1',
            'MacBookAir10,1',
            'MacBookAir8,1',
            'MacBookAir8,2',
            'MacBookAir9,1',
            'MacBookPro14,1',
            'MacBookPro14,2',
            'MacBookPro14,3',
            'MacBookPro15,1',
            'MacBookPro15,2',
            'MacBookPro15,3',
            'MacBookPro15,4',
            'MacBookPro16,1',
            'MacBookPro16,2',
            'MacBookPro16,3',
            'MacBookPro16,4',
            'MacBookPro17,1',
            'MacBookPro18,1',
            'MacBookPro18,2',
            'MacBookPro18,3',
            'MacBookPro18,4',
            'Macmini8,1',
            'Macmini9,1',
            'MacPro7,1',
            'VirtualMac2,1'
        ]
    },
]


import os
import platform

from ctypes import CDLL, c_uint, byref, create_string_buffer
from ctypes import cast, POINTER, c_int32, c_int64
from ctypes.util import find_library

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


def get_macos_version():
    return int(platform.mac_ver()[0].split('.')[0])


def is_virtual_machine():
    '''Returns True if this is a VM, False otherwise'''
    if get_macos_version() >= 11:
        hv_vmm_present = sysctl('kern.hv_vmm_present', output_type=int)
        return bool(hv_vmm_present)
    else:
        cpu_features = sysctl('machdep.cpu.features').split()
        return 'VMM' in cpu_features


def get_current_model():
    '''Returns model info'''
    return io_key_string_value("model")


def is_supported_model(supported_models):
    '''Returns True if model is in list of supported models,
    False otherwise'''
    return get_current_model() in supported_models


def fact():
    '''Return a fact for each os'''
    facts = {}
    for release in MACOS_RELEASES:
        fact_name = release["name"] + '_upgrade_supported'
        if is_virtual_machine():
            facts[fact_name] = True
        elif ((is_supported_model(release["supported_models"])) and
            get_macos_version() < release["version"]):
            facts[fact_name] = True
        else:
            facts[fact_name] = False
    return facts


if __name__ == '__main__':
    # Debug/testing output when run directly
    print('is_virtual_machine:\t\t%s' % is_virtual_machine())
    print('get_current_model:\t\t%s' % get_current_model())
    print('get_macos_version:\t\t%s' % get_macos_version())
    for k, v in fact().items():
        print(f'{k}:\t{v}')
