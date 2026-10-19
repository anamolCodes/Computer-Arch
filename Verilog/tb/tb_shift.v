`timescale 1ns/1ps
module tb_shift;
  reg [3:0] a, b;
  reg cin;
  wire [3:0] x; wire [3:0] y;
  integer ia, ib, ic, k, expected, remainder, distance, fill, overflow, count;
  alu_shift dut(.a(a), .b(b), .x(x), .y(y));
  initial begin
    $dumpfile("build/shift.vcd");
    $dumpvars(0, dut);
    count=0;
    for (ia=0; ia<16; ia=ia+1)
      for (ib=0; ib<16; ib=ib+1)
        for (ic=0; ic<1; ic=ic+1) begin
          a=ia; b=ib; cin=ic; #10;
          distance=(ib>>1)&3; fill=ib&1;
          if (ib < 8) begin
            expected=((ia*(1<<distance)) + fill*((1<<distance)-1)) & 15;
            overflow=ia>>(4-distance);
          end else begin
            expected=(ia>>distance) + fill*(16-(1<<(4-distance)));
            overflow=(ia & ((1<<distance)-1)) << (4-distance);
          end
          if (x !== expected[3:0] || y !== overflow[3:0])
            $fatal(1,"shift a=%b b=%b x=%b y=%b",a,b,x,y);
          count=count+1;
        end
    $display("PASS shift: %0d cases",count);
    $finish;
  end
endmodule
