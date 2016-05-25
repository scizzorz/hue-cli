#!/usr/bin/env python

import argparse
import json
import os
import phue
import re

CHARS = re.compile('[^a-z ]')

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
    'default': '1',
  }

# look up a light by index or fuzzy name
# return the phue.Light object

def find_light(bridge, idx):
  lights = bridge.get_light_objects('id')
  try:
    return lights[int(idx)]
  except:
    pass

  idx = CHARS.sub('', idx.lower())
  for i, obj in lights.items():
    name = CHARS.sub('', obj.name.lower())
    if idx in name:
      return obj

  raise Exception('Unknown light: {}'.format(idx))

# look up a group by index or fuzzy name
# return the index

def find_group(bridge, idx):
  groups = bridge.get_group()

  if idx in groups:
    return int(idx)

  idx = CHARS.sub('', idx.lower())
  for i, obj in groups.items():
    name = CHARS.sub('', obj['name'].lower())
    if idx in name:
      return int(i)

  raise Exception('Unknown group: {}'.format(idx))

# default command

def main(args):
  bridge = phue.Bridge('192.168.0.101')
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

  if args.dim:
    package['bri'] = 0

  package['on'] = not args.off

  if args.group:
    group = find_group(bridge, args.group)
    bridge.set_group(group, package, transitiontime=args.time*10)
    return

  lights = [find_light(bridge, x).light_id for x in args.lights.split(',')]
  bridge.set_light(lights, package, transitiontime=args.time*10)

# subcommands

def list_cmd(args):
  bridge = phue.Bridge('192.168.0.101')
  bridge.connect()

  lights = bridge.get_light_objects('id')
  for i, obj in lights.items():
    print('{: >3} {}'.format(i, obj.name))

def groups_cmd(args):
  bridge = phue.Bridge('192.168.0.101')
  bridge.connect()

  groups = bridge.get_group()
  for i, obj in sorted(groups.items()):
    print('{: >3} {}'.format(i, obj['name']))

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
lights_group.add_argument('-l', '--lights', default=config['default'], help='comma-separated light indices')
lights_group.add_argument('-g', '--group', help='a group name')

parser.add_argument('-t', '--time', help='transition time in seconds', default=0.4, type=float)
parser.add_argument('-o', '--off', help='turn off lights', action='store_true')
parser.add_argument('-d', '--dim', help='dim the lights', action='store_true')

lights_parser = subs.add_parser('list', help='list lights')
lights_parser.set_defaults(func=list_cmd)

lights_parser = subs.add_parser('groups', help='list groups')
lights_parser.set_defaults(func=groups_cmd)

args = parser.parse_args()

args.func(args)

json.dump(config, open(RCFILE, 'w'))
