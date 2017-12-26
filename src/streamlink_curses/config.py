import os

VERSION="0.1"

DEFAULT_RESOLUTION = 'Best'

CHECK_ONLINE_ON_START = False
CHECK_ONLINE_THREADS = 15
CHECK_ONLINE_INTERVAL = 0

STREAMLINK_COMMANDS = ["streamlink"]

RC_DEFAULT_DIR  = (os.environ.get('XDG_CONFIG_HOME') or
                  os.path.expanduser(u'~/.config/streamlink-curses'))
RC_DEFAULT_PATH = os.path.join(RC_DEFAULT_DIR, u'streamlink-cursesrc')
DB_DEFAULT_DIR  = (os.environ.get('XDG_DATA_HOME') or
                  os.path.expanduser(u'~/.local/share/streamlink-curses'))
DB_DEFAULT_PATH = os.path.join(DB_DEFAULT_DIR, u'streamlink-curses.db')

# colors - foreground, background
HEADER_COLOR = ['white', 'red']
SELECT_COLOR = ['red', 'white']
TITLE_COLOR  = ['white', 'red']
FOOTER_COLOR = ['white', 'red']
STATUS_COLOR = ['white', 'red']


INDICATORS = [
        '  x  ', # offline
        ' >>> ', # streaming
        '  ?  ', # unknown
        '  !  ', # error
        '[>>>]'  # playing
]
