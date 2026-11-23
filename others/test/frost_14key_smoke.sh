#!/usr/bin/env bash
# Requires a C++ compiler and librime development headers/libraries (no Lua plugin).
set -euo pipefail

root=$(cd -- "$(dirname -- "$0")/../.." && pwd)
scratch=$(mktemp -d /tmp/frost-14key-smoke.XXXXXX)
trap 'if [[ "$scratch" == /tmp/frost-14key-smoke.* ]]; then rm -rf -- "$scratch"; fi' EXIT
mkdir -p "$scratch/shared" "$scratch/user"

# Deploy the three fourteen-key schemas with their production rules and shared dictionary.
schemas=(rime_frost_14key rime_frost_double_pinyin_14key rime_frost_double_pinyin_flypy_14key)
for schema in "${schemas[@]}"; do
  grep -Eq "^[[:space:]]*- schema: ${schema}([[:space:]]|$)" "$root/default.yaml"
  cp "$root/$schema.schema.yaml" "$scratch/shared/"
done
cp "$root"/{default.yaml,rime_frost.schema.yaml,rime_frost_double_pinyin.schema.yaml,rime_frost_double_pinyin_flypy.schema.yaml,rime_frost.dict.yaml,essay.txt,symbols_v.yaml} "$scratch/shared/"
cp -R "$root"/{cn_dicts,cn_dicts_cell} "$scratch/shared/"
{
  printf 'patch:\n  schema_list:\n'
  printf '    - schema: %s\n' "${schemas[@]}"
} > "$scratch/user/default.custom.yaml"

"${CXX:-c++}" -std=c++11 "$root/others/test/frost_14key_smoke_test.cc" \
  -lrime -o "$scratch/smoke"
"$scratch/smoke" "$scratch/shared" "$scratch/user"
