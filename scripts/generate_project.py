"""Generate the independent four-bit modules and exhaustive unit benches."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RTL = ROOT / 'Verilog/rtl'
TB = ROOT / 'Verilog/tb'
ops = {'and': 'a & b', 'nand': '~(a & b)', 'or': 'a | b',
       'nor': '~(a | b)', 'xor': 'a ^ b', 'xnor': '~(a ^ b)', 'not': '~a'}
for name, expr in ops.items():
    ports = 'input wire [3:0] a, ' + ('' if name == 'not' else 'input wire [3:0] b, ') + 'output wire [3:0] x'
    (RTL / f'alu_{name}.v').write_text(f'`timescale 1ns/1ps\nmodule alu_{name}({ports});\n  assign x = {expr};\nendmodule\n')

sources = {
'add': '''module alu_add(input wire [3:0] a, b, input wire cin,
  output wire [3:0] x, output wire cout);
  assign {cout, x} = {1'b0,a} + {1'b0,b} + {4'b0,cin};
endmodule
''',
'sub': '''// cin is carry/no-borrow input: x = a - b - (1-cin).
module alu_sub(input wire [3:0] a, b, input wire cin,
  output wire [3:0] x, output wire cout);
  assign {cout, x} = {1'b0,a} + {1'b0,~b} + {4'b0,cin};
endmodule
''',
'mul': '''module alu_mul(input wire [3:0] a, b,
  output wire [3:0] x, y);
  wire [7:0] product;
  assign product = {4'b0,a} * {4'b0,b};
  assign {y,x} = product;
endmodule
''',
'div': '''// Unsigned division. Invalid divisor is explicit, never silently valid.
module alu_div(input wire [3:0] a, b,
  output wire [3:0] x, y, output wire divide_by_zero);
  assign divide_by_zero = (b == 0);
  assign x = divide_by_zero ? 4'hf : a / b;
  assign y = divide_by_zero ? a : a % b;
endmodule
''',
'shift': '''// b[3]: direction, b[2:1]: distance, b[0]: fill.
// y collects shifted-out bits, initially zero, in their shift positions.
module alu_shift(input wire [3:0] a, b,
  output reg [3:0] x, y);
  integer i;
  always @* begin
    x = a;
    y = 4'b0000;
    for (i = 0; i < 3; i = i + 1) begin
      if (i < b[2:1]) begin
        if (b[3]) begin
          y = {x[0], y[3:1]};
          x = {b[0], x[3:1]};
        end else begin
          y = {y[2:0], x[3]};
          x = {x[2:0], b[0]};
        end
      end
    end
  end
endmodule
'''}
for name, source in sources.items():
    (RTL / f'alu_{name}.v').write_text('`timescale 1ns/1ps\n' + source)

for name in [*ops, *sources]:
    arith = name in ('add','sub')
    two = name in ('mul','div','shift')
    decl = 'wire [3:0] x;' + (' wire [3:0] y;' if two else '')
    decl += ' wire cout;' if arith else ''
    decl += ' wire divide_by_zero;' if name == 'div' else ''
    ports = '.a(a), ' + ('' if name == 'not' else '.b(b), ') + '.x(x)'
    ports += ', .cin(cin), .cout(cout)' if arith else ''
    ports += ', .y(y)' if two else ''
    ports += ', .divide_by_zero(divide_by_zero)' if name == 'div' else ''
    if name in ops:
        # Per-bit truth-table oracle, independent of vector RTL operations.
        truths = {'and':8,'nand':7,'or':14,'nor':1,'xor':6,'xnor':9,'not':3}
        expected = f'''expected = 0;
          for (k=0; k<4; k=k+1)
            expected = expected | ((({truths[name]} >> (2*((ia>>k)&1)+((ib>>k)&1))) & 1) << k);
          if (x !== expected[3:0]) $fatal(1,"{name} a=%d b=%d",ia,ib);'''
    elif arith:
        formula = 'ia + ib + ic' if name == 'add' else 'ia - ib - (1-ic)'
        carry = '(expected >= 16)' if name == 'add' else '(expected >= 0)'
        expected = f'''expected = {formula};
          if (x !== (expected & 15) || cout !== {carry})
            $fatal(1,"{name} a=%d b=%d cin=%d",ia,ib,ic);'''
    elif name == 'mul':
        expected = '''expected = 0;
          for(k=0;k<ib;k=k+1) expected = expected + ia;
          if ({y,x} !== expected[7:0]) $fatal(1,"mul a=%d b=%d",ia,ib);'''
    elif name == 'div':
        expected = '''if (ib == 0) begin
            if (divide_by_zero !== 1'b1 || x !== 4'hf || y !== a)
              $fatal(1,"divide by zero a=%d",ia);
          end else begin
            expected=0; remainder=ia;
            while (remainder >= ib) begin
              remainder=remainder-ib; expected=expected+1;
            end
            if (divide_by_zero !== 1'b0 || x !== expected[3:0] || y !== remainder[3:0])
              $fatal(1,"div a=%d b=%d",ia,ib);
          end'''
    else:
        expected = '''distance=(ib>>1)&3; fill=ib&1;
          if (ib < 8) begin
            expected=((ia*(1<<distance)) + fill*((1<<distance)-1)) & 15;
            overflow=ia>>(4-distance);
          end else begin
            expected=(ia>>distance) + fill*(16-(1<<(4-distance)));
            overflow=(ia & ((1<<distance)-1)) << (4-distance);
          end
          if (x !== expected[3:0] || y !== overflow[3:0])
            $fatal(1,"shift a=%b b=%b x=%b y=%b",a,b,x,y);'''
    bench = f'''`timescale 1ns/1ps
module tb_{name};
  reg [3:0] a, b;
  reg cin;
  {decl}
  integer ia, ib, ic, k, expected, remainder, distance, fill, overflow, count;
  alu_{name} dut({ports});
  initial begin
    $dumpfile("build/{name}.vcd");
    $dumpvars(0, dut);
    count=0;
    for (ia=0; ia<16; ia=ia+1)
      for (ib=0; ib<{1 if name == 'not' else 16}; ib=ib+1)
        for (ic=0; ic<{2 if arith else 1}; ic=ic+1) begin
          a=ia; b=ib; cin=ic; #10;
          {expected}
          count=count+1;
        end
    $display("PASS {name}: %0d cases",count);
    $finish;
  end
endmodule
'''
    (TB / f'tb_{name}.v').write_text(bench)
