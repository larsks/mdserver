#!/usr/bin/python

import argparse
import errno
import jinja2
import logging
import markdown
import os
import re
import sys
import yaml

from bottle import route, run, response, \
    static_file, HTTPError

args = None
page = None
default_config = os.path.join(
    os.environ['HOME'],
    '.config',
    'mdserver',
    'mdserver.yaml')

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--debug',
                   action='store_const',
                   const=logging.DEBUG,
                   dest='loglevel')
    p.add_argument('--verbose',
                   action='store_const',
                   const=logging.INFO,
                   dest='loglevel')
    p.add_argument('--config', '-f', default=default_config)
    p.add_argument('--listen', '-l', default='8080')
    p.add_argument('--directory', '-d')
    p.add_argument('--template', '-t',
                   default=os.environ.get('MDSERVER_TEMPLATE'))
    p.add_argument('--static', '-s', nargs=2, action='append')
    p.add_argument('--yaml', '-Y', action='store_true')

    p.set_defaults(loglevel=logging.WARN)
    return p.parse_args()

def parse_frontmatter(text):
    content = text
    metadata = {}

    mo = re.match('---\n(.*?)\n---\n(.*)', text, re.DOTALL)
    if mo:
        print 'frontmatter:'
        print mo.group(1)
        metadata = yaml.load(mo.group(1))
        content = mo.group(2)

    return content, metadata

def render_markdown(text, title=None):
    global args
    global page
    metadata = {}

    if args.yaml:
        text, metadata = parse_frontmatter(text)

    if title:
        metadata['title'] = title

    return page.render(
            content=markdown.markdown(text),
            **metadata)
    
def render_index(path):
    global page
    text = []

    for item in sorted(os.listdir(path)):
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
        content = fd.read()
    return render_markdown(content)

def render_static(path, root='.'):
    return static_file(path, root)

def static_handler(root):
    def _(path):
        return static_file(path, root)

    return _

def index():
    return render_index('.')

def render(path):
    if os.path.isdir(path):
        return render_index(path)
    elif path.endswith('.md') or path.endswith('.txt'):
        return render_file(path)
    elif os.path.isfile(path):
        return render_static(path)
    elif os.path.isfile('%s.md' % path):
        return render_file('%s.md' % path)
    elif os.path.isfile(path.replace('.html', '.md')):
        return render_file(path.replace('.html', '.md'))
    else:
        raise HTTPError(404)

def setup_routes():
    '''Because we're generating dynamic routes -- that must be defined
    before the default ones -- we can't use decorator-style routing with
    @route.'''

    global args

    if args.static:
        for urlprefix,staticdir in args.static:
            staticdir = os.path.expanduser(staticdir)
            logging.debug('adding dir "%s" for url prefix "%s"',
                          staticdir, urlprefix)
            route('%s/<path:path>' % urlprefix, 'GET',
                  static_handler(staticdir))

    route('/', 'GET', index)
    route('/<path:path>', 'GET', render)

def setup_template():
    global args
    global page

    args.template = os.path.expanduser(args.template)

    with open(args.template) as fd:
        page = jinja2.Template(fd.read())

def main():
    global args
    config = {}

    args = parse_args()

    logging.basicConfig(
        level=args.loglevel)

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

    setup_routes()
    setup_template()

    if args.directory:
        os.chdir(args.directory)

    if ':' in args.listen:
        addr, port = args.listen.split(':')
        port = int(port)
    else:
        addr = '127.0.0.1'
        port = int(args.listen)

    run(host=addr, port=port)

if __name__ == '__main__':
    main()

