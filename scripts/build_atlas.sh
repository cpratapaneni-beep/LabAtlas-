#!/bin/sh
# Rebuild the atlas data from a source atlas file, in the order the steps depend
# on each other:
#
#   1. clean the provable errors (clean_atlas_data.py)
#   2. check the NIH figures against RePORTER, if the machine can reach it
#      (nih_reporter_verify.py; skipped with --no-nih)
#   3. place every investigator on the wet/dry axis with the trained model,
#      measuring it on the locked test set first (ml/wetdry.py), then write
#      the department-by-department report the page reads (department_report.py)
#   4. audit the result (audit_atlas.py) - exits non-zero on any error. With
#      --no-nih the NIH figures stay unverified, so the audit will still list
#      the grant errors only RePORTER can settle; everything else must be clean.
#
#   sh scripts/build_atlas.sh source.html out.html [--no-nih]
#
# Every step writes its log and reports under build/. Nothing is overwritten
# except out.html and build/.
set -e
here=$(cd "$(dirname "$0")/.." && pwd)
src=$1; out=$2; nonih=$3
[ -n "$src" ] && [ -n "$out" ] || { echo "usage: sh scripts/build_atlas.sh source.html out.html [--no-nih]"; exit 2; }
mkdir -p build
python3 "$here/scripts/clean_atlas_data.py" "$src" build/1_clean.html --log build/clean
step=build/1_clean.html
if [ "$nonih" != "--no-nih" ]; then
  python3 "$here/scripts/nih_reporter_verify.py" "$step" --patch --out build/nih
  step=build/1_clean_nih.html
fi
L="--split $here/ml/split.json --labels $here/ml/gold_labels.csv --extra $here/ml/gold_labels_dept.csv"
python3 "$here/ml/wetdry.py" evaluate --data "$step" $L --out build/wetdry_report
python3 "$here/ml/wetdry.py" predict  --data "$step" $L --out build/predictions.json
python3 "$here/ml/department_report.py" "$step" build/predictions.json build/wetdry_report/test_predictions.csv $L --out build/wetdry_report
python3 "$here/ml/apply_wetdry.py" "$step" build/predictions.json build/wetdry_report/evaluation.csv \
  --departments build/wetdry_report/departments.json --confidence build/wetdry_report/confidence.json -o "$out"
python3 "$here/scripts/audit_atlas.py" "$out" --out build/audit
