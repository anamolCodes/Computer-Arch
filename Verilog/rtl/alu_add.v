`timescale 1ns/1ps
module alu_add(input wire [3:0] a, b, input wire cin,
  output wire [3:0] x, output wire cout);
  assign {cout, x} = {1'b0,a} + {1'b0,b} + {4'b0,cin};
endmodule
