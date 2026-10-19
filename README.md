# Computer-Arch — Project Step 2

Twelve separate four-bit combinational Verilog modules, twelve exhaustive unit
testbenches, actual VCD simulation traces, plotted waveforms, and a LaTeX/PDF report.
No final-stage controller is included.

## Run

Install Icarus Verilog (`iverilog` and `vvp`), Python 3 with Matplotlib, and
LaTeX with `listings`, `graphicx`, and TikZ. The test runner also supports the
local Icarus 12 installation under `/workspace/tools/iverilog` in this environment.

```sh
bash scripts/test.sh       # 12 independent tests, 3,344 exhaustive cases
bash scripts/report.sh     # rerun tests, render actual traces, compile PDF twice
```

Tests fail on mismatches or unknown outputs. Generated logs, VCD files, and
simulation executables are under `build/`. The report is `latex/report.pdf`.

## Interfaces

| Module | Inputs | Outputs / convention |
|---|---|---|
| `alu_and`, `alu_nand`, `alu_or`, `alu_nor`, `alu_xor`, `alu_xnor` | `a`, `b` | bitwise `x` |
| `alu_not` | `a` | bitwise `x` |
| `alu_shift` | `a`, `b` | `x`, shifted-out bits `y` |
| `alu_add` | `a`, `b`, `cin` | `x`, `cout`: a+b+cin |
| `alu_sub` | `a`, `b`, `cin` | `x`, `cout`: a-b-(1-cin); cout=1 means no borrow |
| `alu_mul` | `a`, `b` | `{y,x}` = full unsigned product |
| `alu_div` | `a`, `b` | quotient `x`, remainder `y`, `divide_by_zero` |

All data ports are four bits; flags are one bit. Arithmetic is unsigned.
Ordinary subtraction requires `cin=1`. Multiply and divide have no carry ports;
their full results use both data outputs. For division by zero, the error flag
is 1, `x=15`, and `y=a`; these are sentinel outputs, not a valid division.
The report explicitly identifies these choices where the assignment is ambiguous.

Shifter control: `b[3]` is direction (0 left, 1 right), `b[2:1]` is distance
(0–3), and `b[0]` is the fill bit. Left overflow is right-aligned; right overflow
is left-aligned. Both handout examples are exercised, including
`a=1011,b=0110 -> x=1000,y=0101` and
`a=0101,b=1101 -> x=1101,y=0100`.

## Before submission

Review **`latex/identity.tex`**, which contains Zion, Anamol Khadka, Prashant Subedi,
Davos A De Hoyos, and CS3339. Update the report date if needed. Then run
`bash scripts/report.sh`. The supplied course template
was unavailable, so the report uses a standalone article layout. Review it
against your course's template and interface expectations. Functional block
diagrams are included; they are not synthesized gate schematics. Optional wider
ALUs are not implemented.

Run `python scripts/package.py` to create
`/workspace/artifacts/Zion-ProjectStep2.zip` and a copy of the report PDF.
The filename is derived from the group name. It contains the PDF, `latex/`
sources/figures, `Verilog/` modules/tests/raw waveforms/test logs, and build scripts.

The Python generation scripts record how the source and report were assembled.
Normal development does not require `generate_project.py`; it overwrites the
generated RTL and benches. `build_report.py` preserves `identity.tex` and only
builds after all expected test PASS records are present.
