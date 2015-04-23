#!/usr/bin/env python

import argparse
import json
import os
import phue

HUES = {
	'red': 0,
	'orange': 30,
	'yellow': 60,
	'lime': 90,
	'green': 120,
	'seafoam': 150,
	'foam': 150,
	'cyan': 180,
	'sky': 210,
	'blue': 240,
	'purple': 270,
	'magenta': 300,
	'pink': 330,
}

RCFILE = os.path.expanduser('~/.huerc')

if os.path.isfile(RCFILE):
	config = json.load(open(RCFILE))
else:
	config = {
		'rooms': {'default': [1]},
	}

# default command

def main(args):
	bridge = phue.Bridge('192.168.1.113')
	bridge.connect()

	package = {}

	if args.color is not None:
		args.hue = HUES[args.color]

	if args.hue is not None:
		package['hue'] = int(args.hue * 65535 / 360)

	if args.saturation is not None:
		package['sat'] = int(args.saturation * 254 / 100)

	if args.brightness is not None:
		package['bri'] = int(args.brightness * 254 / 100)

	lights = config['rooms'][args.room]
	if args.lights is not None:
		lights = [int(x) for x in args.lights.split(',')]

	package['on'] = not args.off

	bridge.set_light(lights, package, transitiontime=args.time*10)

# rooms subcommand

def room(args):
	print(config['rooms'])

def room_set(args):
	config['rooms'][args.name] = [int(x) for x in args.lights.split(',')]

def room_rm(args):
	del config['rooms'][args.name]

# main parser

parser = argparse.ArgumentParser()
parser.set_defaults(func=main)
subs = parser.add_subparsers()

color_group = parser.add_mutually_exclusive_group()
color_group.add_argument('-c', '--color', choices=list(HUES))
color_group.add_argument('-u', '--hue', help='0 - 360', type=int)

parser.add_argument('-s', '--saturation', help='0 - 100', type=int)
parser.add_argument('-b', '--brightness', help='0 - 100', type=int)

lights_group = parser.add_mutually_exclusive_group()
lights_group.add_argument('-l', '--lights', help='comma-separated light indices')
lights_group.add_argument('-r', '--room', choices=list(config['rooms']), default='default')

parser.add_argument('-t', '--time', help='transition time in seconds', default=0.4, type=float)
parser.add_argument('-o', '--off', help='turn off lights', action='store_true')

room_parser = subs.add_parser('room', help='manage rooms')
room_parser.set_defaults(func=room)
room_subs = room_parser.add_subparsers()

room_set_parser = room_subs.add_parser('set', help='add or update a room')
room_set_parser.add_argument('name', type=str)
room_set_parser.add_argument('lights')
room_set_parser.set_defaults(func=room_set)

room_rm_parser = room_subs.add_parser('rm', help='remove a room')
room_rm_parser.add_argument('name', choices=list(config['rooms']))
room_rm_parser.set_defaults(func=room_rm)

args = parser.parse_args()

args.func(args)

json.dump(config, open(RCFILE, 'w'))
