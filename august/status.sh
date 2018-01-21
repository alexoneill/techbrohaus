#!/bin/bash
# status.sh
# aoneill - 11/14/17

function main() {
  DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  source "${DIR}/support.sh"

  verify_token || return 1

  tmp=$(mktemp)
  curl "https://api-production.august.com/remoteoperate/${LOCK_ID}/status" \
    -X PUT \
    -H "x-august-api-key: 7cab4bbd-2693-4fc1-b99b-dec0fb20f9d4" \
    -H "x-kease-api-key: 7cab4bbd-2693-4fc1-b99b-dec0fb20f9d4" \
    -H "Content-Type: application/json" \
    -H "Accept-Version: 0.0.1" \
    -H "User-Agent: August/Luna-6.3.4 (Android; SDK 23; Nexus One)" \
    -H "x-august-access-token: $(cat ${ACCESS_TOKEN})" \
    2>/dev/null >${tmp}

  display_result ${tmp}
}

main $@
