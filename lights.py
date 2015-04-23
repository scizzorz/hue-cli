#!/usr/bin/env python

import argparse
import phue

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--hue", help="the hue", type=int)
parser.add_argument("-s", "--saturation", help="the saturation", type=int)
parser.add_argument("-b", "--brightness", help="the brightness", type=int)
parser.add_argument("-l", "--lights", help="the lights", default="1,2")
parser.add_argument("-t", "--time", help="transition time in 100ms", default=4, type=int)
parser.add_argument("-o", "--off", help="turn off", action="store_true")
args = parser.parse_args()

bridge = phue.Bridge('192.168.1.113')
bridge.connect()

package = {}

if args.hue is not None:
	package['hue'] = args.hue

if args.saturation is not None:
	package['sat'] = args.saturation

if args.brightness is not None:
	package['bri'] = args.brightness

package['on'] = not args.off

bridge.set_light([int(x) for x in args.lights.split(',')], package, transitiontime=args.time)
