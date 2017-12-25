from streamlink import Streamlink as Livestreamer

class Poller(object):

    def __init__(self):
        self.livestreamer = Livestreamer()

    def _check_stream(self, url):
        try:
            plugin = self.livestreamer.resolve_url(url)
            avail_streams = plugin.get_streams()
            if avail_streams:
                return 1
            return 0
        except:
            return 3

    def prepare_check(self, streams):
        done_queue   = queue.Queue()

    def check_online_streams(self):
        self.all_streams_offline = True
        self.set_status(' Checking online streams...')

        def check_stream_managed(args):
            url, queue = args
            status = self._check_stream(url)
            done_queue.put(url)
            return status

        pool = Pool(CHECK_ONLINE_THREADS)
        args = [(s['url'], done_queue) for s in self.streams]
        statuses = pool.map_async(check_stream_managed, args)
        n_streams = len(self.streams)

        while not statuses.ready():
            sleep(0.1)
            self.set_status(' Checked {0}/{1} streams...'.format(done_queue.qsize(), n_streams))
            self.s.refresh()

        statuses = statuses.get()
        for i, s in enumerate(self.streams):
            s['online'] = statuses[i]
            if s['online']:
                self.all_streams_offline = False

        self.refilter_streams()

