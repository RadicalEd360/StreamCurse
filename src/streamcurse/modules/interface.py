#!/usr/bin/env python3
# this will have all the curses things here

from multiprocessing.pool import ThreadPool as Pool
from time import sleep
import streamlink
import curses
import shlex
import queue
import os

from . import databases as db
from . import services
from . import player
from . import config

class QueueFull(Exception): pass
class QueueDuplicate(Exception): pass


class InterFace:
	'interface for streamlink curses'
	version='v1.0'
	"""---------------------------------------------------------- initialization """
#-------------------------------------------------------------startup variables
	startpos = 0
	selection = 0
	filter=''
	show_offline_streams = 1
	checked_online = []
	nowindow = False
	nodata = True
	database_list = []
	dbnumber = 0
	dbname = 'null'
	got_g = False

	def __init__(self, conf, dbfile, mode):
#--------------------------------------------------------------------------args
		self.conf = conf
		self.mode = mode
		self.dbfile = dbfile
#-----------------------------------------------------------------configuration
		self.dbpath = conf['DIRECTORY']['database_dir']
		self.twitch_username = conf['TWITCH']['username']

		cmd_list = []
		for cmd in conf['COMMANDS']:
			cmd_list.append(conf['COMMANDS'][cmd])
		self.cmd_list = list(map(shlex.split, cmd_list))
		self.cmd_index = 0
		self.cmd = self.cmd_list[self.cmd_index]
#-----------------------------------------------------------------------objects
		self.twitch = services.Twitch()
		self.streamlink = streamlink.Streamlink()
		self.q = player.ProcessList(player.StreamPlayer().play)
#-------------------------------------------------------------establich history
		self.currentpad = 'main'
		self.prevpad = self.currentpad
		self.prevdb = self.dbfile
#------------------------------------------------------------------static texts
		#res = os.path.abspath(os.path.join(os.path.dirname(__file__), 'resources'))
		res = os.path.abspath(os.path.dirname(__file__))
		with open(os.path.join(res, 'help.txt'), 'r') as handle:
			self.helpmenu = handle.readlines()

		with open(os.path.join(res, 'firstrun.txt'), 'r') as handle:
			self.firstrun = handle.readlines()
#------------------------------------------------------------------------------

	def __call__(self, s):
		self.s = s # self.s is our stdscr
		self.refreshall()
		self.run()

	""" ------------------------------------------------------------------Interface setup and run """
	# normal mode only
	def loaddata(self):
		if self.database_list == []:
			self.database_list = [f for f in os.listdir(self.dbpath) if os.path.isfile(os.path.join(self.dbpath, f))]
		#self.dbfile = os.path.join(self.dbpath, self.database_list[self.dbnumber])
		self.database = db.load(self.dbfile)
		if self.dbfile not in self.checked_online:
			for stream in self.database:
				stream['online'] = 0
			self.savedb()
		self.nodata = False
		self.filter_streams()
		self.dbname = self.database_list[self.dbnumber]
		if self.database == []:
			self.mode = 'firstrun'
		else:
			self.mode = 'normal'

	def savedb(self):
		db.save(self.database, self.dbfile)

	# non normal mode only
	def loadcache(self):
		self.dbfile = '/tmp/sc-cache-twitch'
		if not os.path.exists(self.dbfile):
			db.create(self.dbfile)
			data = self.twitch.getfollows(self.twitch_username)
			db.save(data, self.dbfile)
		self.database = db.load(self.dbfile)
		self.nodata = False
		self.filter_streams()
		if self.database == []:
			self.mode = 'firstrun'
		else:
			self.mode = 'twitch'

	# non normal modes only
	def clearcache(self):
		self.dbfile = '/tmp/sc-cache-twitch'
		if os.path.exists(self.dbfile):
			os.remove(self.dbfile)
		else:
			return

	def init(self):
		self.maxY, self.maxX = self.s.getmaxyx()
		self.bodyMaxY, self.bodyMaxX = self.maxY - 4, self.maxX
		self.s.nodelay(0)

#----------------------------------------------------------------------------------------
		if self.nodata == True:
			if self.mode == 'normal':
				self.loaddata()
			if self.mode == 'twitch':
				self.loadcache()
		else:
			self.filter_streams()
#----------------------------------------------------------------------------------------

		self.title  = self.s.subwin(1, self.maxX, 0, 0)
		self.header = self.s.subwin(1, self.maxX, 1, 0)
		self.footer = self.s.subwin(1, self.maxX, self.maxY -2, 0)
		self.status = self.s.subwin(1, self.maxX, self.maxY -1, 0)

		self.body = curses.newpad(self.maxY - 4, self.maxX)

		self.body.keypad(1) # allow use of arrow keys
		curses.curs_set(0) # stop the cursor from showing up
#----------------------------------------------------------------------------------------

	def settexts(self):
		if self.currentpad == 'main':
			self.header.erase()
			self.title.erase()
			self.footer.erase()
			if self.mode == 'twitch':
				self.header.addstr(0, 0, ' No.')
				self.header.addstr(0, 5 + 1, 'Streamer')
				self.header.addstr(0, 25 + 3, 'Game')
				self.header.addstr(0, self.bodyMaxX - 10, 'Status')
			if self.mode == 'normal':
				self.header.addstr(0, 0, ' No.')
				self.header.addstr(0, 5 + 1, 'Name')
				self.header.addstr(0, self.bodyMaxX - 10, 'Status')

		if self.currentpad == 'help':
			self.header.erase()
			self.footer.erase()
			msg='up/down q to exit menu'
#			self.footer.addstr(0, 3, 'up/down q to exit')
			self.footer.addstr(0, int(int(self.maxX - len(msg))/2), msg)

		if self.mode == 'firstrun' or self.currentpad == 'help':
			msg='StreamCurse '+self.version+' by RadicalEd'
			self.header.addstr(0, int(int(self.maxX - len(msg))/2), msg)

		if self.mode == 'firstrun':
			msg='https://github.com/RadicalEd360/streamlink-curses'
			self.footer.addstr(0, int(int(self.maxX - len(msg))/2), msg)
			msg='DATABASE: {0}'.format(self.dbname)
			self.title.addstr(0, int(int(self.maxX - len(msg))/2), msg)

		if not self.mode == 'firstrun' and self.mode == 'normal':
			try:
				self.title.addstr('MODE: {0} | FILTER: {1} | DATABASE: {2}'.format(self.mode, 'None' if self.filter == '' else self.filter, self.dbname))
			except:
				pass
		if not self.mode == 'firstrun' and self.mode == 'twitch':
			try:
				self.title.addstr('MODE: {0} | FILTER: {1} | USERNAME: {2}'.format(self.mode, 'None' if self.filter == '' else self.filter, self.twitch_username))
			except:
				pass

	""" theming """
	def setcolors(self):
		colors = curses.has_colors()
		#------------------------------------------------------------------------decide colors
		if colors:
			# converts strings to colors
			def getcolor(colr):
				colorkeys = {
					'BLACK'  : curses.COLOR_BLACK,
					'RED'    : curses.COLOR_RED,
					'GREEN'  : curses.COLOR_GREEN,
					'YELLOW' : curses.COLOR_YELLOW,
					'BLUE'   : curses.COLOR_BLUE,
					'MAGENTA': curses.COLOR_MAGENTA,
					'CYAN'   : curses.COLOR_CYAN,
					'WHITE'  : curses.COLOR_WHITE
                        		}
				try:
					x = int(colr)
					if x > curses.COLORS: # if its a color the terminal doesnt support, use -1 as the color instead
						return(-1)
					else:
						return(x) # make sure its an integer

				except ValueError:
					return(colorkeys.get(colr.upper(), -1)) # check our list of strings for the color else give -1 as color


			curses.use_default_colors()
			t = self.conf['THEME']           # read the config and assign the colors
			curses.init_pair(1, getcolor(t['title'].split()[0]), getcolor(t['title'].split()[1]))
			curses.init_pair(2, getcolor(t['header'].split()[0]), getcolor(t['header'].split()[1]))
			curses.init_pair(3, getcolor(t['select'].split()[0]), getcolor(t['select'].split()[1]))
			curses.init_pair(4, getcolor(t['footer'].split()[0]), getcolor(t['footer'].split()[1]))
			curses.init_pair(5, getcolor(t['status'].split()[0]), getcolor(t['status'].split()[1]))
		else:
			curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
			curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
			curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
			curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_WHITE)
			curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
		self.title_color = curses.color_pair(1)
		self.header_color = curses.color_pair(2)
		self.select_color = curses.color_pair(3)
		self.footer_color = curses.color_pair(4)
		self.status_color = curses.color_pair(5)
		# ----------------------------------------------------------------set the backgrounds
		self.title.bkgd(self.title_color)
		self.header.bkgd(self.header_color)
		self.footer.bkgd(self.footer_color)
		self.status.bkgd(self.status_color)
	""" main event loop """
	def run(self):
		while True:
			self.check_stopped_streams()
			self.body.timeout(5000)
			try:
				c = self.body.getch()
				ret = self.keypress(c)
				if (ret == -1):
					break
			except KeyboardInterrupt:        # handles ctrl + c
				break

	def keypress(self, char):
		""" ----------------------------------------- keybindings """
		#----------------- resize
		if char == ord('#') or char == curses.KEY_RESIZE or char == -1:
			self.refreshall()

		if self.nowindow:
			if char == curses.KEY_EXIT or char == ord('q') or char == ord('Q'):
				return -1
			return

		#---------------------------------------------------------help menu
		if self.currentpad == 'help':
			if char == curses.KEY_EXIT or char == ord('q') or char == ord('Q'):
				self.currentpad = 'main'
				self.refreshall()
			#----------- navigation
			if char == curses.KEY_UP or char == ord('k') or char == ord('K'):
				self.setselect(self.startpos - 1, page=True)
				self.refreshbody()

			if char == curses.KEY_DOWN or char == ord('j') or char == ord('J'):
				self.setselect(self.startpos + 1, page=True)
				self.refreshbody()
			return
		#------------------------------------------------------------------main menu
		if self.currentpad == 'main':
			if char == curses.KEY_EXIT or char == ord('q') or char == ord('Q'):
				return -1
			#--------------- navigation
			if char == curses.KEY_UP or char == ord('k') or char == ord('K'):
				self.setselect(self.selection - 1)
				self.refreshbody()

			if char == curses.KEY_DOWN or char == ord('j') or char == ord('J'):
				self.setselect(self.selection + 1)
				self.refreshbody()

			if char == ord('g'):
				if self.got_g:
					self.setselect(0)
					self.refreshbody()
					self.got_g = False
				else:
					self.got_g = True
			else:
				self.got_g = False

			if char == ord('G'):
				self.setselect(10000)
				self.refreshbody()

			#--------------- menus
			if char == ord('h') or char == ord('?'):
				self.currentpad = 'help'
				self.refreshall()

			#--------------- modes
			# normal only
			if self.mode == 'normal' or self.mode == 'firstrun':
				if char == ord('a') or char == ord('A'):
					self.add_stream()
					if self.database != [] and self.mode == 'firstrun':
						self.mode = 'normal'
						self.nodata = False
					self.refreshall()
				if char == ord('c'):
					if len(self.database_list) <=1:
						return
					self.cycledb()
					if self.database != [] and self.mode == 'firstrun':
						self.mode = 'normal'
					self.refreshall()
					self.msgbox(self.dbfile)
				if char == ord('C'):
					self.createdb()
					self.refreshall()
					self.msgbox('new database created')
				if char == ord('D'):
					self.deletedb()
					if not os.path.exists(self.dbfile):
						return -1
					self.refreshall()

			if self.mode == 'normal':
				if char == ord('d'):
					self.del_stream()
					self.refreshall()
				if char == ord('n') or char == ord('N'):
					self.edit_stream('name')
					self.refreshall()
				if char == ord('u') or char == ord('U'):
					self.edit_stream('url')
					self.refreshall()
			# twitch mode
			if self.mode == 'twitch' or self.mode == 'firstrun':
				if char == ord('w'):
					self.show_offline_streams = 1
					self.clearcache()
					if self.twitch_username == 'None':
						self.get_username()
						if self.twitch_username == 'None':
							self.refreshall()
							return
					self.msgbox('Syncing {0}...'.format(self.twitch_username))
					self.loadcache()
					self.refreshall()

				if char == ord('u'):
					self.get_username()
					self.refreshall()
			# all modes
			if self.mode == 'normal' or self.mode == 'twitch':
				if char == curses.KEY_ENTER or char == 10 or char == 13:
					self.play_stream()
				if char == ord('s'):
					self.stop_stream()
				if char == ord('f'):
					self.set_filter()
					self.refreshall()
				if char == ord('l'):
					self.msgbox(' '.join(str(e) for e in self.cmd))
				if char == ord('L'):
					self.cyclecmds()
					self.msgbox(' '.join(str(e) for e in self.cmd))
				if char == ord('F'):
					self.clear_filter()
					self.refreshall()
				if char == ord('o'):
					self.show_offline_streams ^= 1
					self.filter_streams()
					self.refreshall()
				if char == ord('O'):
					self.show_offline_streams = 0
					self.check_online_streams()
					self.refreshall()

			if char == ord('m') or char == ord('M'):
				self.cyclemode()
				self.refreshall()
			return
		"""-----------------------------------------------------------"""
	""" ----------------------------------------------------------------------- Interface calls """
	# ---------------------------------------------------- refreshing
	def refreshbody(self): # example taken from pyradio
		if self.database == []:
			self.mode = 'firstrun'
			self.settexts()
			self.header.refresh()
			self.title.refresh()

		if self.currentpad is not self.prevpad or self.dbfile != self.prevdb:
			self.startpos = 0
			self.prevdb = self.dbfile
			self.prevpad = self.currentpad
			self.selection = 0

		if self.currentpad == 'main':
			self.data = self.filtered_streams

		if self.mode == 'firstrun':
			self.data = self.firstrun

		if self.currentpad == 'help':
			self.data = self.helpmenu


		self.body.erase()
		self.body.move(0, 0)
		maxDisplay = self.bodyMaxY

		for idx in range(maxDisplay):
			if(idx > maxDisplay):
				break
			try:
				select = self.data[idx + self.startpos]
				col = curses.color_pair(0) # normal transparent
				"""-------------------------------------------- First Run & Help Menu """
				if self.currentpad == 'help' or self.mode == 'firstrun':
					self.body.addstr(idx, 5, select, col)

				elif self.currentpad == 'main':
					#---------------------------current selection
					if idx + self.startpos == self.selection:
						col = self.select_color # selectbar
						self.body.hline(idx + 0, 0, ' ', self.bodyMaxX, self.select_color)

						#----------------------------- set footer
						position = '[{0}/{1}]'.format(self.selection +1, str(len(self.data)))
						self.footer.erase()
						self.footer.addstr(0, 0, position)
						if self.mode == 'twitch':
							try:
								status = select['status']
								if status == None:
									status = ''
								else: # unicode chars is leaving characters behind ??, encoding to ascii fixes the problem
									status = status.encode('ascii', 'ignore')[0:70]
								if len(status) == 70:
									status = str(status, 'UTF_8') + '...'
								self.footer.addstr(0, 10, status, self.footer_color) # set the footer to the users status
							except:
								pass
						if self.mode == 'normal':
							self.footer.addstr(0, 10, select['url'])
						self.footer.refresh()
						#------------------------------------------
					# No. column
					numb = str(idx + self.startpos + 1) + '.'
					nombre = numb.rjust(4)
					self.body.addstr(idx, 0, nombre, col)
					# Streamer column
					self.body.addstr(idx, 5, select['name'][0:19], col)
					# Twitch Game column
					if self.mode == 'twitch' and select['game']:
						try:
							self.body.addstr(idx, 25, select['game'], col)
						except:
							pass
					# Online column
					if not self.mode == 'firstrun':
						if select['online'] is 0:
							ind = self.conf['INDICATORS']['offline']
						if select['online'] is 1:
							ind = self.conf['INDICATORS']['online']
						if select['online'] is 2:
							ind = self.conf['INDICATORS']['playing']
						self.body.addstr(idx, self.bodyMaxX - 10, str(ind), col)
			except:
				break

		self.body.refresh(0,0, 2,0, self.bodyMaxY+1,self.bodyMaxX)

	def refreshall(self):
		try:
			self.init()
			self.setcolors()
			self.settexts()

			self.footer.noutrefresh()
			self.header.noutrefresh()
			self.title.noutrefresh()
			self.status.noutrefresh()
			curses.doupdate()
			self.refreshbody()
			self.nowindow = False
		except Exception as e:
			#raise(e)
			self.s.erase()
			self.s.addstr('terminal too small')
			self.s.refresh()
			self.nowindow = True
	#-----------------------------------------------------------------------------------------------

	def setselect(self, number, page=False): # adapted from pyradio
		""" sets all the numbers for our page to move, movements happen when numbers are changed and then refreshed
			self.startpos defines the upper left of whats to be displayed, when this is not 0 it displays an upper left portion starting
			from that row in the data, so page appears to move when refreshed

			self.selection defines the position of the selectbar, when this is changed it highlights the row of data it defines
		"""
		# make sure our number passed doesnt go out of bounds
		number = max(0, number)
		number = min(number, len(self.data) - 1)

		maxDisplayedItems = self.bodyMaxY

		# move page
		if page:
			# move the page down
			if self.startpos + maxDisplayedItems >= len(self.data) + 1:
				self.startpos = number
			# allow the page to move back up
			elif number + maxDisplayedItems < len(self.data) + 1 :
				self.startpos = number
		# move line, page if necessary
		else:
			# move the select bar
			self.selection = number

			# if selection is at bottom moving down
			if self.selection - self.startpos >= maxDisplayedItems:
				self.startpos = self.selection - maxDisplayedItems + 1
			# if selection is at top moving upward
			elif self.selection < self.startpos:
				self.startpos = self.selection
	def createdb(self):
		newdb = self.prompt_input('New database name: ')
		if not newdb:
			return
		newdb = os.path.join(self.dbpath, newdb)
		if os.path.exists(newdb):
			return
		db.create(newdb)
		self.database_list = [f for f in os.listdir(self.dbpath) if os.path.isfile(os.path.join(self.dbpath, f))]
		self.dbfile = newdb
		self.loaddata()
	def deletedb(self):
		if self.prompt_confirm('Are you sure you want to delete the current database?'):
			if self.prompt_confirm('Confirm Deletion of '+ self.dbname):
				db.rmdb(self.dbfile)
				self.database_list = [f for f in os.listdir(self.dbpath) if os.path.isfile(os.path.join(self.dbpath, f))]
				self.cycledb()

	def cyclemode(self):
		self.mode = 'twitch' if (self.mode == 'normal') else 'normal'
		self.nodata = True
		self.show_offline_streams = 1

	def cycledb(self):
		self.dbnumber += 1
		if self.dbnumber >= len(self.database_list):
			self.dbnumber = 0
		self.dbfile = os.path.join(self.dbpath, self.database_list[self.dbnumber])
		self.loaddata()

	def cyclecmds(self):
		if len(self.cmd_list) == 1:
			return
		self.cmd_index += 1
		if self.cmd_index >= len(self.cmd_list):
			self.cmd_index = 0
		self.cmd = self.cmd_list[self.cmd_index]

	def edit_stream(self, option):
		stream = self.database[self.selection]
		usrinput = self.prompt_input('{0}: '.format(option))
		if not usrinput:
			return
		stream[option] = usrinput
		db.save(self.database, self.dbfile)

	def add_stream(self):
		url = self.prompt_input('New stream URL: ')
		if not url:
			return

		name = url.split('/')[-1]
		if not name:
			name = 'unnamed'
		stream = {
				'url': url,
				'name': name
			}
		self.database.append(stream)
		db.save(self.database, self.dbfile)

	def del_stream(self):
		stream = self.filtered_streams[self.selection]
		if self.prompt_confirm('Delete stream {0}'.format(stream['name'])):
			self.database.remove(stream)
			db.save(self.database, self.dbfile)
		else:
			return

	def prompt_confirm(self, prompt=''):
		hint = 'y/n'
		self.status.erase()
		self.status.addstr('{0} {1}'.format(prompt, hint))
		curses.curs_set(1)
		curses.echo()
		i = self.status.getch()
		curses.noecho()
		curses.curs_set(0)
		self.status.erase()
		if i == ord('y') or i == ord('Y'):
			return True
		elif i == ord('n') or i == ord('N'):
			return False
		else:
			return False

	def prompt_input(self, prompt=''):
		self.status.erase()
		self.status.addstr(prompt)
		curses.curs_set(1)
		curses.echo()
		usrinput = self.status.getstr().decode()
		curses.noecho()
		curses.curs_set(0)
		self.status.erase()
		return usrinput

	def msgbox(self, msg):
		boxh = 3
		boxw = len(msg) +2
		boxx = int(int(self.bodyMaxX - boxw)/2)
		boxy = int(int(self.bodyMaxY - boxh)/2)

		box = curses.newwin(boxh, boxw, boxy, boxx)
		box.immedok(True)
		box.box()
		box.addstr(1,1,msg)

	def clear_filter(self):
		self.filter = ''
		self.filter_streams()

	def set_filter(self):
		self.filter = self.prompt_input('Filter: ').lower()
		self.filter_streams()


	def filter_streams(self):
		self.filtered_streams = []
		for stream in self.database:
			if not 'online' in stream:
				stream['online'] = 0

                      # Filtering Process starts here, one big if statement
                      #    0 1------------------------------------------------------1
			if ( (self.show_offline_streams or stream['online'] in [1,2])                         # decide whether or not to show offline streams
                      #     1 2-----------------------------------------------------------------------------2
			and ( (self.filter in stream['name'].lower() or self.filter in stream['url'].lower()) # check name and url for filter
                      #    2--------------------------------------------------------2
			or (stream['game'] and self.filter in stream['game'].lower())                         # if game value exists check it for filter
                      # 1
			)
                      # 0                 # closing tags for if statement
			):
				self.filtered_streams.append(stream)
                      # End of Filtering

	def get_username(self):
		self.twitch_username = self.prompt_input('Twitch Username: ')
		if self.twitch_username == '':
			self.twitch_username = 'None'

	def _check_stream(self, url): # from the original streamlink-curses
		try:
			plugin = self.streamlink.resolve_url(url)
			avail_streams = plugin.get_streams()
			if avail_streams:
				return 1
			return 0
		except:
			return 3
	def check_online_streams(self): # from the original streamlink-curses
		self.status.addstr('Checking online streams...')
		self.status.refresh()
		self.checked_online.append(self.dbfile)

		done_queue = queue.Queue()
							# disables showing hosting streams as online
		self.streamlink.set_plugin_option('twitch', 'disable_hosting', True)

		def check_stream_managed(args):
			url, queue = args
			status = self._check_stream(url)
			done_queue.put(url)
			return status

		self.CHECK_ONLINE_THREADS = 10
		pool = Pool(self.CHECK_ONLINE_THREADS)
		args = [(s['url'], done_queue) for s in self.database]
		statuses = pool.map_async(check_stream_managed, args)
		n_streams = len(self.database)

		while not statuses.ready():
			sleep(0.1)
			self.status.erase()
			self.status.addstr('Checked {0}/{1} streams...'.format(done_queue.qsize(), n_streams))
			self.status.refresh()

		self.status.erase()
		statuses = statuses.get()

		for i, s in enumerate(self.database):
			if s['online'] != 2 :
				s['online'] = statuses[i]

		self.savedb()
		self.filter_streams()
		pool.close()

	def check_stopped_streams(self):
		finished = self.q.get_finished()
		for f in finished:
			for s in self.database:
				try:
					i = self.filtered_streams.index(s)
				except ValueError:
					continue
				if f == s['url']:
					s['online'] = 1
					self.status.addstr('Stream {0} has stopped'.format(s['name']))
					self.status.refresh()
					self.refreshbody()

	def stop_stream(self):
		stream = self.filtered_streams[self.selection]
		if stream['online'] is 2:
			self.status.erase()
			self.status.addstr('stopping ' + stream['name'])
			self.status.refresh()
			self.status.erase()

			p = self.q.terminate_process(stream['url'])
			if p:
				stream['online'] = 1
				self.refreshall()

	def play_stream(self):
		stream = self.filtered_streams[self.selection]
		self.status.erase()
		self.status.addstr('playing ' + stream['name'])
		self.status.refresh()
		self.status.erase()

		oldonline = stream['online']

		try:
			stream['online'] = 2
			self.refreshbody()
			self.q.put(stream, self.cmd)
		except Exception as e:
			if type(e) == player.QueueDuplicate:
				self.status.erase()
				self.status.addstr('already playing')
				self.status.refresh()
			elif type(e) == player.OSError:
				self.status.erase()
				self.status.addstr('os error')
				self.status.refresh()
			elif type(e) == player.QueueFull:
				self.status.erase()
				self.status.addstr('queue full')
				self.status.refresh()
			else:
				raise(e)
			stream['online'] = oldonline
			self.status.erase()

	def __del__(self):
		self.clearcache()

if __name__ == '__main__':
	#conf = config.load()
	#data = db.load('asdf')
	#l = InterFace(conf, data)
	#curses.wrapper(l)
	pass
