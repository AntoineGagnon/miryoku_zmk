#!/usr/bin/env bash
# Regenerate the interposer from source and verify it, end to end.
#
#   ./build.sh          generate, upgrade, ERC, DRC
#   ./build.sh fab      the above plus gerbers, drill, placement, renders and a fab zip
#
# Nothing here is interactive and every check is fatal, so a green run means the board in
# output/ is the board described by gen_interposer.py and gen_schematic.py.

set -euo pipefail
cd "$(dirname "$0")"

PROJECT=temper-tps43-interposer
KICAD_PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9

if [[ ! -x $KICAD_PY ]]; then
    echo "KiCad's bundled python is missing at $KICAD_PY" >&2
    echo "pcbnew is only importable from that interpreter." >&2
    exit 1
fi

# KiCad's CLI is noisy about the system fontconfig on macOS; none of it is actionable. The
# command's own exit status is preserved: piping into grep would otherwise hide failures.
NOISE='fontconfig|stdpbase|^Build Tech layer|^(Simplif|Calculating|Build BVH|Load Raytracing|Loading 3D|Reload time|Rendering)'
quiet() {
    local out status=0
    out=$("$@" 2>&1) || status=$?
    printf '%s\n' "$out" | grep -viE "$NOISE" || true
    if (( status != 0 )); then
        echo "FAIL: $* exited $status" >&2
        exit "$status"
    fi
}

step() { printf '\n\033[1m==> %s\033[0m\n' "$1"; }

step "Schematic"
python3 gen_schematic.py
quiet kicad-cli sch upgrade "$PROJECT.kicad_sch"

step "Board"
quiet "$KICAD_PY" gen_interposer.py

step "ERC"
# Delete the reports first so a stale one from a previous run can never pass the gate below.
rm -f "$PROJECT-erc.rpt" "$PROJECT-drc.rpt"
quiet kicad-cli sch erc --severity-all --exit-code-violations \
    --units mm -o "$PROJECT-erc.rpt" "$PROJECT.kicad_sch"

step "DRC (with schematic parity)"
quiet kicad-cli pcb drc --severity-all --exit-code-violations --schematic-parity \
    --units mm -o "$PROJECT-drc.rpt" "$PROJECT.kicad_pcb"

# kicad-cli reports violations on stdout but still exits 0 for parity issues, so gate on the
# report text as well as the exit status.
for report in "$PROJECT-erc.rpt" "$PROJECT-drc.rpt"; do
    if [[ ! -s $report ]]; then
        echo "FAIL: $report was not written" >&2
        exit 1
    fi
    if grep -qE '(\*\*|\*\*\*\*\*)? *Found [1-9]|ERC messages: [1-9]' "$report"; then
        echo "FAIL: $report is not clean" >&2
        grep -vE '^$' "$report" >&2
        exit 1
    fi
done
echo "ERC and DRC clean, schematic and board agree."

if [[ ${1:-} != fab ]]; then
    echo
    echo "Run './build.sh fab' to also produce output/."
    exit 0
fi

step "Fabrication output"
rm -rf output
mkdir -p output/gerbers

quiet kicad-cli pcb export gerbers -o output/gerbers/ \
    --layers F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,F.Paste,B.Paste,Edge.Cuts \
    --subtract-soldermask --check-zones --precision 6 "$PROJECT.kicad_pcb"

quiet kicad-cli pcb export drill -o output/gerbers/ --format excellon \
    --drill-origin absolute --excellon-zeros-format decimal --excellon-units mm \
    --excellon-separate-th --generate-map --map-format gerberx2 "$PROJECT.kicad_pcb"

quiet kicad-cli pcb export pos -o output/pos-front.csv --format csv --units mm \
    --side front "$PROJECT.kicad_pcb"

quiet kicad-cli sch export pdf -o output/schematic.pdf "$PROJECT.kicad_sch"
quiet kicad-cli pcb render --side top --width 950 --height 1180 -o output/top.png "$PROJECT.kicad_pcb"
quiet kicad-cli pcb render --side bottom --width 950 --height 1180 -o output/bottom.png "$PROJECT.kicad_pcb"

(cd output/gerbers && zip -q "../$PROJECT-gerbers.zip" ./*)

step "Sanity check of the fab output"
python3 - <<'PY'
import glob
import os
import re

gerbers = os.path.join("output", "gerbers")
required = ["F_Cu.gtl", "B_Cu.gbl", "F_Mask.gts", "B_Mask.gbs",
            "F_Silkscreen.gto", "B_Silkscreen.gbo",
            "F_Paste.gtp", "B_Paste.gbp", "Edge_Cuts.gm1", "-PTH.drl"]
missing = [r for r in required if not glob.glob(os.path.join(gerbers, "*" + r))]
assert not missing, "missing fab files: %s" % missing

outline = open(glob.glob(os.path.join(gerbers, "*Edge_Cuts.gm1"))[0]).read()
pts = [(int(a) / 1e6, int(b) / 1e6)
       for a, b in re.findall(r"X(-?\d+)Y(-?\d+)D0[12]", outline)]
w = max(p[0] for p in pts) - min(p[0] for p in pts)
h = max(p[1] for p in pts) - min(p[1] for p in pts)
# 20.0 mm is capped by Temper's choc switches, 40.0 mm by its nice!view header. See PCB_SPEC.
assert abs(w - 20.0) < 0.001 and abs(h - 40.0) < 0.001, \
    "board outline is %.3f x %.3f mm, expected 20.000 x 40.000" % (w, h)

# The glob has to be anchored: "*PTH.drl" also matches the NPTH file, which is empty.
drill = open(glob.glob(os.path.join(gerbers, "*-PTH.drl"))[0]).read()
tools = dict(re.findall(r"^T(\d+)C([\d.]+)", drill, re.M))
counts, cur = {}, None
for line in drill.splitlines():
    m = re.match(r"^T(\d+)$", line)
    if m:
        cur = m.group(1)
    elif line.startswith("X") and cur:
        counts[cur] = counts.get(cur, 0) + 1
by_size = {float(tools[t]): n for t, n in counts.items()}
assert by_size.get(1.0) == 24, "expected 24 x 1.0mm header holes, got %r" % by_size
print("outline %.3f x %.3f mm, drill %s" % (w, h, by_size))
PY

echo
echo "Fab package: output/$PROJECT-gerbers.zip"
ls -1 output output/gerbers | sed 's/^/  /'
