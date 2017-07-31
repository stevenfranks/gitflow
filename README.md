# Installation

### Clone project

`git clone git@code:bg/gitflow.git`

### Create symlink (optional)

Go to `/usr/local/bin` and run `ln -s path/to/gitflow.py gitflow`

You can now run `gitflow hotfix` within a project directory

# Usage

## Hotfixes

### Start a hotfix

`gitflow hotfix` or `python gitflow.py hotfix`

This will;
* Create hotfix branch and switch to it
* Increment current version


### Finish a hotfix

`gitflow finish-hotfix` or `python gitflow.py finish-hotfix`

This will;

* Merge hotfix branch into develop and master
