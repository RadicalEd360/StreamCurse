import os

VERSION="1.5.2_Ed"

DEFAULT_RESOLUTION = 'Best'

CHECK_ONLINE_ON_START = False
CHECK_ONLINE_THREADS = 15
CHECK_ONLINE_INTERVAL = 0

STREAMLINK_COMMANDS = ["streamlink"]

RC_DEFAULT_DIR  = (os.environ.get('XDG_CONFIG_HOME') or
                  os.path.expanduser(u'~/.config/livestreamer-curses'))
RC_DEFAULT_PATH = os.path.join(RC_DEFAULT_DIR, u'livestreamer-cursesrc')
DB_DEFAULT_DIR  = (os.environ.get('XDG_DATA_HOME') or
                  os.path.expanduser(u'~/.local/share/livestreamer-curses'))
DB_DEFAULT_PATH = os.path.join(DB_DEFAULT_DIR, u'livestreamer-curses.db')

INDICATORS = [
        '  x  ', # offline
        ' >>> ', # streaming
        '  ?  ', # unknown
        '  !  ', # error
        '[>>>]'  # playing
]
