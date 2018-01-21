#!/bin/bash
# support.sh
# aoneill - 11/13/17

function verify_token() {
  # Make sure the access token exists
  [[ ! -f ${ACCESS_TOKEN} ]] && echo "err: bad ACCESS_TOKEN" && return 1
  return 0
}

# Parse the access token and save it
function update_token() {
  grep "x-august-access-token" $1 \
    | sed -e "s/.*: //g" > ${ACCESS_TOKEN}
}

# Show a pretty-print of the JSON result
function display_result() {
  tail -n 1 $1 | jq
}
