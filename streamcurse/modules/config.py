import os
import configparser

# c = config.Conf()
class Conf:
	version='1.1'
	# our config object
	c = configparser.ConfigParser()

	# some globals
	if 'XDG_CONFIG_HOME' in os.environ:
		confdir = os.environ['XDG_CONFIG_HOME']
	elif 'CONFIG' in os.environ:
		confdir = os.environ['CONFIG']
	else:
		confdir = os.path.join(os.path.expanduser('~'), '.config')
	default_dir=os.path.join(confdir, 'streamcurse')
	database_dir=os.path.join(default_dir, 'databases')
	default_cfg=os.path.join(default_dir, 'config.ini')
	default_db='default.db'

	def __init__(self):
		# if our prog path does not exist, create it
		if not os.path.exists(self.default_dir):
			os.makedirs(self.default_dir)
		# if our database dir is not there create it
		if not os.path.exists(self.database_dir):
			os.makedirs(self.database_dir)

	# load our users config and return it for use
	def load(self, file=None):
		# if file wasnt passed then use the default
		if not file:
			file=self.default_cfg

		# if config exists load it, else create it
		if os.path.exists(file):
			self.c.read(file)
			return(self.c)

		# if its the default config and it doesnt exist create one else complain
		elif file == self.default_cfg:
			self.create()
			return(self.c)
		else:
			print(file, 'does not exist')
			exit()

	# function for creating a default config
	def create(self, file=None):
		print('creating config')
		# if file wasnt passed then use the default
		if not file:
			file=self.default_cfg

		# this will be the default configuration file
		self.c['DIRECTORY'] = {
				'database'    : self.default_db,
				'database_dir': self.database_dir
				}
		self.c['THEME'] = {
				'title'       :'blue white',
				'header'      :'white blue',
				'select'      :'blue white',
				'footer'      :'white blue',
				'status'      :'blue white',
				}
		self.c['COMMANDS'] = {
				'cmd1'        :'mpv',
				'cmd2'        :'streamlink __urlhere__ best',
				'cmd3'        :'cvlc',
				}
		#self.c['TWITCH'] = {
		#		'username'    :'None'
		#		}
		self.c['INDICATORS'] = {
				'offline'     :'---',
				'playing'     :'[>]',
				'online'      :'>>>',
				'error'       :'!!!',
				}

		# write the config file
		with open(file, 'w') as configfile:
			self.c.write(configfile)
