## Changelog
### 25-Dec-17
- this project was born from https://github.com/gapato/livestreamer-curses
- moved everything over to streamlink
- added additional curses color support, black background is now transparrent and interface has a blue bar
- hosted twitch streams now show up as offline
- added theming support, you can now set your own colors for the interface within streamlink-cursesrc file

### 26-Dec-17
- themes now support 255 colors

### 20-Jan-18
- completely rewrote entire project from scratch
- project now only requires streamlink just to check if streams are online, this may change in the future
- config file now makes alot more sense and is straightforward, however every option is required for project to run, you can generate a fresh config easily just in case
- switch modes between normal and twitch
- twitch mode uses api calls to get info about the streamers username follows up to 100 streams
- normal mode can create, edit, delete, and switch databases on the fly
- twitch mode only requires a username to lookup their follows
- commands can be anything written in the config file, with __urlhere__ as an optional placement for url, otherwise url is appended to end of command
- removed support for switching resolutions, you can set a resolution within your cmd e.g. streamlink __urlhere__ 720p
