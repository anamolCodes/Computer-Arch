`timescale 1ns/1ps
module tb_add;
  reg [3:0] a, b;
  reg cin;
  wire [3:0] x; wire cout;
  integer ia, ib, ic, k, expected, remainder, distance, fill, overflow, count;
  alu_add dut(.a(a), .b(b), .x(x), .cin(cin), .cout(cout));
  initial begin
    $dumpfile("build/add.vcd");
    $dumpvars(0, dut);
    count=0;
    for (ia=0; ia<16; ia=ia+1)
      for (ib=0; ib<16; ib=ib+1)
        for (ic=0; ic<2; ic=ic+1) begin
          a=ia; b=ib; cin=ic; #10;
          expected = ia + ib + ic;
          if (x !== (expected & 15) || cout !== (expected >= 16))
            $fatal(1,"add a=%d b=%d cin=%d",ia,ib,ic);
          count=count+1;
        end
    $display("PASS add: %0d cases",count);
    $finish;
  end
endmodule
