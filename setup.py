#!/usr/bin/env python

from setuptools import setup

setup(name="streamcurse",
      version='1.1',
      description="streamcurse is a curses stream launcher, inspired by gapatos livestreamer-curses.",
      url="https://github.com/RadicalEd360/streamcurse",
      author="Radical Edward",
      author_email="Radical.Ed360@gmail.com",
      license="MIT",
      packages = ['streamcurse','streamcurse.modules'],
      package_data={"": ["*.txt"] },
      install_requires=["streamlink"],
      entry_points={
          "console_scripts": ["streamcurse=streamcurse.main:main"]
      },
      classifiers=["Operating System :: POSIX",
                  "Programming Language :: Python :: 3",
                   "Environment :: Console :: Curses",
                   "Topic :: Utilities"]
)
