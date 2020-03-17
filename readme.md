(only a command line utility at the moment, but basically running)

# Lucidity Alarm
**Super Random Fun Time Alarm Clock**

For Linux, but who knows maybe also for Mac and Windows since it's python and stuff.

Will play random audio files, in a random pitch, with random reverb effects,
within a random time frame and sometimes doesn't trigger at all.

By default it actually starts the alarm precisely, so it can also be
used as a normal alarm clock on your HTPC as well.

The plan is to provide recordings of your voice, suggesting random things to you
during your dreams. It's very random so that you are not able to get used to it,
so it doesn't lose its effect (hopefully). So keep it as random as possible, and try to set
the start time about 4h into your normal sleep time and end time to 4h after the
start time. So there is a higher chance to play the audio files during your REM sleep.

Now if you record audio files suggesting to realize that you are dreaming, you might
potentially get some lucid dreams out of it. But I haven't tried if that works. It's
very experimental. It would also be good if there are multiple voices available and
the alarm clock will decide for one of the voices from a random subdirectory each day
(and randomly pitch and possibly randomly apply reverb effects to it).

This is based on an observation: If the TV is running in the morning
dreams are affected by its sound.

## Usage

**GUI**

start a gtk interface with

```bash
python interface.py
```

**CLI**

help:

```bash
python main.py --help
```

you can find an example in `test.sh`

## How to Contribute

**Those super akward audio recordings in the audio dir**

Well, I think my voice sounds horrible in those files but afaik it's normal to find your
own recorded voice strange. It would be nice if people could contribute voices like that and be brave
enough to share it in the internet. Each subdirectory should be one set of audio
files that can be played in one night. Next night it's a different voice/subdirectory.
Be creative in what to say.

You can post a link to your single high quality audio recording and I can
cut and compress it here: https://github.com/antimaterieman/lucidity-alarm/issues,
or you can cut and compress it yourself directly make a pull request on github. Since lucidity-alarm uses
pydub which uses ffmpeg, many formats should be compatible.

## Dependencies

use those commands in manjaro/arch to get the needed dependencies. package names may be similar in ubuntu using apt

```
sudo pip3 install pysndfx pydub sounddevice
```

## TODO

- make GUI and add button to add it to autostart and make it minimizable to the system tray
- add config that loads when the GUI starts
- collect audiorecordings for lucid dream induction from members of lucid dreaming forums
- make sure it works on windows
- PEP 257 docstrings
- add the option to specify a folder for music files, e.g. to get some ambient texture play in the background.

**pies in the sky**
- if it works, make android app that does the same thing
- make android app that detects movements and sounds in bed, sends message to the computer that
an REM phase might be happening right now and increase the chance of being triggered at that time

