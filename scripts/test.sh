#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build
if command -v iverilog >/dev/null; then
  compiler=(iverilog)
  runner=(vvp)
elif [[ -x /workspace/tools/iverilog/usr/bin/iverilog ]]; then
  compiler=(/workspace/tools/iverilog/usr/bin/iverilog -B /workspace/tools/iverilog/usr/lib/x86_64-linux-gnu/ivl)
  runner=(/workspace/tools/iverilog/usr/bin/vvp -M /workspace/tools/iverilog/usr/lib/x86_64-linux-gnu/ivl)
else
  echo 'Install Icarus Verilog (Debian/Ubuntu: apt-get install iverilog).' >&2
  exit 1
fi
for op in and nand or nor xor xnor not shift add sub mul div; do
  "${compiler[@]}" -g2012 -Wall -s "tb_$op" -o "build/$op.vvp" "Verilog/rtl/alu_$op.v" "Verilog/tb/tb_$op.v"
  "${runner[@]}" "build/$op.vvp" | tee "build/$op.log"
done
