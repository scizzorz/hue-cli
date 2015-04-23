#!/usr/bin/env python

import argparse
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


parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument("-c", "--color", choices=list(HUES))
group.add_argument("-u", "--hue", help="0 - 360", type=int)
parser.add_argument("-s", "--saturation", help="0 - 100", type=int)
parser.add_argument("-b", "--brightness", help="0 - 100", type=int)
parser.add_argument("-l", "--lights", help="comma-separated light indices", default="1,2")
parser.add_argument("-t", "--time", help="transition time in seconds", default=0.4, type=float)
parser.add_argument("-o", "--off", help="turn off lights", action="store_true")
args = parser.parse_args()

bridge = phue.Bridge('192.168.1.113')
bridge.connect()

package = {}

if args.color is not None and args.color in HUES:
	args.hue = HUES[args.color]

if args.hue is not None:
	package['hue'] = int(args.hue * 65535 / 360)

if args.saturation is not None:
	package['sat'] = int(args.saturation * 254 / 100)

if args.brightness is not None:
	package['bri'] = int(args.brightness * 254 / 100)

package['on'] = not args.off

bridge.set_light([int(x) for x in args.lights.split(',')], package, transitiontime=args.time*10)
