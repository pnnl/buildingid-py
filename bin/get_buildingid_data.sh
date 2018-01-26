#!/usr/bin/env sh
#
# pnnl-buildingid: bin/get_buildingid_data.sh
#
# Copyright (c) 2018, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE.txt and WARRANTY.txt for details.

set -e # terminate on non-zero exit status
set -x # print commands when they are executed

command -v buildingid >/dev/null 2>&1 || {
  echo "The \`buildingid\` command is required but is not found."
  echo "To continue, install the \`pnnl-buildingid\` package for Python 3."
  exit 1
}

# ==============================================================================
# Buildings
# https://dev.socrata.com/foundry/data.cityofchicago.org/tf32-rk4u
# ==============================================================================

CHICAGO_DIR_RELPATH="data/dev.socrata.com/foundry/data.cityofchicago.org/tf32-rk4u"
CHICAGO_FILE_RELPATH="$CHICAGO_DIR_RELPATH/rows.csv"
CHICAGO_URL="https://data.cityofchicago.org/api/views/tf32-rk4u/rows.csv?accessType=DOWNLOAD&api_foundry=true"
mkdir -p "$CHICAGO_DIR_RELPATH"
curl "$CHICAGO_URL" | buildingid append2csv > "$CHICAGO_FILE_RELPATH"

# ==============================================================================
# building
# https://dev.socrata.com/foundry/data.cityofnewyork.us/hzv7-g8fs
# ==============================================================================

NEW_YORK_CITY_DIR_RELPATH="data/dev.socrata.com/foundry/data.cityofnewyork.us/hzv7-g8fs"
NEW_YORK_CITY_FILE_RELPATH="$NEW_YORK_CITY_DIR_RELPATH/rows.csv"
NEW_YORK_CITY_URL="https://data.cityofnewyork.us/api/views/hzv7-g8fs/rows.csv?accessType=DOWNLOAD&api_foundry=true"
mkdir -p "$NEW_YORK_CITY_DIR_RELPATH"
curl "$NEW_YORK_CITY_URL" | buildingid append2csv > "$NEW_YORK_CITY_FILE_RELPATH"

# ==============================================================================
# sf13m_bldg_footprint_attribZ_pgz_data
# https://dev.socrata.com/foundry/data.sfgov.org/2s2t-jwzp
# ==============================================================================

SAN_FRANCISCO_DIR_RELPATH="data/dev.socrata.com/foundry/data.sfgov.org/2s2t-jwzp"
SAN_FRANCISCO_FILE_RELPATH="$SAN_FRANCISCO_DIR_RELPATH/rows.csv"
SAN_FRANCISCO_URL="https://data.sfgov.org/api/views/2s2t-jwzp/rows.csv?accessType=DOWNLOAD&api_foundry=true"
mkdir -p "$SAN_FRANCISCO_DIR_RELPATH"
curl "$SAN_FRANCISCO_URL" | buildingid append2csv > "$SAN_FRANCISCO_FILE_RELPATH"
