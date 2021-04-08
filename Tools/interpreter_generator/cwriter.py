
from .clexer import tokenize, LBRACE, LPAREN, LBRACKET, RPAREN, RBRACE, RBRACKET, COLON

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
        self.label = False

    def write(self, txt):
        for tkn in tokenize(txt):
            self._write_token(tkn)

    def _write_token(self, tkn):
        self.label = False
        if tkn.kind in (RBRACE, RPAREN, RBRACKET):
            self.line_indent -= 1
        if tkn.kind in (LBRACE, LPAREN, LBRACKET):
            self.line_indent += 1
        if tkn.kind == "\n":
            self._write_line()
            self.prior_indent = self.line_indent
            self.line_text = ""
            self.column = 0
        else:
            if self.column > 0 and self.column < tkn.column:
                self.line_text += " " * (tkn.column-self.column)
            self.column = tkn.end_column
            self.line_text += tkn.text
        self.label = tkn.kind == COLON

    def write_tokens(self, tkns):
        for tkn in tkns:
            self._write_token(tkn)

    def close(self):
        if self.line_text:
            self.write_line()

    def _write_line(self):
        indent = min(self.prior_indent, self.line_indent)-self.label
        self.line_text = self.line_text.strip()
        if self.line_text and self.line_text[0] != "#":
            self.out.write(indent * "    ")
        self.out.write(self.line_text)
        self.out.write("\n")
