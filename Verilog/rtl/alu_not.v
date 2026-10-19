`timescale 1ns/1ps
module alu_not(input wire [3:0] a, output wire [3:0] x);
  assign x = ~a;
endmodule
