#!/usr/bin/python

from __future__ import unicode_literals # for python 2 - convert all strings to unicode

import re
import os
import sys
import getopt
import os.path
import subprocess

from prompt_toolkit import prompt
from prompt_toolkit.contrib.completers import WordCompleter

from prompt_toolkit.token import Token
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.styles import style_from_dict

import getpass

example_style = style_from_dict({
    # User input.
    Token:          '#ff0066',

    # Prompt.
    Token.Username: '#884444',
    Token.At:       '#00aa00',
    Token.Colon:    '#00aa00',
    Token.Pound:    '#00aa00',
    Token.Host:     '#000088 bg:#aaaaff',
    Token.Path:     '#884444 underline',
    Token.Toolbar: '#ffffff bg:#333333',
})

syntax_completer = WordCompleter(['start', 'finish', 'hotfix', 'help', 'exit', 'check'])
# text = prompt(get_prompt_tokens=get_prompt_tokens, style=example_style, completer=syntax_completer)


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
            # print 'Current version is %s..' % first_line

            current = first_line
            # current = 'Current version is %s ' % first_line

            return current
    else:

        print 'Version file not found'


def hotfix():

    print 'Using mode: hotfix'

    # print '----------'
    # print 'Updating branches'
    # print '----------'

    # make sure we have the latest changes
    os.system('git checkout master; git pull origin master;')
    os.system('git checkout develop; git pull origin develop;')
    os.system('git checkout master;')

    # get current version
    current_version = get_current_version(version_file)

    # increment version number
    new_version = increment(current_version)

    # print 'Do you want to bump to %s? (y/n)' %new_version
    # confirm_new_version = raw_input(':')

    confirm_new_version = prompt('Do you want to bump to %s? (y/n) > ' %new_version, completer=syntax_completer, style=example_style, )


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


def check_branch():
    branch = os.system('git show-branch remotes/origin/master')
    return branch


def get_bottom_toolbar_tokens(cli):
    # get current version
    current_version = get_current_version(version_file)
    return [(Token.Toolbar, current_version)]


logo = """
      :::::::::   :::::::: 
     :+:    :+: :+:    :+: 
    +:+    +:+ +:+         
   +#++:++#+  :#:          
  +#+    +#+ +#+   +#+#    
 #+#    #+# #+#    #+#     
#########   ########       

Type a command and press enter:
"""


logo = """
        .__  __    _____.__                 
   ____ |__|/  |__/ ____\  |   ______  _  ___
  / ___\|  \   __\   __\|  |  /  _ \ \/ \ / /
 / /_/  >  ||  |  |  |  |  |_(  <_> )      / 
 \___  /|__||__|  |__|  |____/\____/ \_/\_/  
/_____/  v1.0.0                                   
                                                
Type a command and press enter:
"""


# start gitflow cli

os.system('clear')

try:

    text = prompt(logo + '> ', style=example_style, completer=syntax_completer, vi_mode=True)

except EOFError:

    print 'Bye!'
    sys.exit()

except KeyboardInterrupt:

    print 'Bye!'
    sys.exit()


# keep prompt running
while True:

    try:

        if text.strip() == 'exit':
            break

        elif text.strip() == 'help':
            print 'Check if current branch exists: check'
            print 'Enter hotfix mode: hotfix'
            print 'Exit gitflow: exit'
            print 'Show current logfile: show log'

        elif text.strip() == 'hotfix' or text.strip() == 'start':
            hotfix()

        elif text.strip() == 'check':
            check_branch()

    except EOFError:

        print 'Bye!'

    except:

        pass

    text = prompt('> ', completer=syntax_completer, style=example_style, )
    # text = prompt('> ', completer=syntax_completer, get_bottom_toolbar_tokens=get_bottom_toolbar_tokens, style=example_style, )


def main(argv):

    # read arguments
    for arg in sys.argv:
        # print arg
        if arg == "-h":
            print 'Create a hotfix: gitflow hotfix OR gitflow start'
            print 'Finish a hotfix: gitflow finish-hotfix OR gitflow finish'
            sys.exit()
        if arg == 'hotfix' or arg == 'start':
            hotfix()
        if arg == 'finish-hotfix' or arg == 'finish':
            finish_hotfix()

if __name__ == "__main__":
    main(sys.argv[1:])
