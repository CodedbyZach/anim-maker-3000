#!/usr/bin/env bash
set -euo pipefail

if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "Python not found. Install Python 3." >&2
  exit 1
fi

VENV=".venv"
if [[ ! -d "$VENV" ]]; then
  "$PY" -m venv "$VENV"
fi

if [[ -f "$VENV/bin/activate" ]]; then
  source "$VENV/bin/activate"
  PIP="$VENV/bin/pip"
  ACTIVATE="source \"$VENV/bin/activate\""
else
  source "$VENV/Scripts/activate"
  PIP="$VENV/Scripts/pip.exe"
  ACTIVATE="source \"$VENV/Scripts/activate\""
fi

if [[ -f "requirements.txt" ]]; then
  "$PIP" install -r requirements.txt
fi

cat > run.sh <<EOF
#!/bin/bash
$ACTIVATE

echo "Select quality:"
echo "1) Low    - 480p15, fastest (-ql)"
echo "2) Medium - 720p30, default (-qm)  [default]"
echo "3) High   - 1080p60, slower (-qh)"
read -rp "Choice [1/2/3, default=2]: " q
q=\${q:-2}
case "\$q" in
  1) QUALITY="-ql" ;;
  2) QUALITY="-qm" ;;
  3) QUALITY="-qh" ;;
  *) echo "Invalid quality"; exit 1 ;;
esac

read -rp "Preview after render? (Y/n) [default=Y]: " pv
pv=\${pv:-Y}
if [[ "\$pv" =~ ^[Yy]\$ ]]; then
  PREVIEW="-p"
else
  PREVIEW=""
fi

echo
echo "Select animation(s):"
echo "1) HypnoticLissajous"
echo "2) PulseGrid"
echo "3) SurfaceWave3D  [default]"
echo "4) TextMorph"
echo "a) All scenes"
read -rp "Choice [1/2/3/4/a, default=3]: " s
s=\${s:-3}

set -u
if [[ "\$s" == "a" ]]; then
  echo "Rendering all scenes..."
  manim \$PREVIEW \$QUALITY -a main.py
else
  case "\$s" in
    1) SCENE="HypnoticLissajous" ;;
    2) SCENE="PulseGrid" ;;
    3) SCENE="SurfaceWave3D" ;;
    4) SCENE="TextMorph" ;;
    *) echo "Invalid selection"; exit 1 ;;
  esac
  echo "Rendering \$SCENE..."
  manim \$PREVIEW \$QUALITY main.py \$SCENE
fi
EOF

chmod +x run.sh