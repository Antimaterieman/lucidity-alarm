(not working yet, not playing any sound)

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

## How to Controbute

**Those super akward audio recordings in the audio dir**

Well, I think my voice sounds horrible in those files but afaik it's normal to find your
own recorded voice strange because you hear it differently the majority of your time,
through vibrations in your skull. It would be nice if people could contribute voices like that and be brave
enough to share it in the internet. Each subdirectory should be one set of audio
files that can be played in one night. Next night it's a different voice/subdirectory.
Be creative in what to say. Please compress them to e.g. mp3.

## Dependencies

```
apt install sox
pip3 install pysndfx
```

## Roadmap

- make the command line work, playing sounds as described above
- make GUI and add button to add it to autostart and make it minimizable to the system tray
- collect audiorecordings for lucid dream induction from members of lucid dreaming forums
- pie in the sky 1: if it works, make android app that does the same thing
- pie in the sky 2: make android app that detects movements and sounds in bed, sends message to the computer that
an REM phase might be happening right now and increase the chance of being triggered at that time
