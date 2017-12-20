# Installation

### Clone project

`git clone git@code:bg/gitflow.git`

### Install Requirements

`python install setup.py`

### Create symlink (optional)

Go to `/usr/local/bin` and run `ln -s path/to/gitflow.py gitflow`

You can now run `gitflow` within a project directory to start the CLI

# Usage

## Hotfixes

### Start a hotfix

Type `hotfix` and press `Enter`

This will;
* Create hotfix branch and switch to it
* Increment current version


### Finish a hotfix

Type `finish` and press `Enter`

This will;

* Merge hotfix branch into develop and master
