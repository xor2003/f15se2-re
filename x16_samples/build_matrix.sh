#!/bin/bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
SAMPLES="$ROOT/x16_samples"
DOSBUILD="$ROOT/mzretools/tools/dosbuild.sh"
UASM="$ROOT/UASM/GccUnixR/uasm"
SRC="$SAMPLES/IDEMO.C"
MANIFEST="$SAMPLES/matrix_manifest.json"

cd "$ROOT"

rm -f "$SAMPLES"/*.OBJ "$SAMPLES"/*.EXE "$SAMPLES"/*.MAP "$SAMPLES"/*.COD "$SAMPLES"/*.COM "$SAMPLES"/*.LST
cp "$SAMPLES/intdemo.c" "$SRC"

variants=(
  "ISOD small /AS /Od"
  "ISOT small /AS /Ot"
  "ISOX small /AS /Ox"
  "IMOD medium /AM /Od"
  "IMOT medium /AM /Ot"
  "IMOX medium /AM /Ox"
  "ILOD large /AL /Od"
  "ILOT large /AL /Ot"
  "IHOD huge /AH /Od"
  "IHOT huge /AH /Ot"
)

json_tmp=$(mktemp)
printf '[\n' > "$json_tmp"
first=1

emit_json() {
  local entry=$1
  if [ $first -eq 0 ]; then
    printf ',\n' >> "$json_tmp"
  fi
  first=0
  printf '%b' "$entry" >> "$json_tmp"
}

for variant in "${variants[@]}"; do
  set -- $variant
  id=$1
  model_name=$2
  model_flag=$3
  opt_flag=$4

  echo "== Building $id ($model_name, $opt_flag) =="
  DOSBOX_TIMEOUT=40 "$DOSBUILD" cc msc510 -i x16_samples/IDEMO.C -o "x16_samples/${id}.OBJ" -f "/Fc /Zi /Gs ${opt_flag} ${model_flag}"
  cp "$SAMPLES/IDEMO.COD" "$SAMPLES/${id}.COD"
  DOSBOX_TIMEOUT=40 "$DOSBUILD" link msc510 -i "x16_samples/${id}.OBJ" -o "x16_samples/${id}.EXE" -f "/M /INFORMATION"

  emit_json "  {\n    \"id\": \"${id}\",\n    \"format\": \"exe\",\n    \"compiler\": \"msc510\",\n    \"source\": \"IDEMO.C\",\n    \"memory_model\": \"${model_name}\",\n    \"optimization\": \"${opt_flag}\",\n    \"binary\": \"${id}.EXE\",\n    \"object\": \"${id}.OBJ\",\n    \"cod\": \"${id}.COD\",\n    \"map\": \"${id}.MAP\"\n  }"
done

for asm in ICOMDO ICOMBI; do
  echo "== Building $asm.COM =="
  "$UASM" -q -0 -bin -Fl="$SAMPLES/${asm}.LST" -Fo"$SAMPLES/${asm}.COM" "$SAMPLES/${asm}.ASM"
  emit_json "  {\n    \"id\": \"${asm}\",\n    \"format\": \"com\",\n    \"compiler\": \"uasm\",\n    \"source\": \"${asm}.ASM\",\n    \"memory_model\": \"tiny\",\n    \"optimization\": \"n/a\",\n    \"binary\": \"${asm}.COM\",\n    \"listing\": \"${asm}.LST\"\n  }"
done

printf '\n]\n' >> "$json_tmp"
mv "$json_tmp" "$MANIFEST"

echo "Wrote $MANIFEST"
