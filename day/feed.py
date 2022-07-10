#!/usr/bin/python3
# Copyright (c) 2022 Sam Blenny
# SPDX-License-Identifier: CC-BY-NC-SA-4.0
#
# Atom feed generator for Markab Dev Journal entries
#
from string import Template
from datetime import datetime, timezone
import os
import re
import subprocess

FEED_FILE = '../feed.atom'   # <- feed xml will get writen to this file
N_MOST_RECENT = 10           # <- this many most recent entries get included


def ts(year, month, day, hour=0, minute=0):
  """Generate RFC3339 timestamp with 'T' and 'Z' for the specified date"""
  t = datetime(year, month, day, hour, minute, tzinfo=timezone.utc)
  return t.strftime("%Y-%m-%dT%H:%MZ")


# Atom feed xml template
TEMPLATE_FEED = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
 <title>${title}</title>
 <link href="${feed_url}" rel="self" />
 <link href="${site_url}" />
 <id>${feed_url}</id>
 <author><name>${author_name}</name></author>
 <updated>${updated}</updated>
${entries}
</feed>
"""

class Feed():
  """Class to hold the metadata and entry content for an Atom feed"""
  def __init__(self, title, feed_url, site_url, author, entries):
    t = datetime.now(tz=timezone.utc)
    self.data = {
      'title': title,
      'feed_url': feed_url,
      'site_url': site_url,
      'author_name': author,
      'updated': ts(t.year, t.month, t.day, t.hour, t.minute),
      'entries': "",
    }
    self.entries = entries

  def __str__(self):
    self.data['entries'] = "\n" + "\n".join([str(e) for e in self.entries])
    return Template(TEMPLATE_FEED).substitute(self.data)


def pandoc(filename):
  """Use pandoc to convert markdown to an Atom entry xml fragment"""
  cmd = ['pandoc', '-f',
         'markdown+lists_without_preceding_blankline',
         '--wrap=preserve', '--strip-comments', '-s',
         '--template=atom_template.html', filename
         ]
  result = subprocess.run(cmd, cwd=os.getcwd(), capture_output=True)
  if result.returncode != 0:
    print(result.stderr.decode())
    raise Exception("pandoc failed")
  return result.stdout.decode()


# Scan the current directory for markdown files
markdown_files = []
with os.scandir('.') as d:
  for entry in d:
    if entry.name.endswith('.md'):
      markdown_files.append(entry.name)

# Filter the list of markdown files to just the ones that have the correct
# metadata fields to render in Pandoc with the Atom template. (older entries
# do not have the necessary metadata)
atom_markdown = []
published = re.compile(r"published: (.*T.*Z)")
updated = re.compile(r"updated: .*T.*Z")
link = re.compile(r"link: .*https://")
for name in markdown_files:
  with open(name, 'r') as f:
    text = f.read()
    pub_ = published.search(text)
    up_ = updated.search(text)
    link_ = link.search(text)
    if pub_ and up_ and link_:
      # This makes tuples like `("'2022-07-10T04:18Z", '2022-07-10.md')`
      # so `sorted(..., reverse=True)` on the array will sort the filenames
      # according to their `published: ...` timestamp metadata field
      atom_markdown.append((pub_.group(1), name))

# Sort the files that have Atom metadata, most recent first
selected_files = [f for (pub, f) in sorted(atom_markdown, reverse=True)]

# Select only the most recent files
most_recent = selected_files[:N_MOST_RECENT]

# Convert the selected Markdown files to Atom entry xml fragments with Pandoc
entries = [pandoc(f) for f in most_recent]

# Render an Atom feed file with the entry fragments
title = 'Markab Dev Journal'
feed_url = 'https://samblenny.github.io/markab-dev-journal/feed.atom'
site = 'https://samblenny.github.io/markab-dev-journal/'
rights = 'Copyright (c) 2022 Sam Blenny'
author = 'Sam Blenny'
feed = Feed(title, feed_url, site, author, entries)
with open(FEED_FILE, 'w') as f:
  f.write(str(feed))



# Notes
"""
W3C Feed Validator to check quality of generated feed:
- https://validator.w3.org/feed/

RFC 4287: Atom Syncation Format
- https://datatracker.ietf.org/doc/html/rfc4287

RFC 3339: Date and Time on the Internet: Timestamps
- https://datatracker.ietf.org/doc/html/rfc3339

Github pages file extension to content-type mapping:
- Atom feed file extension needs to be .atom
  https://github.com/jshttp/mime-db/blob/v1.52.0/src/apache-types.json#L27-L29
- RSS feed file extension needs to be .rss
  https://github.com/jshttp/mime-db/blob/v1.52.0/src/apache-types.json#L440-L442

Html pages related to the atom feed should have a link like:
<link href="../feed.atom" type="application/atom+xml"
 rel="alternate" title="Atom feed" />
"""
