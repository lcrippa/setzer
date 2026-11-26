#!/bin/bash
set -euo pipefail

ROOT="$(dirname -- "$(realpath -- "${BASH_SOURCE[0]}")")"
STAMP="$ROOT/Setzer"
#EWS_SRC="$(realpath "$ROOT/ews-core/evolution-ews-3.62.1")"
#EWS_DEVEL="$ROOT/ews-core/ews-devel"
#EWSLIB=/usr/lib/evolution-ews

cd "$STAMP"
git reset --hard
git clean -fdx


# Exit cleanly if --cleanup was passed anywhere in the arguments
[[ " $* " == *" --cleanup "* ]] && exit 0

for i in "$ROOT"/myrepo/patches/*.patch; do
  patch -p1 < "$i"
done
cp -r ../myrepo/debian ./


DEB_BUILD_OPTIONS=nocheck dpkg-buildpackage -rfakeroot -uc -b
rm ../*.changes
rm ../*.buildinfo
rm ../*.tar.*z
rm ../*.dsc
