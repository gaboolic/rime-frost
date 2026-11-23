#!/usr/bin/env bash
# Requires a C++ compiler and librime development headers/libraries (no Lua plugin).
set -euo pipefail

root=$(cd -- "$(dirname -- "$0")/../.." && pwd)
scratch=$(mktemp -d /tmp/frost-14key-smoke.XXXXXX)
trap 'if [[ "$scratch" == /tmp/frost-14key-smoke.* ]]; then rm -rf -- "$scratch"; fi' EXIT
mkdir -p "$scratch/shared" "$scratch/user"

# Deploy only this schema, but use the production spelling rules and full dictionary.
grep -Eq '^[[:space:]]*- schema: rime_frost_14key([[:space:]]|$)' "$root/default.yaml"
cp "$root"/{default.yaml,rime_frost_14key.schema.yaml,rime_frost.schema.yaml,rime_frost.dict.yaml,essay.txt} "$scratch/shared/"
cp -R "$root"/{cn_dicts,cn_dicts_cell} "$scratch/shared/"
printf 'patch:\n  schema_list:\n    - schema: rime_frost_14key\n' > "$scratch/user/default.custom.yaml"

"${CXX:-c++}" -std=c++11 "$root/others/test/frost_14key_smoke_test.cc" \
  -lrime -o "$scratch/smoke"
"$scratch/smoke" "$scratch/shared" "$scratch/user"
