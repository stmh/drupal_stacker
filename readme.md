# drupal_stacker

drupal_stacker is a small python-script to setup a drupal stack from the beginning using [Fabric](http://www.fabfile.org/en/latest/)

In its current form it will create a folder, add a _tools-folder and add the following github repositories as submodules:

* [fabalicious](https://github.com/stmh/fabalicious) a fagric-based deployment-tool with support for docker, drupal and drush
* [drupal-docker](https://github.com/stmh/drupal-docker) a Dockerfile suitable for drupal-installations and some helper-scripts.
* [baseBox](https://github.com/MuschPusch/basebox) provides a vagrant based virtual machine running a docker-instance


## Installation

drupal_stacker needs fabric:

on Mac OS X:

    brew install python
    pip install fabric
    pip install pyyaml


on Debian/Ubuntu:

    apt-get install python-pip
    pip install fabric
    pip install pyyaml


Copy the folder to a suitable folder on your hard-drive

## Usage

drupal_stacker provides currently only one task

    fab -f /path/to/drupal_stacker.py init:<project-path>

This will create the folder <project-path>, init a git-repository, add the submodules, add some symlinks, create a fabalicious-config-file and run a drush-makefile for a standard drupal-installation

As an alternative you can use a separate configuration-file:

    fab -f /path/to/drupal_stacker.py init:root_dir=<project-path>,config_file=<path-to-config-file.yaml>



