#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if [[ $# != 1 ]]; then
	exit 1
fi

head -1001 "$1" | sponge "$1"
