

import sys
import argparse
from .clexer import tokenize, MACRO
from .cwriter import CWriter

class Instruction:

    def __init__(self, name, body):
        self.name = name
        self.body = body

    def __str__(self):
        return "Instruction: " + self.name + "\n" + to_text(self.body)

def extract_code(src):
    instructions = []
    tkn_iter = tokenize(src)
    for tkn in tkn_iter:
        if tkn.kind == MACRO:
            if tkn.text == "#define":
                next(tkn_iter)
            continue
        if tkn.text == "TARGET":
            inst = extract_instruction(tkn_iter)
            instructions.append(inst)
    return instructions

def extract_instruction(tkn_iter):
    body = []
    braces = 0
    lp, name, pr, colon = (next(tkn_iter) for _ in range(4))
    for tkn in tkn_iter:
        if tkn.text == "{":
            braces += 1
        if tkn.text == "}":
            braces -= 1
        body.append(tkn)
        if not braces:
            break
    return Instruction(name.text, body)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Extract instructions from ceval.c')
    parser.add_argument("input", metavar="input",
        help ="ceval.c or equivalent", type=argparse.FileType('r'))
    parser.add_argument("--output", "-o", metavar="output",
        help='file to write instructions to', default=sys.stdout, type=argparse.FileType('w'))
    args = parser.parse_args()
    src = args.input.read()
    out = CWriter(args.output)
    insts = extract_code(src)
    for inst in insts:
        if inst.name == "EXTENDED_ARG":
            continue
        out.write(inst.name + " ")
        out.write_tokens(inst.body)
        out.write("\n\n")
    if out is not sys.stdout:
        out.close()

