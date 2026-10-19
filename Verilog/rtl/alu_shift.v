`timescale 1ns/1ps
// b[3]: direction, b[2:1]: distance, b[0]: fill.
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
