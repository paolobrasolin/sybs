#!/usr/bin/env python3
# coding: utf-8

import os

from argparse import ArgumentParser
import json
import html
import re

import yaml

from tqdm import tqdm

#=====================[ COMMANDLINE PARSING ]===================================

PARSER = ArgumentParser(
    description='Prepares raw quotations merging a string from amruta json dump.')

PARSER.add_argument(
    'query', type=str,
    help='query string')

PARSER.add_argument(
    '--source', type=str, default="amruta.json",
    help='amruta posts dump file from wp json api')

PARSER.add_argument(
    '--offset', type=int, default=1000,
    help='padding and merging distance for matches (default: 1000)')

ARGS = PARSER.parse_args()

#=====================[ MAIN LOOP ]=============================================

with open(ARGS.source, 'r') as input_file:
    all_posts = json.load(input_file)#[:600]

def post_contains(post, string):
    return post['content']['rendered'].lower().find(string.lower()) > 0

PATTERN = "(?:(?:(?!{0}).){{0,{1}}}){0}(?:.{{0,{2}}}{0})*(?:(?!{0}).){{0,{1}}}".format(ARGS.query,ARGS.offset,ARGS.offset*2)
SHERLOCK = re.compile(PATTERN, flags=re.IGNORECASE|re.MULTILINE|re.DOTALL)

def post_content(post):
    unescaped = html.unescape(post['content']['rendered'])
    stripped = re.sub('<[^<]+?>', '', unescaped)
    # normalised = re.sub('\n', '', stripped)
    return stripped

quotations = []

class folded_unicode(str): pass
class literal_unicode(str): pass
def folded_unicode_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='>')
def literal_unicode_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')
yaml.add_representer(folded_unicode, folded_unicode_representer)
yaml.add_representer(literal_unicode, literal_unicode_representer)

for post in tqdm(all_posts):
    if post_contains(post, ARGS.query):
        for quotation in SHERLOCK.findall(post_content(post)):
            entry = {
                        'amruta_id': post['id'],
                        'tags': [],
                        'text': folded_unicode(quotation.strip())
                    }
            quotations.append(entry)

if not os.path.exists('results'):
    os.makedirs('results')

with open("results/{0}.yml".format(ARGS.query), 'w') as yml_file:
    yaml.dump(quotations, yml_file, default_flow_style=False, allow_unicode=True)

