`timescale 1ns/1ps
module tb_or;
  reg [3:0] a, b;
  reg cin;
  wire [3:0] x;
  integer ia, ib, ic, k, expected, remainder, distance, fill, overflow, count;
  alu_or dut(.a(a), .b(b), .x(x));
  initial begin
    $dumpfile("build/or.vcd");
    $dumpvars(0, dut);
    count=0;
    for (ia=0; ia<16; ia=ia+1)
      for (ib=0; ib<16; ib=ib+1)
        for (ic=0; ic<1; ic=ic+1) begin
          a=ia; b=ib; cin=ic; #10;
          expected = 0;
          for (k=0; k<4; k=k+1)
            expected = expected | (((14 >> (2*((ia>>k)&1)+((ib>>k)&1))) & 1) << k);
          if (x !== expected[3:0]) $fatal(1,"or a=%d b=%d",ia,ib);
          count=count+1;
        end
    $display("PASS or: %0d cases",count);
    $finish;
  end
endmodule
