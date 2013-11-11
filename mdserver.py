#!/usr/bin/python

import os
import sys
import argparse
import errno

import yaml
import jinja2
import markdown
from bottle import route, run, response, static_file, HTTPError

args = None
page = None
default_config = os.path.join(os.environ['HOME'], '.config', 'mdserver', 'mdserver.conf')

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--config', '-f', default=default_config)
    p.add_argument('--port', '-p', default=8080, type=int)
    p.add_argument('--directory', '-d')
    p.add_argument('--template', '-t')
    p.add_argument('--static', '-s')
    return p.parse_args()

def render_markdown(text, title=None):
    global page
    return page.render(
            content=markdown.markdown(text),
            title=title)
    
def render_index(path):
    global page
    text = []

    for item in os.listdir(path):
        itempath=os.path.join(path, item)
        text.append('- [%s](%s%s)' % (
            item,
            item,
            ('/' if os.path.isdir(itempath) else '')
            ))

    return render_markdown('\n'.join(text),
            title='Listing of %s' % path)

def render_file(path, title=None):
    global page
    with open(path) as fd:
        content = markdown.markdown(fd.read())
    return render_markdown(content)

def render_static(path, root='.'):
    return static_file(path, root)

@route('/')
def index():
    return render_index('.')

@route('/static/<path:path>')
def static(path):
    global args

    if args.static:
        return render_static(path, args.static)
    else:
        raise HTTPError(body='Static resource directory not configured')

@route('/<path:path>')
def render(path):
    if os.path.isdir(path):
        return render_index(path)
    elif path.endswith('.md') or path.endswith('.txt'):
        return render_file(path)
    elif os.path.isfile(path):
        return render_static(path)
    elif os.path.isfile('%s.md' % path):
        return render_file('%s.md' % path)
    else:
        raise HTTPError(404)

def main():
    global args
    global page
    config = {}

    args = parse_args()

    if args.config:
        try:
            with open(args.config) as fd:
                config = yaml.load(fd)
        except IOError as detail:
            if not detail.errno == errno.ENOENT:
                raise

    if not args.template:
        args.template = config.get('mdserver', {}).get('template')
    if not args.static:
        args.static = config.get('mdserver', {}).get('static')

    if not args.template:
        print >>sys.stderr, 'ERROR: you must specify a template'
        sys.exit(1)

    if not args.static:
        args.static = os.path.dirname(args.template)

    args.template = os.path.expanduser(args.template)
    args.static = os.path.expanduser(args.static)

    with open(args.template) as fd:
        page = jinja2.Template(fd.read())

    if args.directory:
        os.chdir(args.directory)

    run(port=args.port)

if __name__ == '__main__':
    main()

