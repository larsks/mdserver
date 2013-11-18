# mdserver

Do you have a collection of [Markdown][] documents you would like to
render in your browser?  Would you find it convenient to be able to
instantly preview changes to a Markdown document you're current
editing?

Maybe [mdserver][] is for you.

[Mdserver][] is a small server for Markdown documents.  If you have a
directory containing:

    README.md
    another_document.md

And you run:

    mdserver

Then you can request:

- `http://localhost:8080/` to get a document index,
- `http://localhost:8080/another_document.md` to see the rendered
  version of `another_document.md`.  You can *also* request...

    - `http://localhost:8080/another_document.html`
    - `http://localhost:8080/another_doucment`

    ...to get the same thing.

This filename handling was implemented such that links in your
Markdown documents can always use `.html` extensions, so that they
will continue to work if you statically render your documents to HTML.

## Installation

You will need to install the Python modules list in
[requirements.txt][req].  The modules are probably already packages
for your distribution of choice, or you can run:

    pip install -r requirements.txt

Then you can drop `mdserver.py` somewhere in your `$PATH` (I usually
install it as `~/bin/mdserver`).

## Options

- `--config`, `-f` *CONFIG* -- path to a [YAML][] configuration file.
  See [Configuration][cf], below, for more information.
- `--directory`, `-d` *DIRECTORY* -- directory containing your
  Markdown documents.  By default `mdserver` uses your current working
  directory.
- `--template`, `-t` *TEMPLATE_PATH* -- path to the HTML template used for
  rendering Markdown documents.
- `--static`, `-s` *URL* *STATIC_PATH* -- URLs starting with *URL*
  will serve static assets from *STATIC_PATH*.
- `--yaml`, `-Y` -- enable support for [Jekyll YAML
  frontmatter][jekyll].
- `--listen`, `-l` [*ADDRESS*]:*PORT* -- Specify a port on which to
  listen (and optionally an address on which to bind).

## <a name="configuration">Configuration</a>

Mdserver will read configuration from a file, by default
`~/.config/mdserver/mdserver.yaml`.  You can specify an alternate
configuration file with the `-f` command line option.

The following command line:

    mdserver -l 8080 -t ~/lib/markdown/template.html \
      -s /static ~/lib/markdown

Would be represented by the following configuration file:

    mdserver:
      listen: 8080
      template: ~/lib/markdown/template.html
      static:
        - [ /static, ~/lib/markdown ]

[mdserver]: http://github.com/larsks/mdserver
[markdown]: http://en.wikipedia.org/wiki/Markdown
[req]: requirements.txt
[jekyll]: http://jekyllrb.com/docs/frontmatter/
[cf]: #configuration

