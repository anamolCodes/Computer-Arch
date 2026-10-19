`timescale 1ns/1ps
module tb_mul;
  reg [3:0] a, b;
  reg cin;
  wire [3:0] x; wire [3:0] y;
  integer ia, ib, ic, k, expected, remainder, distance, fill, overflow, count;
  alu_mul dut(.a(a), .b(b), .x(x), .y(y));
  initial begin
    $dumpfile("build/mul.vcd");
    $dumpvars(0, dut);
    count=0;
    for (ia=0; ia<16; ia=ia+1)
      for (ib=0; ib<16; ib=ib+1)
        for (ic=0; ic<1; ic=ic+1) begin
          a=ia; b=ib; cin=ic; #10;
          expected = 0;
          for(k=0;k<ib;k=k+1) expected = expected + ia;
          if ({y,x} !== expected[7:0]) $fatal(1,"mul a=%d b=%d",ia,ib);
          count=count+1;
        end
    $display("PASS mul: %0d cases",count);
    $finish;
  end
endmodule
