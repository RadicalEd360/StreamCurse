import shlex
import queue

import time

from subprocess import Popen, DEVNULL
from multiprocessing.pool import ThreadPool as Pool



class QueueFull(Exception): pass
class QueueDuplicate(Exception): pass

class ProcessList(object):
    """ Small class to store and handle calls to a given callable """

    def __init__(self, f, max_size=10):
        """ Create a ProcessList

        f        : callable for which a process will be spawned for each call to put
        max_size : the maximum size of the ProcessList

        """
        self.q        = {}
        self.max_size = max_size
        self.call     = f

    def __del__(self):
        self.terminate()

    def full(self):
        """ Check is the List is full, returns a bool """
        return len(self.q) == self.max_size

    def empty(self):
        """ Check is the List is full, returns a bool """
        return len(self.q) == 0
####################################################################################
    def put(self, stream, cmd):
        """ Spawn a new background process """
        if len(self.q) < self.max_size: # check if queuefull
            if stream['url'] in self.q: # check if already in queue
                raise QueueDuplicate
            p = self.call(stream, cmd)  # play it
            self.q[stream['url']] = p   # add stream to now playing queue with its popen status
        else:
            raise QueueFull
####################################################################################
    def get_finished(self):
        """ Clean up terminated processes and returns the list of their ids """
        indices  = []
        for idf, v in self.q.items():
            if v.poll() != None:
                indices.append(idf)

        for i in indices:
            self.q.pop(i)
        return indices

    def get_process(self, idf):
        """ Get a process by id, returns None if there is no match """
        return self.q.get(idf)

    def get_stdouts(self):
        """ Get the list of stdout of each process """
        souts = []
        for v in self.q.values():
            souts.append(v.stdout)
        return souts

    def terminate_process(self, idf):
        """ Terminate a process by id """
        try:
            p = self.q.pop(idf)
            p.terminate()
            return p
        except:
            return None

    def terminate(self):
        """ Terminate all processes """
        for w in self.q.values():
            try:
                w.terminate()
            except:
                pass

        self.q = {}
###################################################################
class StreamPlayer(object):
    """ Provides a callable to play a given url """

    def play(self, stream, cmd):
        full_cmd = list(cmd)
        if '__urlhere__' in full_cmd:
            for idx, item in enumerate(full_cmd):
                if item == '__urlhere__':
                    full_cmd[idx] = stream['url']
        else:
            full_cmd.extend([stream['url']])

        return Popen(full_cmd, stdout=DEVNULL, stderr=DEVNULL)
###################################################################

if __name__ == '__main__':
	pass
	"""
	q = ProcessList(StreamPlayer().play) # init the caller wrapper object
	cmds = ['echo','echo','mpv']            # emulate cmds like in the config
	cmd_list = list(map(shlex.split, cmds)) #
	cmd = cmd_list[2]			#
	s = {'id':'30', 'name': 'asdfstream',            # dummy stream
		'url': 'https://www.twitch.tv/theonly0'} #

	# do the thing
	try:
		q.put(s, cmd) #play it
	except Exception as e: #see what the error is if error in playing
		if type(e) == QueueDuplicate:
			print('already playing')
		elif type(e) == OSError:
			print('bad command')
		else:
			raise e

	# testing other functions
	#p = q.get_process(s['url']) != None
	#if p:
	#	print('playing')
	#else:
	#	print('not playing')


	# timer till everything stops
	for i in range(1,300):
		print(i)
		time.sleep(1)
	"""
