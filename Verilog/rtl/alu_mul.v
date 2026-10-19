`timescale 1ns/1ps
module alu_mul(input wire [3:0] a, b,
  output wire [3:0] x, y);
  wire [7:0] product;
  assign product = {4'b0,a} * {4'b0,b};
  assign {y,x} = product;
endmodule
