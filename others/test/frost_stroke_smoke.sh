#!/usr/bin/env bash
# Requires a C++ compiler and librime development headers/library.
set -euo pipefail

root=$(cd -- "$(dirname -- "$0")/../.." && pwd)
scratch=$(mktemp -d /tmp/frost-stroke-smoke.XXXXXX)
trap 'if [[ "$scratch" == /tmp/frost-stroke-smoke.* ]]; then rm -rf -- "$scratch"; fi' EXIT
mkdir -p "$scratch/shared" "$scratch/user"

# Supply only the shared data needed by this test, as on a minimal frontend.
cp "$root"/{default.yaml,rime_frost_stroke_t9.schema.yaml,stroke.dict.yaml,essay.txt} "$scratch/shared/"
# Deploy only stroke, without requiring libraries for the unrelated Frost schemas.
printf 'patch:\n  schema_list:\n    - schema: rime_frost_stroke_t9\n' > "$scratch/user/default.custom.yaml"

"${CXX:-c++}" -std=c++11 "$root/others/test/frost_stroke_smoke_test.cc" \
  -lrime -o "$scratch/smoke"
"$scratch/smoke" "$scratch/shared" "$scratch/user"
