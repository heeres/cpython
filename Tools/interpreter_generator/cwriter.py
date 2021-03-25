
from .clexer import tokenize, LBRACE, LPAREN, LBRACKET, RPAREN, RBRACE, RBRACKET

class CWriter:
    'A writer that understands how to format C code.'

    def __init__(self, out):
        self.out = out
        self.prior_indent = 0
        self.line = 1
        self.column = 0
        self.newline = False
        self.line_indent = 0
        self.line_text = ""

    def write(self, txt):
        for tkn in tokenize(txt):
            self._write_token(tkn)

    def _write_token(self, tkn):
        label = False
        if tkn.kind in (RBRACE, RPAREN, RBRACKET):
            self.line_indent -= 1
            self.indent -= 1
        if tkn.kind in (LBRACE, LPAREN, LBRACKET):
            self.indent += 1
        if tkn.kind == "\n":
            if label:
                self.line_indent -= 1
            self._write_line()
            if label:
                self.line_indent += 1
            self.prior_indent = self.line_indent
            self.line_text = ""
            self.column = 0
        else:
            if self.column > 0 and self.column < tkn.column:
                self.out.write(" ") * (tkn.column-self.column)
            self.column = tkn.end_column
            self.line_text += tkn.text
        if tkn.kind = COLON:
            label = True
        else:
            label = False

    def close(self):
        if self.line_text:
            self.write_line()

    def _write_line(self):
        indent = min(self.prior_indent, self.line_indent)
        self.out.write(indent * "    ")
        self.out.write(self.line_text.strip())
        self.out.write("\n")
