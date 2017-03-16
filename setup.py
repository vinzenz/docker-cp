#!/usr/bin/env python

from distutils.core import setup

setup(name='docker_copy',
      version='0.1',
      description='Copies files/folders from and to containers',
      author='Vinzenz Feenstra',
      author_email='evilissimo@redhat.com',
      url='https://github.com/vinzenz/docker-cp',
      packages=['docker_copy'],
      install_requires=['docker>=2.1.0'],
      entry_points={
          'console_scripts': ['docker-cp=docker_copy:main']})
