#!/usr/bin/env bash

# List content belonging to a specified stream
#
# Copyright 2015, Outernet Inc.
# Some rights reserved.
# 
# This software is free software licensed under the terms of GPLv3. See COPYING
# file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
#

set -e

SRC=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
SCRIPTNAME=$(basename ${BASH_SOURCE[0]})
VERSION=$(cat "$SRC/VERSION")

. "$SRC/util/pathutil.sh"
. "$SRC/util/streamutil.sh"

help() {
    cat <<EOF
$SCRIPTNAME v$VERSION

Usage:
    $SCRIPTNAME LABEL

Parameter:
    LABEL       stream label
EOF
}

label=$1

if [ -z "$label" ]
then
    help
    exit 1
fi

if [ -z "$(getstream "$label" || true)" ]
then
    echo "${label}: no such stream"
    exit 1
fi

grep "$label" $PATH_WC/.broadcast | cut -d: -f1 \
    | pjoinseg / "$OUTERNET_CONTENT" ".broadcast"