
import sys
import argparse
from .clexer import to_text
from .parse_instructions import parse_file, Instruction
from .cwriter import CWriter
from collections import defaultdict
from jinja2 import Template, Environment, FileSystemLoader

HEADER = """
/********************************************************

    This code is automatically generated. Do not edit.

********************************************************/

"""

class NoDispatch:

    def dispatch(self):
        return "}"

class NoInstrumentation:

    def opcode_start(self, instruction):
        return ""

    def opcode_end(self, instruction):
        return ""

def main():
    parser = argparse.ArgumentParser(
        description='generate the interpreter function')
    parser.add_argument("--output", "-o", metavar="output",
        help='file to write interpreter to', default=sys.stdout, type=argparse.FileType('w'))
    parser.add_argument("instructions", metavar="instructions", nargs='+',
        help ="instruction description file(s)", type=argparse.FileType('r'))
    parser.add_argument("template", metavar="template",
        help ="template file")

    args = parser.parse_args()
    file_loader = FileSystemLoader(".")
    env = Environment(loader=file_loader, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template(args.template)
    insts = {}
    for fd in args.instructions:
        parse_file(fd.read(), insts, fd.name)
        fd.close()
    out = CWriter(args.output)
    out.write(HEADER)
    out.write(
        template.render(
            instructions=list(insts.values()),
            instrument = NoInstrumentation(),
            dispatch=NoDispatch(),
            to_text=to_text,
        )
    )
    args.output.close()

if __name__ == "__main__":
    main()
