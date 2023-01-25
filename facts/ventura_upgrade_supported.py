'''Returns a fact to indicate if this machine can be upgraded to macOS 13 Ventura'''

# Based on
# https://github.com/hjuutilainen/adminscripts/blob/master/
#         check-10.12-sierra-compatibility.py

# sysctl function by Michael Lynn
# https://gist.github.com/pudquick/581a71425439f2cf8f09

# IOKit bindings by Michael Lynn
# https://gist.github.com/pudquick/
#         c7dd1262bd81a32663f0#file-get_platform-py-L22-L23

# Information on supported models is buried in the installer found here:
#   Install macOS Ventura.app/Contents/SharedSupport/SharedSupport.dmg - mount this
#       /Volumes/Shared Support/com_apple_MobileAsset_MacSoftwareUpdate/42e79bd54bb7295a5b729d32cb2493217f5d88f0.zip 
#        - decompress this, the name of the zip will most likely change with every OS update.
#           - Combining, sorting, and de-duping values from the following result in a list of supported models 
#                    - 'SupportedProductTypes' from 42e79bd54bb7295a5b729d32cb2493217f5d88f0/AssetData/boot/Restore.plist
#                    - 'SupportedModelProperties' from 42e79bd54bb7295a5b729d32cb2493217f5d88f0/AssetData/boot/PlatformSupport.plist


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
    '''Returns True if model is in list of supported models,
    False otherwise'''
    supported_models = [
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
    current_model = get_current_model()
    if not current_model:
        return False
    elif current_model in supported_models:
        return True
    else:
        return False

def get_minor_system_version():
    '''Returns 18 for Ventura, 17 for Monterey, 16 for Big Sur, etc.'''
    darwin_version = int(os.uname()[2].split('.')[0])
    return darwin_version - 4


def is_supported_system_version():
    '''Returns True if current macOS version is 10.12 through 12.x,
    False otherwise'''
    macos_minor_version = get_minor_system_version()
    if macos_minor_version >= 18:
        return False
    elif macos_minor_version >= 12:
        return True
    else:
        return False

def get_current_model():
    '''Returns model info'''
    return io_key_string_value("model")

def fact():
    '''Return our ventura_upgrade_supported fact'''
    if is_virtual_machine():
        return {'ventura_upgrade_supported': True}
    if ((is_supported_model()) and
            is_supported_system_version()):
        return {'ventura_upgrade_supported': True}
    return {'ventura_upgrade_supported': False}


if __name__ == '__main__':
    # Debug/testing output when run directly
    print('is_virtual_machine:          %s' % is_virtual_machine())
    print('get_current_model:           %s' % get_current_model())
    print('is_supported_model:          %s' % is_supported_model())
    print('get_minor_system_version:    %s' % get_minor_system_version())
    print('is_supported_system_version: %s' % is_supported_system_version())
    print(fact())
