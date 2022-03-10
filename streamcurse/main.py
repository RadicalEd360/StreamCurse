#!/usr/bin/env python3
###################################################################################################################
#     Copyright 2018 @ Radical Edward - Radical.Ed360@gmail.com
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
###################################################################################################################
import argparse
import os
from curses import wrapper

from .modules import config as config
from .modules import databases as db
from .modules.interface import InterFace

def main():
	parser = argparse.ArgumentParser(description='StreamCurse, flexible stream launcher')

	try:
		arg_type = unicode
	except:
		arg_type = str

	parser.add_argument('-g', type=arg_type, metavar='configfile', help='generate a default config file')

	args = parser.parse_args()


	c = config.Conf()

	# -g generate a new config
	if args.g:
		c.create(file=args.g)
		print('generated:', args.g)
		exit()

	# load the config
	conf = c.load()

	default_database = os.path.join(conf['DIRECTORY']['database_dir'], conf['DIRECTORY']['database'])
	if not os.path.exists(default_database):
		db.create(default_database)
	data = default_database

	mode = 'normal'

	l = InterFace(conf, data, mode)
	wrapper(l)

if __name__ == "__main__":
	main()
