import pyparsing

class BrainStackProgram:
    def __init__(self):
        self._parser = self.get_parser()
        self._symbol_defs = {}
        self._code_info = None

    @property
    def imports(self):
        return self._code_info[0]["imports"]

    @property
    def symbol_defs(self):
        return self._symbol_defs

    @property
    def code(self):
        return self._code_info[0]["code"]

    def from_string(self, a_program):
        self._code_info = self._parser.parseString(a_program)
        # If there are imports, prepopulate the symbol definition table
        for an_import in self.imports:
            u = BrainStackProgram().from_file(an_import)
            self._symbol_defs.update(u.symbol_defs)
        # Append the locally defined symbols
        for a_symbol_def in self._code_info[0]["symbol_defs"]:
            self._symbol_defs[a_symbol_def["symbol"]] = a_symbol_def["code"]
        return self


    def from_file(self, a_file):
        with open(a_file, "rt") as fd:
            data = fd.read()
        return self.from_string(data)

    def compile(self, a_program=None):
        bf_code = "+-.,<>[]"
        source_code = a_program
        if a_program is None:
            source_code = list(self.code)
        compiled_code = []
        # While there are symbols, keep substituting them
        for a_symbol in source_code:
            if a_symbol not in bf_code:
                compiled_code.extend(self.compile(self.symbol_defs[a_symbol]))
            else:
                compiled_code.append(a_symbol)

        return compiled_code


    @staticmethod
    def get_parser():
        symbol_id = pyparsing.Regex("[a-zA-Z0-9_]+")
        basic_code_block = pyparsing.OneOrMore(pyparsing.Regex("[+\-\.,<>\[\]]") ^ symbol_id)
        # code_block = pyparsing.Forward()
        # code_block << (basic_code_block ^ (pyparsing.Literal("[") + code_block + pyparsing.Literal("]")))
        #code_section = pyparsing.ZeroOrMore(code_block)
        code_section = pyparsing.ZeroOrMore(basic_code_block)
        def_statement = pyparsing.Group(pyparsing.Suppress(":") + symbol_id("symbol") + code_section("code") + pyparsing.Suppress(";"))
        defs_section = pyparsing.ZeroOrMore(def_statement)
        import_statement = pyparsing.Suppress("import") + pyparsing.QuotedString("\"")
        imports_section = pyparsing.ZeroOrMore(import_statement)
        bf_program = pyparsing.Group(imports_section("imports") + defs_section("symbol_defs") + code_section("code"))
        return bf_program

if __name__ == "__main__":
    u = BrainStackProgram().from_string("import \"stdio.bs\"\n 2 push 3 push 4 push add mul ,\n")
    print("".join(u.compile()))
