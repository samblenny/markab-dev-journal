# Copyright (c) 2022 Sam Blenny
# SPDX-License-Identifier: CC-BY-NC-SA-4.0
#
# This was developed on Debian, but it uses .POSIX in the hope of making
# things easy to port. You might need to do `sudo apt install pandoc`
# This uses GNU make's wildcard extensions (not POSIX).
#
.SUFFIXES:             # Disable default old-school inference rules
.PHONY: all clean

MD_FILES   = $(wildcard 20??-??-??*.md)
HTML_FILES = $(MD_FILES:.md=.html)

PD_TEMPLATE = pandoc_template.html
PD_FMT = -f markdown+lists_without_preceding_blankline+autolink_bare_uris
PD_OPT = --wrap=preserve --strip-comments -s --toc


# This will trigger the .md.html inference rule
all: $(HTML_FILES)
	@echo done

clean:
	rm -f $(HTML_FILES)

# Add inference rule for pandoc markdown to html conversion
.SUFFIXES: .md .html
.md.html:
	pandoc $(PD_FMT) $(PD_OPT) --template=$(PD_TEMPLATE) -o $@ $<
