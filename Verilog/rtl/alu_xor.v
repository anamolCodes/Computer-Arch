`timescale 1ns/1ps
module alu_xor(input wire [3:0] a, input wire [3:0] b, output wire [3:0] x);
  assign x = a ^ b;
endmodule
