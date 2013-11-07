#!/usr/bin/python

import os
import sys
import argparse

import jinja2
import markdown
from bottle import route, run, response, static_file

args = None
page = None

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--port', '-p', default=8080, type=int)
    p.add_argument('--directory', '-d')
    p.add_argument('--template', '-t',
            default='template.html')
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
    else:
        return render_static(path)

def main():
    global args
    global page

    args = parse_args()
    with open(args.template) as fd:
        page = jinja2.Template(fd.read())

    if args.directory:
        os.chdir(args.directory)

    run(port=args.port)

if __name__ == '__main__':
    main()

