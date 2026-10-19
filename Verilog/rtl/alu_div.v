`timescale 1ns/1ps
// Unsigned division. Invalid divisor is explicit, never silently valid.
module alu_div(input wire [3:0] a, b,
  output wire [3:0] x, y, output wire divide_by_zero);
  assign divide_by_zero = (b == 0);
  assign x = divide_by_zero ? 4'hf : a / b;
  assign y = divide_by_zero ? a : a % b;
endmodule
