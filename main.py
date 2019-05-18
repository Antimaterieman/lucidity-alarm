#!/usr/bin/env python3

import argparse
import datetime
import time
import random
import os
import threading
import multiprocessing
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
pygame.init()
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
from pysndfx import AudioEffectsChain
import numpy as np


# controls are in minutes because that's easier and convenient I guess
parser = argparse.ArgumentParser(description='Randomized alarm clock')
parser.add_argument('--start', metavar='TIME', dest='start', help='earliest time the alarm clock will alert. ' +
    'If --end is not provided, will alarm exactly at this time. Example: 23:50', required=True, type=str)
parser.add_argument('--end', metavar='TIME', dest='end', help='latest time the alarm clock will alert. ' +
    'Example: 06:20', type=str, default=None)
parser.add_argument('--script', metavar='PATH', dest='script', help='optional command/script to run when ' +
    'the alarm is triggered. Examples: "beep", "./some/funky/script.sh", which will be executed in a new Thread ' +
    'while the alarm clock is running. The alarm will not turn off until the script is terminated', type=str)
parser.add_argument('--audio', metavar='PATH', dest='audio_path', help='path to a folder that contains audiofiles ' +
    'for the alarm. If that folder contains subdirectories, will decide for a single one of those subdirectories ' +
    'each day and only play files out of that one. They will be played until this script is stopped or --max-duration ' +
    'is reached', type=str)
parser.add_argument('--max-duration', metavar='INT', dest='max_duration', help='after how many minutes to stop' +
    ' the alarm. Default: 30. If 0, will go on forever', type=float, default=30)
parser.add_argument('--fade-duration', metavar='INT', dest='fade_duration', help='if provided and greater than ' +
    '0, will start quiet and increase to --max-volume within the specified time in minutes. After --max-duration time ' +
    'has passed, decreases the volume in the same way. Default 0', default=0, type=float)
parser.add_argument('--max-volume', metavar='INT', dest='max_volume', help='how many percent volume are the ' +
    'limit. Default 100', default=100, type=int)
parser.add_argument('--effect', metavar='FLOAT', dest='effect', help='Between 0 and 100, how crazy ' +
    'the effects added to the voices should be. Will be change each night, so sometimes it sounds normal,' +
    'sometimes it\'s ghost like. Defaults to 100', default=100, type=int)
parser.add_argument('--probability', metavar='FLOAT', dest='probability', help='How likely it is that the alarm ' +
    'starts at all on a given day. Between 0 and 100. Default 100', default=100, type=int)
parser.add_argument('--unlock', dest='unlock', help='Will try to unlock the screen.', default=False, type=bool)
parser.add_argument('--cec-on', dest='cec', help='Will try to turn on the monitor/TV using ' +
    'CEC over hdmi. There aren\'t many computer devices that support this. The raspberry does. Default False',
    default=False, action='store_true')
parser.add_argument('--relax', dest='relax', help='The maximum multiple of the audio file duration to wait until the ' +
    'next audio file playback. Default 10', default=10, type=int)
parser.add_argument('--debug', dest='debug', help=argparse.SUPPRESS, default=False, action='store_true')

args = parser.parse_args()


def parse_time(time):
    """returns the number of seconds since midnight
    
    Examples:
        parse_time("01:00") = 3600
        parse_time("13:30") = 48600
        parse_time("13:30:10") = 48610"""

    a = time.split(':')
    if len(a) == 2:
        return (int(a[0]) * 60 + int(a[1])) * 60
    elif len(a) == 3:
        return (int(a[0]) * 60 + int(a[1])) * 60 + int(a[2])
    else:
        raise ValueError("unknown format", time, "expected something like 13:30 or 13:30:10")


# transform values to seconds now
if args.max_duration:
    args.max_duration *= 60
if args.fade_duration:
    args.fade_duration *= 60
if args.start:
    args.start = parse_time(args.start)
if args.end:
    args.end = parse_time(args.end)
# from here on every timestamp and duration is in seconds

if args.debug:
    # sets the earliest alarm time to 1 second in the future
    # has 10 seconds until latest alarm time to observe
    # if the random stuff works
    now = datetime.datetime.now()
    current_t = now.hour * 3600 + now.minute * 60 + now.second
    args.start = current_t + 1
    args.end = args.start + 1
    args.morph = 2

volume = 100
playing = False


def time_to_string(seconds):
    """transforms 3600 to 01:00:00 and 48610 to 13:30:10,
    reversing the parse_time function.

    Examples:
        time_to_string(48600) = 13:30:00
        time_to_string(3600) = 01:00:00"""

    hours = seconds / 3600
    minutes = (hours - int(hours)) * 60
    seconds = seconds % 60
    # now to strings
    hours = str(int(hours)).zfill(2)
    minutes = str(int(minutes)).zfill(2)
    seconds = str(int(seconds)).zfill(2)
    return "{}:{}:{}".format(hours, minutes, seconds)


def set_volume(percent, system=False):
    """sets the volume of the playback.
    
    Percent is between 0 and 100.

    If system is True, will control the system volume using
    amixer instead. system can also be a string like "Master"
    or "PCM", which is the amixer control. The amixer command
    can help you find out what you want to control. Default is
    False."""

    percent = int(percent)
    if system != False:
        # leave the volume variable at 100 or whatever it is at
        # the moment and only control the system
        control = 'Master'
        if isinstance(system, str):
            control = system
        os.system('amixer -M set {} {}% > /dev/null'.format(control, percent))
    else:
        global volume
        volume = percent


def fade_volume(fading_time, start_v=0, end_v=100):
    """fading_time in seconds, start_v and end_v in percent between
    0 and 100. Will block during that time so it should be
    started as a thread. Rises the volume in timesteps of 1
    second."""

    end_t = time.time() + fading_time
    volume_step = (end_v - start_v) / fading_time
    new_volume = start_v
    while time.time() < end_t:
        logger.debug('new volume: {}'.format(int(new_volume)))
        set_volume(new_volume)
        time.sleep(1)
        new_volume += volume_step
    set_volume(end_v)
    logger.info('new volume: {}'.format(int(new_volume)))


def apply_fx(fx, a):
    # fx seems to chain the channels behind each other so the sound gets
    # played twice if stereo, and also it transposes the output.
    a = np.array([fx(a[:,0]), fx(a[:,1])]).T
    a = np.ascontiguousarray(a, np.int16)
    return a.astype(np.int16)


def play_music(dir, effect, relax):
    """dir is the path to where all the sound files are stored,
    will select it or one of it's subdirectories randomly to
    decide about which sound files to use. Will not recurse
    into subdirectories of the selected subdirectory.
    effect is an int between 0 (none) and 100 (full)"""

    global playing
    playing = True

    # select random effect parameters
    pitch = 1
    reverb = 0
    reverse = False
    if effect > 0:
        highest_pitch = 1.3
        lowest_pitch = 0.7
        pitch = (((random.random() * (highest_pitch - lowest_pitch)) + lowest_pitch) * effect + 1 * (100 - effect)) / 100
        reverb = random.randint(0, effect)
        reverse = random.randint(0, 1) == True

    # start playing random files from the provided path and its subdirs
    # apply pitch to all files
    all_sound_files = [(dirpath, list(map(lambda x: dirpath + os.sep + x, filenames))) for dirpath, _, filenames in os.walk(dir)]

    # select a subdir randomly (including the root dir and it's direct audio childs,
    # which coveres for there not being subdirs)
    sound_files = []
    selected_path = ''
    while len(sound_files) == 0:
        selection = all_sound_files[random.randint(0, len(all_sound_files) - 1)]
        sound_files = selection[1]
        selected_path = selection[0]

    logger.info('todays pitch: {}'.format(pitch))
    logger.info('todays reverb: {}, reverse: {}'.format(reverb, reverse))
    logger.info('todays folder: "{}"'.format(selected_path))

    # https://github.com/carlthome/python-audio-effects
    fx = (
        AudioEffectsChain()
        .speed(pitch)
    )

    # reverb
    if reverse:
        fx.reverse()
    fx.reverb(reverberance=reverb)
    if reverse:
        fx.reverse()

    while playing:
        original = pygame.mixer.Sound(sound_files[random.randint(0, len(sound_files) - 1)])
        a = pygame.sndarray.array(original)
        duration = len(a) / 44100 * (1 / pitch)
        zeros = np.zeros(a.shape, a.dtype)

        # add plenty of room for reverb in the array
        if reverse:
            a = np.concatenate([zeros] * 2 + [a])
        else:
            a = np.concatenate([a] + [zeros] * 2)

	# between 33% and 100% of the current volume
        a = (a * (1/3 + random.random() * 2/3) * volume / 100).astype(np.int16)
        a = apply_fx(fx, a)

        wet = pygame.sndarray.make_sound(a)
        pygame.mixer.Sound.play(wet)
        
	# at least a third of the duration, at most duration * relax
        time.sleep(duration * (1/3 + random.random() * 2/3) * relax)


while True:
    now = datetime.datetime.now()
    current_t = now.hour * 3600 + now.minute * 60 + now.second

    will_alarm = random.randint(0, 100) <= args.probability
    # make double secure, because an alarm can be quite important,
    # so also check if probability is below 100 to cover for bugs
    if not will_alarm and args.probability < 100:
        logger.info('skipping the next alarm, sleeping for a day now')
        time.sleep(25 * 60 * 60)
    else:
        sleep_duration = (args.start - current_t) % (24 * 3600)
        if not args.end is None:
            sleep_duration += random.randint(0, (args.end - args.start) % (24 * 3600))

        logger.info('sleeping until next alarm will be triggered for {}'.format(time_to_string(sleep_duration)))

        # now wait. Hide that debug message later because it should not be predictable for the user
        time.sleep(sleep_duration)

        # start provided script using os.system or something and the path from command line args
        script_thread = None
        if args.script:
            script_thread = threading.Thread(target=os.system, args=args.script)
            script_thread.start()

        # set volume to 0 (if fading-in is active)
        fading_thread = None
        if args.fade_duration:
            logger.info('fading in...')
            fading_thread = threading.Thread(target=fade_volume, args=[args.fade_duration, 0, args.max_volume])
            fading_thread.start()

        # try to unlock linux screensaver with dbus
        if args.unlock:
            logger.info('not yet implemented')
        # turn tv on with lib-cec
        if args.cec:
            logger.info('not yet implemented')
        
        # play music in extra process and provide the path and max random effect level as params.
        # in main thread check if end time is reached and then stop
        music_thread = threading.Thread(target=play_music, args=[args.audio_path, args.effect, args.relax])
        music_thread.start()

        # wait for the max duration to be reached
        if args.max_duration > 0:
            end_t = time.time() + args.max_duration
            alarm_duration = end_t - time.time()
            logger.info('stopping or fading out the alarm in {}'.format(time_to_string(round(alarm_duration, 3))))
            time.sleep(alarm_duration)
        else:
            logger.info('alarm will go on forever, because --max-duration is set to 0')
            # wait for the music_thread to join which will ofc never happen
            # because the main process stops it normally by setting playing to False
            music_thread.join()

        
        if script_thread and script_thread.is_alive():
            logger.info('waiting for script to finish')
            script_thread.join()
            
        # fade out the volume
        if fading_thread and fading_thread.is_alive():
            # first make sure the previous job for fading in is done
            fading_thread.join()
        logger.info('fading out...')
        fading_thread = threading.Thread(target=lambda: fade_volume(args.fade_duration, volume, 0))
        fading_thread.start()
        fading_thread.join()

        # end music thread and then start over
        playing = False
        