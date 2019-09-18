#!/usr/bin/env python

from __future__ import print_function  # for python 3 - print function compatibility
from __future__ import unicode_literals  # for python 2 - convert all strings to unicode

import os
import os.path
import re
import subprocess
import sys

from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.token import Token

prompt_style = style_from_dict({
    # User input.
    Token: '#ff0066',
    # Prompt.
    Token.Toolbar: '#ffffff bg:#000000',
})

completion_list = sorted(['feature', 'hotfix', 'help', 'exit', 'check', 'shell', 'lint', 'review'])
syntax_completer = (WordCompleter(completion_list))
history = InMemoryHistory()

version_file = '.version'
last_num = re.compile(r'(?:[^\d]*(\d+)[^\d]*)+')


def increment(s):
    """ look for the last sequence of number(s) in a string and increment """
    m = last_num.search(s)
    if m:
        next = str(int(m.group(1)) + 1)
        start, end = m.span(1)
        s = s[:max(end - len(next), start)] + next + s[end:]
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

        return 'Version file not found'


def get_git_version():
    git_version = subprocess.check_output(['git', 'version']).lstrip('git version ').split(' ')[0]
    return git_version


def get_all_branches():
    # --sort=-committerdate option only available in git 2.7+
    if get_git_version() > '2.7':
        proc = subprocess.check_output(['git', 'branch', '--sort=-committerdate']).replace('*', '').replace(' ',
                                                                                                            '').split(
            '\n')
    else:
        proc = subprocess.check_output(['git', 'branch']).replace('*', '').replace(' ', '').split('\n')

    return proc


def git_completer():
    git_completer = WordCompleter(get_all_branches())
    return git_completer


def get_diff():
    diff = subprocess.check_output(['git', 'diff'])
    return diff


def create_hotfix():
    print('Using mode: hotfix')

    # see if working tree is dirty

    # tree is clean
    if check_current_tree() == 0:

        # get current branch
        branch_name = subprocess.check_output(['git', 'symbolic-ref', '--short', 'HEAD']).strip()

        # we should be creating the hotfix from master
        if branch_name != 'master':

            confirm_switch_to_master = prompt('It looks like you\'re not on master. Do you want to switch to it? > ',
                                              completer=syntax_completer, style=prompt_style, history=history,
                                              get_bottom_toolbar_tokens=get_bottom_toolbar_tokens)

            if confirm_switch_to_master == 'y':
                # switch back to master before creating hotfix branch
                os.system('git checkout master')

        print('Going to grab latest code')
        continue_hotfix = prompt('Continue? > ', completer=syntax_completer, style=prompt_style, history=history,
                                 get_bottom_toolbar_tokens=get_bottom_toolbar_tokens)

        if continue_hotfix == 'y':

            get_latest_code()

            # get current version
            current_version = get_current_version(version_file)

            # increment version number
            new_version = increment(current_version)

            confirm_new_version = prompt('Do you want to bump to %s? (y/n) > ' % new_version,
                                         completer=syntax_completer, style=prompt_style, history=history,
                                         get_bottom_toolbar_tokens=get_bottom_toolbar_tokens)

            hotfix_name = 'hotfix-%s' % new_version

            if confirm_new_version == 'y':

                create_new_branch(hotfix_name)

                write_new_version(version_file, new_version)
                os.system('git add .version; git commit -m "Bumped to %s"' % new_version)

                print('Going to push hotfix branch')

                push_hotfix = prompt('Continue? > ', completer=syntax_completer, style=prompt_style, history=history,
                                     get_bottom_toolbar_tokens=get_bottom_toolbar_tokens)

                if push_hotfix == 'y':
                    push_branch(hotfix_name)


def finish_hotfix():
    print('Using mode: finish hotfix')

    current_version = get_current_version(version_file)

    confirm_merge = prompt('Do you want to merge into develop and master? > ', completer=syntax_completer,
                           style=prompt_style, history=history, get_bottom_toolbar_tokens=get_bottom_toolbar_tokens)

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
    print('Using mode: feature')

    # see if working tree is dirty

    # tree is clean
    if check_current_tree() == 0:

        feature_name = prompt('What is your feature called? > ', completer=syntax_completer, style=prompt_style,
                              history=history, get_bottom_toolbar_tokens=get_bottom_toolbar_tokens)

        print('Going to grab latest code and push new branch')
        continue_feature = prompt('Continue? > ', completer=syntax_completer, style=prompt_style, history=history,
                                  get_bottom_toolbar_tokens=get_bottom_toolbar_tokens)

        if continue_feature == 'y':
            get_latest_code()
            create_new_branch(feature_name)
            push_branch(feature_name)


def check_branch():
    branch = os.system('git show-branch remotes/origin/master')
    return branch


def get_bottom_toolbar_tokens():
    # get current version
    current_version = get_current_version(version_file)
    return [(Token.Toolbar, current_version)]


def graceful_exit():
    print('Bye!')
    sys.exit()


def get_current_branch():
    # get current branch
    try:
        branch_name = subprocess.check_output(['git', 'symbolic-ref', '--short', 'HEAD']).strip()
        return branch_name
    except:
        graceful_exit()


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

    pull_master = "git pull origin master"
    pull_master_ps = subprocess.Popen(pull_master, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    pull_master_output = pull_master_ps.communicate()[0].strip()

    # check for merge conflicts and then handle them
    if 'Automatic merge failed' in pull_master_output:
        print('Merge conflicts found. Please fix them before continuing')
        sys.exit()
    # get latest code from develop
    # subprocess.check_output(['git', 'checkout', 'develop'])
    # subprocess.check_output(['git', 'pull', 'origin', 'develop'])

    print(pull_master_output)


def handle_merge_conflicts():
    print('Handling merge conflicts')


def check_current_tree():
    # get amount of files in working tree
    not_staged = "git diff-index HEAD | wc -l"
    not_staged_ps = subprocess.Popen(not_staged, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    not_staged_output = not_staged_ps.communicate()[0].strip()

    stash_status = 0

    if not_staged_output != '0':

        print('Current working tree is dirty')
        print('Unstaged files: %s' % not_staged_output)

        text = prompt('Stash changes? > ', completer=syntax_completer,
                      style=prompt_style, history=history, get_bottom_toolbar_tokens=get_bottom_toolbar_tokens)

        if text.strip() == 'y':

            stash_files()
            stash_status = 0

        elif text.strip() == 'n':

            print('Pulling the latest code is probably going to fail. Exiting feature mode')
            stash_status = 1

    return stash_status


def stash_files():
    stash_files = os.system('git add -u; git stash save;')
    return stash_files


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
                        print(':%s ' % line_number + line.strip('\n'))


def shell():
    print('Type \'exit\' to return to gitflow')
    command = prompt('Command to run > ', completer=syntax_completer, style=prompt_style, history=history,
                     get_bottom_toolbar_tokens=get_bottom_toolbar_tokens)
    os.system(command)
    if 'exit' not in command:
        shell()


def get_bottom_toolbar_tokens():
    toolbar_content = '<' + (get_current_version(version_file) + '> <' + get_current_branch() + '>')
    return [(Token.Toolbar, toolbar_content)]


def update_gitflow():
    # get latest gitflow version
    gitflow_symlink_path = os.readlink(__file__)
    gitflow_file_path = gitflow_symlink_path.replace('gitflow.py', '')
    update_file_path = gitflow_symlink_path.replace('gitflow.py', 'update.py')
    current_project_path = os.getcwd()

    if os.path.exists(update_file_path):
        os.chdir(gitflow_file_path)
        exec (open(update_file_path))
        os.chdir(current_project_path)

logo = """
        .__  __    _____.__                 
   ____ |__|/  |__/ ____\  |   ______  _  ___
  / ___\|  \   __\   __\|  |  /  _ \ \/ \ / /
 / /_/  >  ||  |  |  |  |  |_(  <_> )      / 
 \___  /|__||__|  |__|  |____/\____/ \_/\_/  
/_____/
                                                
Type a command and press enter:
"""

os.system('clear')

# get latest gitflow version
update_gitflow()

# start gitflow cli
os.system('clear')

try:

    text = prompt(logo + '> ', completer=syntax_completer, style=prompt_style, history=history,
                  get_bottom_toolbar_tokens=get_bottom_toolbar_tokens)

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
            print('\033[1m' + 'COMMANDS' + '\033[0m')
            print('\033[1m' + 'hotfix' + '\033[0m')
            print('     Create a hotfix branch')
            print('\033[1m' + 'feature' + '\033[0m')
            print('     Create a feature branch')
            print('\033[1m' + 'shell' + '\033[0m')
            print('     Open a shell command prompt. Type exit to return to gitflow')
            print('\033[1m' + 'lint' + '\033[0m')
            print('     Lint changed files for debug statements')
            print('\033[1m' + 'check' + '\033[0m')
            print('    Check if current branch exists on remote')

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

        elif text.strip() == 'shell':
            shell()

    except EOFError:

        graceful_exit()

    except KeyboardInterrupt:

        graceful_exit()

    # main prompt
    try:

        text = prompt('> ', completer=syntax_completer, style=prompt_style, history=history,
                      get_bottom_toolbar_tokens=get_bottom_toolbar_tokens)

    except EOFError:

        graceful_exit()

    except KeyboardInterrupt:

        graceful_exit()
