#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@date: 2012-05-03
@author: shell.xu
'''
from distutils.core import setup

version = '1.7'
description = 'toolset for cross GFW'
long_description = ' toolset for cross GFW, include such tools.\
  * auto start multi ssh tunnel\
  * http proxy use socks as upstream\
  * dns proxy use tcp over ssh'

setup(name='antigfw', version=version,
      description=description, long_description=long_description,
      author='Shell.E.Xu', author_email='shell909090@gmail.com',
      scripts=['gfw_tester', 'dns2tcp'], packages=['uniproxy',],
      data_files=[('share/uniproxy', ['dnsfake', 'gfw.gz', 'routes.list.gz']),
                  ('/etc/uniproxy', ['debian/gfw'])])
