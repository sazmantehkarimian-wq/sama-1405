#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
cat "daramad final2.pdf".part* > "daramad final2.pdf"
cat "SAMA_ENTERPRISE_LAN_v3.8.5_LONG_TERM_OVER_365_1405-05-15(1).zip".part* > "SAMA_ENTERPRISE_LAN_v3.8.5_LONG_TERM_OVER_365_1405-05-15(1).zip"
echo "Reassembly complete."
sha256sum "daramad final2.pdf" "SAMA_ENTERPRISE_LAN_v3.8.5_LONG_TERM_OVER_365_1405-05-15(1).zip"
