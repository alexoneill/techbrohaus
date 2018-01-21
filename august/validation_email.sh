#!/bin/bash
# validate_email.sh
# aoneill - 11/14/17

function main() {
  DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  source "${DIR}/support.sh"

  verify_token || return 1

  tmp=$(mktemp)
  curl "https://api-production.august.com/validation/email" \
    -X POST \
    -H "x-august-api-key: 7cab4bbd-2693-4fc1-b99b-dec0fb20f9d4" \
    -H "x-kease-api-key: 7cab4bbd-2693-4fc1-b99b-dec0fb20f9d4" \
    -H "Content-Type: application/json" \
    -H "Accept-Version: 0.0.1" \
    -H "User-Agent: August/Luna-6.3.4 (Android; SDK 23; Nexus One)" \
    -H "x-august-access-token: $(cat ${ACCESS_TOKEN})" \
    -d @- -D - << EOF 2>/dev/null >${tmp}
{
  "value": "${EMAIL}"
}
EOF

  update_token ${tmp}
  display_result ${tmp}
}

main $@
