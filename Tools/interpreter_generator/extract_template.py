

import sys
import argparse
from .clexer import tokenize, IDENTIFIER, CASE
from .cwriter import CWriter
from .extract_instructions import extract_instruction

PREAMBLE = """
/* Exverything in this section is ignored by the interpreter generator
 * Use it to add #includes, etc to help IDEs */

#include "Python.h"
#include "pycore_abstract.h"
#include "pycore_call.h"
#include "pycore_ceval.h"
#include "frameobject.h"
#include "pycore_code.h"

/* END_IGNORE */


"""

INSTRUCTION_LOOP = """
    {% for instruction in instructions %}
        case TARGET({{ instruction.name }}):
        { {{ instrument.opcode_start(instruction) }}
        {{ to_text(instruction.body) }}
        {{ instrument.opcode_end(instruction) }} {{ dispatch.dispatch() }}

    {% endfor %}
"""

def extract_template(src):
    template = []
    tkn_iter = tokenize(src)
    for tkn in tkn_iter:
        if tkn.kind == IDENTIFIER and tkn.text == "_PyEval_EvalFrameDefault":
            break
    else:
        sys.exit("No _PyEval_EvalFrameDefault found")
    args = extract_bracketted(tkn_iter, "(", ")")
    nl = next(tkn_iter)
    assert nl.text == "\n"
    body = extract_bracketted(tkn_iter, "{", "}")
    return args + body

def extract_bracketted(tkn_iter, left, right):
    body = []
    brackets = 0
    for tkn in tkn_iter:
        if tkn.text == left:
            brackets += 1
        if tkn.text == right:
            brackets -= 1
        body.append(tkn)
        if not brackets:
            break
    return body

def remove_instructions(tkns):
    instruction_seen = False
    tkn_iter = iter(tkns)
    for tkn in tkn_iter:
        if tkn.kind == CASE:
            case = tkn
            tkn = next(tkn_iter)
            if tkn.text == "TARGET":
                extract_instruction(tkn_iter)
                next(tkn_iter)
                next(tkn_iter)
                if not instruction_seen:
                    yield from tokenize(INSTRUCTION_LOOP)
                    instruction_seen = True
                continue
            else:
                yield case
        yield tkn

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Extract template base from ceval.c')
    parser.add_argument("input", metavar="input",
        help ="ceval.c or equivalent", type=argparse.FileType('r'))
    parser.add_argument("--output", "-o", metavar="output",
        help='file to write instructions to', default=sys.stdout, type=argparse.FileType('w'))
    args = parser.parse_args()
    src = args.input.read()
    out = CWriter(args.output)
    tmpl = remove_instructions(extract_template(src))
    out.write(PREAMBLE)
    out.write("PyObject* _Py_HOT_FUNCTION\n")
    out.write("_PyEval_EvalFrameDefault")
    out.write_tokens(tmpl)
    out.write("\n\n")
    if out is not sys.stdout:
        out.close()

