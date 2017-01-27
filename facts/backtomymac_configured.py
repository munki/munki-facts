'''Return a boolean indicating if BackToMyMac is configured on this machine'''

from SystemConfiguration import SCDynamicStoreCopyValue

def fact():
    '''Return True if there is a value for SystemConfiguration's
    Setup:/Network/BackToMyMac key'''
    return {'backtomymac_configured':
            SCDynamicStoreCopyValue(None, 'Setup:/Network/BackToMyMac')
            is not None}

if __name__ == '__main__':
    print fact()