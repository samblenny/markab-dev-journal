#!/bin/sh
# Copyright (c) 2022 Sam Blenny
# SPDX-License-Identifier: CC-BY-NC-SA-4.0
#
# This was developed for the dash shell on Debian, so it should hopefully work
# on other POSIX compliant shells.
#
# Scroll down for new entry template (Copyright, YAML block with title, etc.)
#

# Make a YYYY-MM-DD formatted date string
DATE_PREFIX=`date -u "+%Y-%m-%d"`

# Generate 3 candidate journal entry file names
FILE_A=$DATE_PREFIX.md
FILE_B=${DATE_PREFIX}b.md
FILE_C=${DATE_PREFIX}c.md

# Pick a journal entry file name that does not conflict with existing file
ENTRY_FILE=
if [ ! -e $FILE_A ]; then
    echo "$FILE_A is available"
    ENTRY_FILE=$FILE_A
    else
     echo "$FILE_A is already in use"
     if [ ! -e $FILE_B ]; then
         echo "$FILE_B is available"
         ENTRY_FILE=$FILE_B
     else
         echo "$FILE_B is already in use"
         if [ ! -e $FILE_C ]; then
             echo "$FILE_C is available"
             ENTRY_FILE=$FILE_C
         else
             echo "$FILE_C is already in use"
             echo "Too many entries already today. I give up. Good luck."
             exit 1
         fi
     fi
fi

ENTRY_PREFIX=`basename -s .md $ENTRY_FILE`
echo "Entry prefix is $ENTRY_PREFIX"

# Get a title to use for filling in the YAML block title field
echo "Enter the title you want to use (for YAML block, but omit quotes)..."
echo    "ruler: YYYY-MM-DD: |-------------------------------------|"
read -p "title: ${ENTRY_PREFIX}: " ENTRY_TITLE

# YAML-escape apostrophes in case title has words like "don't" or "I'm". YAML
# syntax is complex, but using `title: '...'` (single quoted string) should be
# pretty safe as long as instances of ' are escaped as '' (two apostrophes).
ENTRY_TITLE=`cat <<EOF | sed --posix "s/'/''/g"
${ENTRY_TITLE}
EOF
`

# This is the journal entry template (uses heredoc multi-line string syntax)
# ==========================================================================
ENTRY_TEMPLATE=$(cat <<HEREDOC
<!--
Copyright (c) 2022 Sam Blenny
SPDX-License-Identifier: CC-BY-NC-SA-4.0
-->

---
title: '${ENTRY_PREFIX}: ${ENTRY_TITLE}'
---

## [first subheading]
HEREDOC
)
# ==========================================================================


# This is the link template for inserting into the index
# ==========================================================================
INDEX_TEMPLATE=$(cat <<HEREDOC
<p><a href="day/${ENTRY_PREFIX}.html">${ENTRY_PREFIX}</a> — ${ENTRY_TITLE}</p>
HEREDOC
)
# ==========================================================================


echo "Creating $ENTRY_FILE from template..."
cat <<EOF >> $ENTRY_FILE
${ENTRY_TEMPLATE}
EOF

echo "Updating index..."
sed -i "/<!--MARKER-->/ a ${INDEX_TEMPLATE}" ../index.html
