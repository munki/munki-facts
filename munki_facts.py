#!/usr/bin/python
'''Processes python modules in the facts directory and adds the info they
return to our ConditionalItems.plist'''

import imp
import os
import sys
import plistlib
from xml.parsers.expat import ExpatError

# pylint: disable=no-name-in-module
from CoreFoundation import CFPreferencesCopyAppValue
# pylint: enable=no-name-in-module


def main():
    '''Run all our fact plugins and collect their data'''
    module_dir = os.path.join(os.path.dirname(__file__), 'facts')
    facts = {}

    # find all the .py files in the 'facts' dir
    fact_files = [
        os.path.splitext(name)[0]
        for name in os.listdir(module_dir)
        if name.endswith('.py') and not name == '__init__.py']

    for name in fact_files:
        # load each file and call its fact() function
        filename = os.path.join(module_dir, name + '.py')
        try:
            module = imp.load_source(name, filename)
            facts.update(module.fact())
        except BaseException, err:
            print >> sys.stderr, u'Error %s in file %s' % (err, filename)

    if facts:
        # Handle cases when facts return None - convert them to empty
        # strings.
        for key, value in facts.items():
            if value is None:
                facts[key] = ''
        # Read the location of the ManagedInstallDir from ManagedInstall.plist
        bundle_id = 'ManagedInstalls'
        pref_name = 'ManagedInstallDir'
        managedinstalldir = CFPreferencesCopyAppValue(pref_name, bundle_id)
        conditionalitemspath = os.path.join(
            managedinstalldir, 'ConditionalItems.plist')

        conditional_items = {}
        # read the current conditional items
        if os.path.exists(conditionalitemspath):
            try:
                conditional_items = plistlib.readPlist(conditionalitemspath)
            except (IOError, OSError, ExpatError), err:
                pass

        # update the conditional items
        conditional_items.update(facts)

        # and write them out
        try:
            plistlib.writePlist(conditional_items, conditionalitemspath)
        except (IOError, OSError), err:
            print >> sys.stderr, 'Couldn\'t save conditional items: %s' % err


if __name__ == "__main__":
    sys.exit(main())
