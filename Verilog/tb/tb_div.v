`timescale 1ns/1ps
module tb_div;
  reg [3:0] a, b;
  reg cin;
  wire [3:0] x; wire [3:0] y; wire divide_by_zero;
  integer ia, ib, ic, k, expected, remainder, distance, fill, overflow, count;
  alu_div dut(.a(a), .b(b), .x(x), .y(y), .divide_by_zero(divide_by_zero));
  initial begin
    $dumpfile("build/div.vcd");
    $dumpvars(0, dut);
    count=0;
    for (ia=0; ia<16; ia=ia+1)
      for (ib=0; ib<16; ib=ib+1)
        for (ic=0; ic<1; ic=ic+1) begin
          a=ia; b=ib; cin=ic; #10;
          if (ib == 0) begin
            if (divide_by_zero !== 1'b1 || x !== 4'hf || y !== a)
              $fatal(1,"divide by zero a=%d",ia);
          end else begin
            expected=0; remainder=ia;
            while (remainder >= ib) begin
              remainder=remainder-ib; expected=expected+1;
            end
            if (divide_by_zero !== 1'b0 || x !== expected[3:0] || y !== remainder[3:0])
              $fatal(1,"div a=%d b=%d",ia,ib);
          end
          count=count+1;
        end
    $display("PASS div: %0d cases",count);
    $finish;
  end
endmodule
