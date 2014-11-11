#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fabric.api import *
from fabric.colors import green, red
import os, re, fabric
import yaml


def help():
  print "Usage:"
  print "drupal_stacker.py [-h] [-o config_file] root_dir"

def get_configuration(config_file):

  if not config_file:
    config_file = "standard.yaml"

  try:
    stream = open(config_file, 'r')
  except IOError:
    config_file = os.path.dirname(os.path.realpath(__file__)) + "/" + config_file
    try:
      stream = open(config_file, 'r')
    except:
      print red("Could not find configuration-file.")
      sys.exit(2)


  conf = yaml.load(stream)

  for key in ('submodules', 'symbolic_links', 'git_add'):
    if not key in conf:
      print red('Missing key in configuration-file: %s' % key)
      sys.exit(2)

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
    local('git add %s; git commit -m "create initial %s"' % (target, target) )

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

  if make_file:
    run_make_file(root_dir, conf['drush_makefile'])

  elif 'drush_makefile' in conf:
    run_make_file(root_dir, conf['drush_makefile'])




