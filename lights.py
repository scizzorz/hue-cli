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

def add_room(args):
	config['rooms'][args.name] = [int(x) for x in args.lights.split(',')]

def rm_room(args):
	del config['rooms'][args.name]

def list_rooms(args):
	print(config['rooms'])

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

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

parser.set_defaults(func=main)

add_room_parser = subparsers.add_parser('add-room', help='make a new room')
add_room_parser.add_argument('name', type=str)
add_room_parser.add_argument('lights')
add_room_parser.set_defaults(func=add_room)

rm_room_parser = subparsers.add_parser('rm-room', help='remove a room')
rm_room_parser.add_argument('name', type=str)
rm_room_parser.set_defaults(func=rm_room)

list_room_parser = subparsers.add_parser('list-rooms', help='list all rooms')
list_room_parser.set_defaults(func=list_rooms)

args = parser.parse_args()

args.func(args)

json.dump(config, open(RCFILE, 'w'))
