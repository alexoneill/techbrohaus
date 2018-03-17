#!/bin/bash
# session.sh
# aoneill - 11/13/17

function main() {
  DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  source "${DIR}/support.sh"

  tmp=$(mktemp)
  curl "https://api-production.august.com/session" \
    -X POST \
    -H "x-august-api-key: 7cab4bbd-2693-4fc1-b99b-dec0fb20f9d4" \
    -H "x-kease-api-key: 7cab4bbd-2693-4fc1-b99b-dec0fb20f9d4" \
    -H "Content-Type: application/json" \
    -H "Accept-Version: 0.0.1" \
    -H "User-Agent: August/Luna-6.3.4 (Android; SDK 23; Nexus One)" \
    -d @- -D - << EOF 2>/dev/null >${tmp}
{
  "installId": "0000000-0000-0000-0000-000000000000",
  "password": "${PASS}",
  "identifier": "email:${EMAIL}"
}
EOF

  update_token ${tmp}
  display_result ${tmp}
}

main $@
