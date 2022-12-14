#!/usr/bin/env python3

import sys
import os


labels = {}
# For setting label addresses
PC     = 0
# For error messages
lineNo = 0



def encode_hex(arg, width):
  """Encode a hexadecimal literal argument"""
  return format(int(arg, 16), "0{}b".format(width))



def encode_bin(arg, width):
  """Encode a binary literal argument"""
  return format(int(arg, 2), "0{}b".format(width))



def encode_dec(arg, width):
  """Encode a decimal literal argument"""
  return format(int(arg), "0{}b".format(width))



def encode_reg(arg):
  """Encode a named register argument"""
  return format(ord(arg) - ord("A"), "04b")



def encode_label(arg, width, direct):
  """Encode a named jump label as a program counter address"""
  global PC, labels
  if direct:
    offset = labels[arg]
  else:
    if PC > labels[arg]:
      raise Exception("Negative relative jumps are not supported by the hardware")
    offset = labels[arg] - PC
  # TODO: Fix jump calculation for negative jumps
  if offset < 0:
    offset += 15
  return format(offset, "0{}b".format(width))



def encode_arg(opcode, arg):
  """Encode an opcode argument with the correct width depending on opcode"""
  WIDTH = {
    "ADI": 4,
    "CMPJ": 4
  }
  if opcode in WIDTH:
    width = WIDTH[opcode]
  else:
    width = 8
  if arg.startswith("0x"):
    return encode_hex(arg, width)
  elif arg.startswith("0b"):
    return encode_bin(arg, width)
  elif arg.isnumeric(): 
    return encode_dec(arg, width)
  elif arg.upper() in "ABCDEFGHIJKLMNOP":
    return encode_reg(arg.upper())
  else:
    return encode_label(arg, width, (opcode == "JMP"))



def encode(opcode, argv, argc):
  """Encode an opcode and its arguments as machine code"""
  OPCODES = {
    "LDI": "0001",
    "ADD": "0010",
    "ADI": "0011",
    "SUB": "0100",
    "MUL": "0101",
    "DIV": "0110",
    "INC": "0111",
    "DEC": "1000",
    "OR":  "1001",
    "AND": "1010",
    "XOR": "1011",
    "COMP":"1100",
    "JMP": "1101",
    "CMPJ":"1110",
    "NOP": "1111",
    "HALT":"0000"
  }
  if len(argv) != argc:
    raise Exception(
      "Wrong number of operands to opcode {} (got {}, expected {})"
      .format(opcode, len(argv), argc)
    )
  mach = OPCODES[opcode]
  if opcode == "INC" or opcode == "DEC":
    mach += encode_arg(opcode, argv[0])
    mach += "0000"
    mach += encode_arg(opcode, argv[1])
  else:
    for arg in argv:
      mach += encode_arg(opcode, arg)

  if len(mach) < 16:
    mach += "0"*(16-len(mach))

  return mach + ";"



def assemble_op(parts):
  """Validate and translate an opcode and its arguments"""
  opcode = parts[0].upper()
  ARGC = {
    "LDI": 2,
    "ADD": 3,
    "ADI": 3,
    "SUB": 3,
    "MUL": 3,
    "DIV": 3,
    "INC": 2,
    "DEC": 2,
    "OR":  3,
    "AND": 3,
    "XOR": 3,
    "COMP":2,
    "JMP": 1,
    "CMPJ":3,
    "NOP": 0,
    "HALT":0
  }
  parts = parts[1:]
  return encode(opcode, parts, ARGC[opcode])



def add_label(label):
  """Record a label with its program counter address"""
  global labels, PC

  if len(label) < 2:
    raise Exception(
      "Label '{}' must be at least 2 characters long".format(label))
    
  if label in labels:
    raise Exception("Duplicate label '{}'".format(label))

  labels[label] = PC
  print("  {}: PC = {}".format(label, PC))
  


def assemble(width, depth, inFile, outFile):
  """Assemble the contents of inFile, writing machine code to outFile"""
  global lineNo, PC, labels

  outAddr = 0

  emit_header(outFile, width, depth)

  longestLine = 0

  for passNo in range(2):
    if passNo == 0:
      print("Labels:")
    else:
      print("\nInstructions:")

    inFile.seek(0)
    PC = 0
    lineNo = 0
    for line in inFile:
      lineNo += 1

      commentIndex = line.find(";")
      if (commentIndex > -1):
        line = line[0:commentIndex]

      line = line.strip()
      if not line:
        continue

      if len(line) > longestLine:
        longestLine = len(line)

      try:
        if line.endswith(":"):
          if passNo == 0:
            add_label(line[:-1]) 
        else:
          if passNo == 1:
            parts = line.split()
            mach = assemble_op(parts)  
            print("  {} {}".format(line.ljust(longestLine+5), mach))
            outFile.write("  {} : {}\n".format(outAddr, mach))
            outAddr += 1
          PC += 1
      except Exception as ex:
        print("! {} (line {}: {})".format(ex, lineNo, line))
        #raise(ex)
        return

  outFile.write("  [{}..{}] : 0000000000000000;\n".format(outAddr, depth-1))
  outFile.write("END;")

  print("\nRead {} lines".format(lineNo))



def main():
  print("Lab4ASM - by Matthew Murphy, for EEE333 wth Seth Abraham");

  inFilename = sys.argv[1] if (len(sys.argv) > 1) else "lab4.asm"

  if len(sys.argv) > 2:
    outFilename = sys.argv[2]
  else:
    outFilename = os.path.splitext(inFilename)[0] + ".mif"

  print("  Input:\t" + inFilename);
  print("  Output:\t" + outFilename);
  print("")

  try:
    inFile = open(inFilename, "r")
  except IOError:
    print("! Input file doesn't exist")
    return -1

  outFile = open(outFilename, "w")

  assemble(16, 256, inFile, outFile)

  inFile.close()
  outFile.close()



def emit_header(file, width, depth):
  """Machine code file prelude"""
  file.write("""-- Intel Memory Initialization File

-- Generated by Lab4ASM by Matthew Murphy
-- for EEE 333 with Seth Abraham

WIDTH={};
DEPTH={};

ADDRESS_RADIX=UNS;
DATA_RADIX=BIN;

CONTENT BEGIN
""".format(width, depth))


if __name__ == "__main__":
  main()