## Introduction

munki_facts.py is an "admin-provided conditions" script for Munki as described [here.](https://github.com/munki/munki/wiki/Conditional-Items#admin-provided-conditions)

munki_facts.py is designed to be modular, allowing more 'facts' to be easily added without duplicating all of the code required to insert the facts into the ConditionalItems.plist.

Python modules that generate one or more facts live in the 'facts' subdirectory. They must have a 'fact()' function that returns a dictionary of keys and values.

Several sample fact modules are included.

## Usage

`munki_facts.py` and the `facts` directory should be installed in `/usr/local/munki/conditions`.
`munki_facts.py` must be marked as executable.

Munki will run `munki_facts.py` and insert any facts it generates into the dictionary of items that are used in [manifest `conditional_items` predicates](https://github.com/munki/munki/wiki/Conditional-Items) and in [`installable_condition` items in pkginfo files](https://github.com/munki/munki/wiki/Pkginfo-Files#installable_condition).

Any additional fact modules (that you create or obtain from others) should be copied into the `/usr/local/munki/conditions/facts` directory.

## Community Facts

Community-created facts can be found at the repositories below. 

Running additional facts will increase the time and resources required when managedsoftwarecenter checks in. It is recommended that you only add facts that you intend to use.

Please submit a pull request if you would like to add your munki-facts repo to the list.

| created by | repo | facts |
| ---------- | ---- | ----------- |
| [@nathanperkins](https://github.com/nathanperkins/) | [link](https://github.com/n8felton/munki-facts) | top_user_by_connect_time, top_user_by_num_logins, group_memberships |
| [@vmiller](https://github.com/vmiller) | [link](https://github.com/vmiller/munki-facts) | is_user_logged_in, logged_in_user |
