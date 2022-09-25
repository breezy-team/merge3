#!/usr/bin/env python3
# encoding: utf-8

from setuptools import setup

with open('README.rst', 'r') as f:
    long_description = f.read()

setup(name="merge3",
      description="Python implementation of 3-way merge.",
      long_description=long_description,
      long_description_content_type='text/x-rst',
      version="0.0.9",
      maintainer="Breezy Developers",
      maintainer_email="team@breezy-vcs.org",
      license="GNU GPLv2 or later",
      url="https://www.breezy-vcs.org/",
      packages=['merge3'],
      test_suite='merge3.test_merge3',
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',  # noqa
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Operating System :: POSIX',
      ])
