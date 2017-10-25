#!/usr/bin/python

import re
import os
import sys
import getopt
import os.path
import subprocess

# print 'Number of arguments:', len(sys.argv), 'arguments.'
# print 'Argument List:', str(sys.argv)

version_file = '.version'
lastNum = re.compile(r'(?:[^\d]*(\d+)[^\d]*)+')

def increment(s):
    """ look for the last sequence of number(s) in a string and increment """
    m = lastNum.search(s)
    if m:
        next = str(int(m.group(1))+1)
        start, end = m.span(1)
        s = s[:max(end-len(next), start)] + next + s[end:]
    return s

def write_new_version(version_file, new_version):

    with open(version_file, 'w') as nf:
        nf.truncate()
        nf.write(str(new_version))

def get_current_version(version_file):

    if os.path.exists(version_file):

        with open(version_file, 'r') as f:

            # get current version
            first_line = f.readline().strip()
            print 'Current version is %s..' % first_line

            current = first_line

            return current
    else:

        print 'Version file not found.. Exiting'
        sys.exit()

def hotfix():

    print 'Using mode: hotfix'

    print '----------'
    print 'Updating branches'
    print '----------'

    # make sure we have the latest changes
    os.system('git checkout master; git pull origin master;')
    os.system('git checkout develop; git pull origin develop;')
    os.system('git checkout master;')

    # get current version
    current_version = get_current_version(version_file)

    # increment version number
    new_version = increment(current_version)

    print 'Do you want to bump to %s? (y/n)' %new_version
    confirm_new_version = raw_input(':')

    if confirm_new_version == 'y':

        # get current branch
        branch_name = subprocess.check_output(['git', 'symbolic-ref', '--short', 'HEAD']).strip()

        # we should be creating the hotfix from master
        if branch_name != 'master':

            print 'It looks like you\'re not on master. Do you want to switch to it?'

            confirm_switch_to_master = raw_input(':')

            if confirm_switch_to_master == 'y':

                # switch back to master before creating hotfix branch
                os.system('git checkout master')

        # check out new branch
        print 'Checking out new hotfix branch..'
        os.system('git checkout -b hotfix-%s' % new_version)

        # bump version
        print 'Bumping version..'
        write_new_version(version_file, new_version)
        os.system('git add .version; git commit -m "Bumped to %s"' % new_version)

        print '----------'
        print 'Finished creating hotfix.. Exiting'
        print 'Run \'gitflow finish-hotfix\' when you\'re done'
        print '----------'

def finish_hotfix():

    print 'Using mode: finish hotfix'

    current_version = get_current_version(version_file)

    print 'Do you want to merge into develop and master? (y/n)'
    confirm_merge = raw_input(':')

    if confirm_merge == 'y':

        # merge into develop
        os.system('git checkout develop; git merge --no-ff --no-edit hotfix-%s' % current_version)
        # merge into master
        os.system('git checkout master; git merge --no-ff --no-edit hotfix-%s' % current_version)

        print '----------'
        print 'Finished hotfix.. Exiting'
        print 'Don\'t forget to tag!'
        print '----------'

def main(argv):

    # read arguments
    for arg in sys.argv:
        # print arg
        if arg == "-h":
            print 'Create a hotfix: gitflow.py hotfix'
            print 'Finish a hotfix: gitflow.py finish-hotfix'
            sys.exit()
        if arg == 'hotfix':
            hotfix()
        if arg == 'finish-hotfix':
            finish_hotfix()

if __name__ == "__main__":
    main(sys.argv[1:])
