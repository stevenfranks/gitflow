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

syntax_completer = WordCompleter(['start', 'finish', 'feature', 'hotfix', 'help', 'exit', 'check'])
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


def create_hotfix():

    print 'Using mode: hotfix'

    # see if working tree is dirty

    # tree is clean
    if check_current_tree() == 0:

        # get current version
        current_version = get_current_version(version_file)

        # increment version number
        new_version = increment(current_version)

        confirm_new_version = prompt('Do you want to bump to %s? (y/n) > ' %new_version, completer=syntax_completer, style=example_style, )

        if confirm_new_version == 'y':

            # get current branch
            branch_name = subprocess.check_output(['git', 'symbolic-ref', '--short', 'HEAD']).strip()

            # we should be creating the hotfix from master
            if branch_name != 'master':

                confirm_switch_to_master =  prompt('It looks like you\'re not on master. Do you want to switch to it? > ', completer=syntax_completer, style=example_style, )

                if confirm_switch_to_master == 'y':

                    # switch back to master before creating hotfix branch
                    os.system('git checkout master')


            hotfix_name = 'hotfix-%s' % new_version

            print 'Going to grab latest code and push new branch'
            continue_hotfix = prompt('Continue? > ', completer=syntax_completer, style=example_style, )

            if continue_hotfix == 'y':

                get_latest_code()
                create_new_branch(hotfix_name)
                push_branch(hotfix_name)

                write_new_version(version_file, new_version)
                os.system('git add .version; git commit -m "Bumped to %s"' % new_version)


def finish_hotfix():

    print 'Using mode: finish hotfix'

    current_version = get_current_version(version_file)

    confirm_merge = prompt('Do you want to merge into develop and master? > ', completer=syntax_completer, style=example_style, )

    if confirm_merge == 'y':

        # merge into develop
        os.system('git checkout develop; git merge --no-ff --no-edit hotfix-%s' % current_version)
        # merge into master
        os.system('git checkout master; git merge --no-ff --no-edit hotfix-%s' % current_version)

        # print '----------'
        # print 'Finished hotfix.. Exiting'
        # print 'Don\'t forget to tag!'
        # print '----------'

def create_feature():

    print 'Using mode: feature'

    # see if working tree is dirty

    # tree is clean
    if check_current_tree() == 0:

        feature_name = prompt('What is your feature called? > ', completer=syntax_completer, style=example_style, )

        print 'Going to grab latest code and push new branch'
        continue_feature = prompt('Continue? > ', completer=syntax_completer, style=example_style, )

        if continue_feature == 'y':

            get_latest_code()
            create_new_branch(feature_name)
            push_branch(feature_name)


def check_branch():
    branch = os.system('git show-branch remotes/origin/master')
    return branch


def get_bottom_toolbar_tokens(cli):
    # get current version
    current_version = get_current_version(version_file)
    return [(Token.Toolbar, current_version)]

def graceful_exit():
    print 'Bye!'
    sys.exit()

def get_current_branch():
    # get current branch
    branch_name = subprocess.check_output(['git', 'symbolic-ref', '--short', 'HEAD']).strip()
    return branch_name

def create_new_branch(new_branch):
    # create new branch
    new_branch = subprocess.check_output(['git', 'checkout', '-b', new_branch]).strip()
    return new_branch

def push_branch(new_branch):
    # push new branch
    push_branch = subprocess.check_output(['git', 'push', 'origin', new_branch]).strip()
    return push_branch

def get_latest_code():
    # get latest code from master
    subprocess.check_output(['git', 'checkout', 'master'])
    subprocess.check_output(['git', 'pull', 'origin', 'master'])
    # get latest code from develop
    # subprocess.check_output(['git', 'checkout', 'develop'])
    # subprocess.check_output(['git', 'pull', 'origin', 'develop'])


def check_current_tree():
    # get amount of files in working tree
    not_staged = "git diff-index HEAD | wc -l"
    not_staged_ps = subprocess.Popen(not_staged, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    not_staged_output = not_staged_ps.communicate()[0].strip()

    stash_status = 0

    if not_staged_output != '0':

        print 'Current working tree is dirty'
        print 'Unstaged files: %s' % not_staged_output
        
        text = prompt('Stash changes? > ', completer=syntax_completer,
                      style=example_style, )

        if text.strip() == 'y':

            stash_files()
            stash_status = 0

        elif text.strip() == 'n':

            print 'Pulling the latest code is probably going to fail. Exiting feature mode'
            stash_status = 1

    return stash_status


def stash_files():
    stash_files = os.system('git add -u; git stash save;')


def lint_files():
    # get changed files
    files = subprocess.check_output(['git', 'diff', '--name-only']).split('\n')
    # look for debug statements
    for file in files:
        if os.path.exists(file):
            with open(file, 'r') as f:
                line_number = 0
                for line in f:
                    line_number = line_number + 1
                    if 'console.log' in line or 'print_me' in line or 'var_dump' in line or 'error_log' in line:
                        print ':%s ' % line_number + line.strip('\n')


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
/_____/  %s    %s                              
                                                
Type a command and press enter:
""" % (get_current_version(version_file), get_current_branch())


# start gitflow cli

os.system('clear')

try:

    text = prompt(logo + '> ', style=example_style, completer=syntax_completer, vi_mode=True)

except EOFError:

    graceful_exit()

except KeyboardInterrupt:

    graceful_exit()


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
            create_hotfix()

        elif text.strip() == 'check':
            check_branch()

        elif text.strip() == 'finish':
            finish_hotfix()

        elif text.strip() == 'feature':
            create_feature()

        elif text.strip() == 'checktree':
            check_current_tree()

        elif text.strip() == 'lint':
            lint_files()

    except EOFError:

        graceful_exit()

    except KeyboardInterrupt:

        graceful_exit()

    except:

        pass


    # main prompt
    try:

        text = prompt('> ', completer=syntax_completer, style=example_style, vi_mode=True)

    except EOFError:

        graceful_exit()

    except KeyboardInterrupt:

        graceful_exit()
