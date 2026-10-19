"""Assemble the report without duplicating the submitted Verilog source."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ops='and nand or nor xor xnor not shift add sub mul div'.split()
for op in ops:
    count=16 if op=='not' else 512 if op in ('add','sub') else 256
    assert f'PASS {op}: {count} cases' in (ROOT/f'build/{op}.log').read_text(), op
descriptions={
'and': ('Bitwise AND',r'$X_i=A_i\land B_i$. A bit is one only when both inputs are one.'),
'nand': ('Bitwise NAND',r'$X_i=\neg(A_i\land B_i)$. This complements AND independently for each bit.'),
'or': ('Bitwise OR',r'$X_i=A_i\lor B_i$. A bit is one when at least one input bit is one.'),
'nor': ('Bitwise NOR',r'$X_i=\neg(A_i\lor B_i)$. A bit is one only when both input bits are zero.'),
'xor': ('Bitwise XOR',r'$X_i=A_i\oplus B_i$. Unequal input bits produce one.'),
'xnor': ('Bitwise XNOR',r'$X_i=\neg(A_i\oplus B_i)$. Equal input bits produce one.'),
'not': ('Bitwise NOT',r'$X_i=\neg A_i$. This is a unary operation; there is no B port.'),
'shift': ('Programmable arithmetic shifter',r'''The handout defines a programmable fill bit, rather than the automatic sign extension of Verilog's arithmetic-right-shift operator. B[3] selects right (1) or left (0), B[2:1] selects distance 0--3, and B[0] supplies the fill bit. The combinational loop performs up to three one-bit shifts, initializing X to A and Y to zero. Each step captures the departing X bit in Y before replacing it with the fill bit. Left-shift overflow is right-aligned; right-shift overflow is left-aligned. Zero distance preserves A and clears Y. Both assignment examples are covered by exhaustive tests.

For distance $s$ and fill $f$, left shift gives $X=(A2^s+f(2^s-1))\bmod16$, $Y=\lfloor A/2^{4-s}\rfloor$. Right shift gives $X=\lfloor A/2^s\rfloor+f(16-2^{4-s})$, $Y=(A\bmod2^s)2^{4-s}$. These formulas are also the independent test oracle.'''),
'add': ('Unsigned addition with carry',r'''A five-bit sum preserves the carry: $T=A+B+C_{in}$, $X=T\bmod16$, $C_{out}=\lfloor T/16\rfloor$. Explicit zero extension prevents premature four-bit truncation. For example, $15+15+1=31$ produces X=15 and carry=1. All 512 input combinations are checked.'''),
'sub': ('Unsigned subtraction with carry/no-borrow',r'''The two's-complement adder implements $T=A+\overline{B}+C_{in}$. Consequently, $X=(A-B-(1-C_{in}))\bmod16$. For ordinary subtraction use $C_{in}=1$; use zero to subtract an incoming borrow. $C_{out}=1$ means no unsigned borrow; borrow-out is its complement. For example, $0-1$ with carry-in 1 gives X=15 and carry-out 0. Chaining the carry directly supports multi-nibble subtraction. The bench uses signed integer subtraction and a comparison, not the complemented-adder expression.'''),
'mul': ('Unsigned multiplication',r'''The eight-bit product is split into low nibble X and high nibble Y, so $16Y+X=AB$. For example, $15\times15=225$ gives Y=14 and X=1. Both operands are explicitly extended. The test oracle uses repeated addition, independently of the multiplication operator.'''),
'div': ('Unsigned division and remainder',r'''For nonzero B, X is the integer quotient and Y is the remainder: $A=BX+Y$ and $0\leq Y<B$. The test oracle uses repeated subtraction. All 240 valid pairs and all 16 zero-divisor pairs are exercised. For B=0, the explicit divide\_by\_zero output is asserted, X=15, and Y=A. These deterministic sentinel values are not a mathematical quotient and remainder and must be interpreted with the error flag. The handout does not prescribe zero-divisor behavior; this is a documented interface choice.''')}
header=r'''\documentclass[11pt]{article}
\usepackage[margin=0.8in]{geometry}
\usepackage{graphicx,listings,xcolor,longtable,hyperref,tikz}
\hypersetup{colorlinks=true,linkcolor=blue}
\lstset{language=Verilog,basicstyle=\ttfamily\scriptsize,breaklines=true,numbers=left,numberstyle=\tiny,frame=single,columns=fullflexible,keepspaces=true,showstringspaces=false,captionpos=t}
\renewcommand{\lstlistingname}{Algorithm}
\input{identity.tex}
\title{Building an Integer ALU\\Step 2: Separate Four-Bit ALU Functions}
\author{\groupname\\\members\\\course}
\date{\reportdate}
\begin{document}
\maketitle
\noindent The course-provided LaTeX template was not supplied; this report uses a standalone article layout.
\tableofcontents
\newpage
\section{Introduction and goals}
Step 2 develops and validates twelve independent combinational ALU modules: seven bitwise logic functions, a programmable shifter, and four integer arithmetic operations. The goals are to preserve every specified result bit, make control and boundary cases explicit, and demonstrate correctness through independent exhaustive unit tests and simulation waveforms. No final-stage opcode selector or integrated ALU is included; integration belongs to the final project step.

\section{Interfaces and design choices}
All data ports are four bits. Inputs A and B are unsigned integers 0--15; X is the primary output. The handout does not specify signed multiplication or division, so this implementation uses unsigned arithmetic. Y carries the high product nibble, division remainder, or shifted-out bits. Only addition and subtraction expose carry-in and carry-out: the handout does not define carry semantics for multiply or divide, whose complete results are instead retained in X and Y. Confirm this interpretation with the instructor if a uniform carry interface is required.

Each function has its own RTL file and dedicated unit-test file. Modules are combinational and require no clock or reset. Delay statements appear only in testbenches. The shift implementation follows the custom fill and overflow rules in the assignment, including the right-shift example's left-aligned overflow.

\subsection{Logic truth table (applied independently to each bit)}
\begin{center}
\begin{tabular}{cc|ccccccc}
A&B&AND&NAND&OR&NOR&XOR&XNOR&NOT A\\\hline
0&0&0&1&0&1&0&1&1\\
0&1&0&1&1&0&1&0&1\\
1&0&0&1&1&0&1&0&0\\
1&1&1&0&1&0&0&1&0
\end{tabular}
\end{center}

\subsection{Arithmetic and shift boundary cases}
\begin{center}
\begin{tabular}{lrrrrl}
Function&A&B&Carry-in&X&Other outputs\\\hline
Add&15&15&1&15&Carry-out=1\\
Subtract&0&1&1&15&Carry-out=0 (borrow)\\
Subtract&0&0&0&15&Carry-out=0 (incoming borrow)\\
Multiply&15&15&--&1&Y=14\\
Divide&15&4&--&3&Y=3, error=0\\
Divide&11&0&--&15&Y=11, error=1\\
Left shift&11&6&--&8&Y=5 (handout example)\\
Right shift&5&13&--&13&Y=4 (handout example)
\end{tabular}
\end{center}

\section{Validation method and measured results}
Icarus Verilog 12.0 compiled each unit separately with SystemVerilog support and warnings enabled. The testbenches enumerate all binary inputs, wait 10 ns after each stimulus, and use case-inequality comparisons so unknown outputs fail instead of being silently accepted. A failed assertion calls \texttt{\$fatal}; the shell runner preserves a failing exit status through its logging pipeline. VCD traces are captured directly from each device under test, and the plotted figures are cropped from those traces, not fabricated expected waveforms.

Each binary logic operation has 256 cases; NOT has 16; shift has 256; addition and subtraction have 512 each; multiplication and division have 256 each. \textbf{All 3,344 cases passed across twelve separate unit tests.} For the binary gates the oracle evaluates a per-bit truth table. Arithmetic reference models use integer arithmetic, repeated addition, or repeated subtraction. Shift expectations use the closed-form equations above rather than repeating the RTL shift loop.

The exhaustive runs cover zero and maximum operands, every carry input, every shift direction/distance/fill combination, overflowing additions and products, subtraction underflow, exact and inexact division, and every zero divisor. These are functional RTL simulations; they do not establish timing closure, gate counts, physical implementation, or behavior for unknown input states. Larger optional ALU widths are outside this required four-bit submission.
'''
sections=[]
for op in ops:
    title,description=descriptions[op]
    inputs='A' if op=='not' else 'A, B'
    if op in ('add','sub'): inputs+=', carry-in'
    outputs='X'
    if op in ('shift','mul','div'): outputs+=', Y'
    if op in ('add','sub'): outputs+=', carry-out'
    if op=='div': outputs+=', error'
    section=f'\n\\clearpage\n\\section{{{title}}}\n{description}\n'
    section+=r'''
\subsection{Functional circuit diagram}
\begin{center}
\begin{tikzpicture}
\node[draw,minimum width=4cm,minimum height=1cm] (core) at (0,0) {'''+title+r'''};
\draw[->] (-6,0) node[left] {'''+inputs+r'''} -- (core.west);
\draw[->] (core.east) -- (5.5,0) node[right] {'''+outputs+r'''};
\end{tikzpicture}
\end{center}
This is a functional port diagram, not a synthesized gate-level schematic.
'''
    section+=f'\\subsection{{Verilog implementation}}\n\\lstinputlisting[caption={{{title}: module}}]{{../Verilog/rtl/alu_{op}.v}}\n'
    section+=f'\\subsection{{Independent unit test}}\n\\lstinputlisting[caption={{{title}: exhaustive unit test}}]{{../Verilog/tb/tb_{op}.v}}\n'
    section+=f'\\subsection{{Observed waveform}}\n\\noindent\\includegraphics[width=\\linewidth]{{figures/{op}.pdf}}\\par\n'
    if op=='shift':
        section+=r'''At 930 ns, A=5 and B=D give X=D and Y=4, matching the right-shift example. The second crop shows A=B (hexadecimal eleven), B=6, X=8, Y=5 at 1820 ns, matching the left-shift example.
\par\noindent\includegraphics[width=\linewidth]{figures/shift_left.pdf}\par
'''
    elif op=='not': section+='The trace sweeps every input from hexadecimal 0 through F; X descends from F to 0.\n'
    elif op=='add': section+='The crop holds A=7 while B crosses 8: carry-out rises as the five-bit sum reaches sixteen; adjacent samples exercise both carry inputs.\n'
    elif op=='sub': section+='The crop holds A=7 while B crosses 7: carry-out distinguishes no borrow from borrow; alternating carry-in values also exercise incoming borrow.\n'
    elif op=='mul': section+='With A=E, increasing B changes both product nibbles. For B=F the product is D2, so Y=D and X=2.\n'
    elif op=='div': section+='The crop includes A=F, B=0 at 2400 ns: error rises, X=F, Y=F. For nonzero B, X and Y return to quotient and remainder.\n'
    else: section+='The crop sweeps B while A=E. Each displayed output follows the per-bit truth table; the testbench checks the full input space beyond this crop.\n'
    sections.append(section)
tail=r'''
\clearpage
\section{Reproducing the results}
From the repository root, run the commands below. Icarus Verilog, Python 3 with Matplotlib, and a LaTeX installation with listings, graphics, and TikZ are required. The test runner also recognizes the local Icarus installation prepared in this cloud environment. No server or credentials are required.
\begin{lstlisting}[language=bash,caption={Reproduce simulations and report}]
bash scripts/test.sh
python scripts/render_waveforms.py
python scripts/build_report.py
cd latex
pdflatex -interaction=nonstopmode -halt-on-error report.tex
pdflatex -interaction=nonstopmode -halt-on-error report.tex
\end{lstlisting}
RTL and unit benches are in the Verilog folder. Raw traces and per-unit test logs are generated in build. The report source and vector waveform figures are in latex. The companion archive contains the PDF, source folders, and scripts. Replace the identity placeholders and rebuild the report before naming the archive GroupName-ProjectStep2.zip. Review the implementation and explanations, and adapt this standalone layout to the course template if required.

\section{Conclusion}
The twelve separate four-bit functions passed exhaustive functional simulation. The two shift examples agree with the assignment, arithmetic outputs preserve carry, high-product bits, and division remainders, and zero-divisor behavior is explicit. The main design ambiguities were overflow alignment in the shifter and the carry convention for subtraction; these were resolved through the supplied examples and a documented no-borrow interface. Independent reference models and full input enumeration make the results stronger than a few selected demonstrations. The next project step can instantiate these modules beneath an opcode controller without merging their implementations. Physical synthesis and optional wider datapaths remain separate work.
\end{document}
'''
(ROOT/'latex/report.tex').write_text(header+''.join(sections)+tail)
print('Wrote latex/report.tex')
