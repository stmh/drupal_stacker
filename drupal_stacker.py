#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fabric.api import *
from fabric.colors import green, red
import os, re, fabric

def help():
  print "Usage:"
  print "drupal_stacker.py [-h] [-o config_file] root_dir"

def get_configuration(config_file):

  conf = {
    'submodules': {},
    'symbolic_links':{},
    'git_ignore': [],
    'git_add': []
  }

  conf['submodules']['fabalicious'] = 'https://github.com/stmh/fabalicious.git'
  conf['submodules']['docker'] = 'https://github.com/stmh/drupal-docker.git'
  conf['submodules']['basebox'] = 'https://github.com/MuschPusch/basebox.git'

  conf['symbolic_links']['Vagrantfile'] = 'basebox/VagrantFile'
  conf['symbolic_links']['fabfile.py'] = 'fabalicious/fabfile.py'

  conf['git_ignore'].append('_tools/chive')
  conf['git_ignore'].append('fabfile.pyc')

  conf['git_add'] = [ 'Vagrantfile', 'fabfile.py', '.gitignore', '.vagrant' ]

  conf['drush_makefile'] = 'http://cgit.drupalcode.org/commons/plain/drupal-org-core.make'

  return conf

def copy_template(source, root_dir, target, replacements):

  template_in = os.path.dirname(os.path.realpath(__file__)) + "/" + source
  template_out = root_dir + "/" + target

  pattern = re.compile('|'.join(re.escape(key) for key in replacements.keys()))

  with open(template_out, 'w') as out:
    for line in open(template_in):
      line = pattern.sub(lambda x: replacements[x.group()], line)
      out.write(line)

  with lcd(root_dir):
    local('git add %s; git commit -m "create initial fabalicious configuration"' % target)

  print template_out + " written and committed."


def copy_fabfile(root_dir):

  print green('creating fabalicious configuration... ')

  print ""
  print "please provide some initial informations about your project:"
  print ""

  project_name  = fabric.operations.prompt("What is the human readable project name?       ")
  machine_name  = fabric.operations.prompt("What is the machine project name (only [az_]) ?")
  ip            = fabric.operations.prompt("What is the ip-address ?                       ")


  replacements = {
    '%%PROJECT_NAME%%': project_name,
    '%%IP%%': ip,
    '%%MACHINE_NAME%%': machine_name,
    '%%HOST_NAME%%': machine_name.replace('_', '-')
  }

  copy_template('fabfile.template.yaml', root_dir, 'fabfile.yaml', replacements)




def init_stack(conf, root_dir):

  print green('initing stack... ')

  local( 'mkdir -p %s' % root_dir )
  local( 'git init %s ' % root_dir )

  local( 'mkdir -p %s/_tools' % root_dir )

  with lcd(root_dir):
    for name, repo in conf['submodules'].items():
      local( 'git submodule add %s _tools/%s' % (repo, name))

    for filename, path in conf['symbolic_links'].items():
      local( 'ln -s _tools/%s %s' % (path, filename))

    for filepath in conf['git_ignore']:
      local( 'echo %s >> .gitignore' % (filepath) )

    for filepath in conf['git_add']:
      local( 'git add %s' % (filepath) )

    local( 'git commit -m "initial commit"' )


def run_make_file(root_dir,make_file):

  with lcd(root_dir):
    local('drush make %s public' % make_file)




@task
def init(root_dir = False, config_file=False, make_file=False):

  if not root_dir:
    help()

  conf = get_configuration(config_file)

  init_stack(conf, root_dir)

  copy_fabfile(root_dir)

  if 'drush_makefile' in conf:
    run_make_file(root_dir, conf['drush_makefile'])




