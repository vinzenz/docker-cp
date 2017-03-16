#!/usr/bin/env python

from distutils.core import setup

setup(name='docker_copy',
      version='0.1',
      description='Copies files/folders from and to containers',
      author='Vinzenz Feenstra',
      author_email='evilissimo@redhat.com',
      url='',
      packages=['docker_copy'],
      entry_points={
          'console_scripts': ['docker-cp=docker_copy:main']})
