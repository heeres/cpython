from .clexer import tokenize, to_text, COMMENT, IDENTIFIER, MACRO

class Instruction:
    
    def __init__(self, name, body):
        self.name = name
        self.body = body

def parse_file(src, instructions, filename):
    tkn_iter = tokenize(src)
    prefix = []
    suffix = []
    current = prefix
    try:
        while True:
            parse_instruction(tkn_iter, instructions, filename)
    except StopIteration:
        pass

def syntax_error(msg, tkn, filename):
    raise SyntaxError(f"{msg} at line {tkn.end[0]} in {filename}")

def parse_error(expecting, tkn, filename):
    syntax_error(
        f"Expecting {expecting}, found {tkn.text}", tkn, filename
    )

def parse_instruction(tkn_iter, instructions, filename):
    tkn = next(tkn_iter)
    # Discard any leading comments or macros
    while tkn.kind == COMMENT or tkn.kind == MACRO or tkn.kind == "\n":
        tkn = next(tkn_iter)
    #Expect either NAME or TARGET(NAME)
    if tkn.kind != IDENTIFIER:
        parse_error("an identifier", tkn, filename)
    name = tkn.text
    brace = next(tkn_iter)
    body = parse_body(tkn_iter, filename)
    tkn = next(tkn_iter)
    instructions[name] = Instruction(name, body)

def parse_body(tkn_iter, filename):
    body = []
    braces = 1
    for tkn in tkn_iter:
        if tkn.text == "{":
            braces += 1
        elif tkn.text == "}":
            braces -= 1
            if not braces:
                break
        body.append(tkn)
    else:
        parse_error('}', tkn, filename)
    return body
