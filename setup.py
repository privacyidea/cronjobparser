# -*- coding: utf-8 -*-
from distutils.core import setup

setup(name='crontabparser',
      version='0.1',
      description='Parser for /etc/crontab',
      author='Cornelius Kölbel',
      author_email='cornelius.koelbel@netknights.it',
      url='https://github.com/privacyidea/crontabparser',
      py_modules=['crontabparser'],
      install_requires=[
            'pyparsing>=2.0',
            'six'
      ]
      )
