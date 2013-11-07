#!/usr/bin/python

import os
import sys
import argparse
import mimetypes

import jinja2
import markdown
from bottle import route, run, response

page = None

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--port', '-p', default=8080, type=int)
    p.add_argument('--directory', '-d')
    p.add_argument('--template', '-t',
            default='template.html')
    return p.parse_args()

def render_index(path):
    global page
    text = []

    for item in os.listdir(path):
        text.append('- [%s](%s)' % (item, item))

    return page.render(content=markdown.markdown('\n'.join(text)))

def render_markdown(path):
    global page
    with open(path) as fd:
        content = markdown.markdown(fd.read())
    return page.render(content=content)

def render_static(path):
    content_type = mimetypes.guess_type(path)
    response.set_header('content-type', content_type[0])
    with open(path) as fd:
        return fd.read()

@route('/')
def index():
    return render_index('.')

@route('/<path:path>')
def render(path):
    if os.path.isdir(path):
        return render_index(path)
    elif path.endswith('.md') or path.endswith('.txt'):
        return render_markdown(path)
    else:
        return render_static(path)

def main():
    global page

    args = parse_args()
    with open(args.template) as fd:
        page = jinja2.Template(fd.read())

    if args.directory:
        os.chdir(args.directory)

    run(port=args.port)

if __name__ == '__main__':
    main()

