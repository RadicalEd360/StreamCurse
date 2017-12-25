#!/usr/bin/env python

from setuptools import setup
from os.path import join, dirname, abspath
from sys import path

srcdir = join(dirname(abspath(__file__)), "src/")
path.insert(0, srcdir)

from streamlink_curses import config

setup(name="streamlink-curses",
      version=config.VERSION,
      description="streamlink-curses is a curses frontend to streamlink",
      url="http://github.com/gapato/livestreamer-curses",
      author="Gapato",
      author_email="g@oknaj.eu",
      license="MIT",
      packages = [ "streamlink_curses" ],
      package_dir={ "": "src" },
      install_requires=["streamlink"],
      entry_points={
          "console_scripts": ["streamlink-curses=streamlink_curses.main:main"]
      },
      classifiers=["Operating System :: POSIX",
                  "Programming Language :: Python :: 2",
                  "Programming Language :: Python :: 3",
                   "Environment :: Console :: Curses",
                   "Development Status :: 4 - Beta",
                   "License :: OSI Approved :: MIT License",
                   "Topic :: Utilities"]
)
