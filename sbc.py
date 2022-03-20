#!/usr/bin/env python
"""
Springboard compiler

:author: Athanasios Anastasiou
:date: Mar 2022

"""
import os
import pyparsing
import click


class SpringboardError(Exception):
    pass


class SymbolRedefined(SpringboardError):
    pass


class SymbolUndefined(SpringboardError):
    pass

class CircularDependency(SpringboardError):
    pass


class SpringboardProgram:
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

    def from_string(self, a_program, previous_imports=[]):
        """
        Compiles a Springboard program given a string.

        :param a_program: A string that conforms to Springboard's grammar
        :type a_program: str
        :param previous_imports: A list of all imports in the main namespace to avoid circular references.
        :type previous_imports: list

        :returns: A string that contains purely brainfuck code (i.e. composed entirely of the brainfuck grammar's symbols).
        :rtype: str
        """
        self._code_info = self._parser.parseString(a_program)
        # If there are imports, prepopulate the symbol definition table
        cwd = os.getcwd()
        p_imports=previous_imports + []
        for an_import in self.imports:
            # Break on circular references
            if an_import not in p_imports:
                p_imports.append(an_import)
            else:
                raise CircularDependency(f"Circular dependency involving {an_import} and {','.join(previous_imports)}.")
            # Change the current working directoy to enable relative imports
            import_path, import_file = os.path.split(an_import)
            if len(import_path) > 0:
                os.chdir(import_path)
            u = SpringboardProgram().from_file(import_file, p_imports)
            os.chdir(cwd)
            self._symbol_defs.update(u.symbol_defs)

        # Append the locally defined symbols
        for a_symbol_def in self._code_info[0]["symbol_defs"]:
            if a_symbol_def["symbol"] not in self._symbol_defs:
                self._symbol_defs[a_symbol_def["symbol"]] = a_symbol_def["code"]
            else:
                raise SymbolRedefined(f"Attempt to redefine symbol {a_symbol_def['symbol']}, from {self._symbol_defs[a_symbol_def['symbol']]} to {a_symbol_def['code']}.")
        return self

    def from_file(self, a_file, previous_imports=[]):
        """
        Compiles a Springboard program given a file.

        :param a_file: The filename of a text file that contains Springboard code.
        :type a_file: str
        :param previous_imports: See `Springboard.from_string`
        :type previous_imports: list

        :returns: A string that contains purely brainfuck code (i.e. composed entirely of the brainfuck grammar's symbols).
        :rtype: str
        """
        p_imports = previous_imports + []
        with open(a_file, "rt") as fd:
            data = fd.read()
        return self.from_string(data, p_imports)

    def compile(self, a_program=None):
        """
        Compiles a Springboard program to brainfuck.

        :param a_program: A string containing Springboard code.
        :type a_program: str

        :returns: A string that contains purely brainfuck code.
        :rtype: str
        """
        bf_code = "+-.,<>[]"
        source_code = a_program
        if a_program is None:
            source_code = list(self.code)
        compiled_code = []
        # While there are symbols, keep substituting them
        for a_symbol in source_code:
            if a_symbol not in bf_code:
                try:
                    compiled_code.extend(self.compile(self.symbol_defs[a_symbol]))
                except KeyError:
                    raise SymbolUndefined(f"Symbol {a_symbol} is undefined.")
            else:
                compiled_code.append(a_symbol)

        return compiled_code


    @staticmethod
    def get_parser():
        """
        Parses Springboard's grammar.

        springboard_program := imports_section defs_section code_section
        imports_section := import_statement*
        import_statement := import \".*?\"
        defs_section := def_statement*
        def_statement := : symbol_identifier code_section ;
        symbol_identifier := [a-zA-Z0-9_]+
        code_section := (basic_code_block | loop_code_block)*
        basic_code_block := "<"|">"|"+"|"-"|"."|","
        loop_code_block := basic_code_block | ("[" (basic_code_block | loop_code_block)* "]")
        """
        symbol_id = pyparsing.Regex("[a-zA-Z0-9_]+")
        basic_code_block = pyparsing.OneOrMore(pyparsing.Regex("[+\-\.,<>]") ^ symbol_id)
        loop_code_block = pyparsing.Forward()
        loop_code_block << (basic_code_block ^ ("[" + pyparsing.ZeroOrMore(basic_code_block ^ loop_code_block) + "]"))
        code_section = pyparsing.ZeroOrMore(basic_code_block ^ loop_code_block)
        def_statement = pyparsing.Group(pyparsing.Suppress(":") + symbol_id("symbol") + code_section("code") + pyparsing.Suppress(";"))
        defs_section = pyparsing.ZeroOrMore(def_statement)
        import_statement = pyparsing.Suppress("import") + pyparsing.QuotedString("\"")
        imports_section = pyparsing.ZeroOrMore(import_statement)
        sb_program = pyparsing.Group(imports_section("imports") + defs_section("symbol_defs") + code_section("code"))
        sb_program.ignore(pyparsing.Literal("#") + pyparsing.rest_of_line())
        return sb_program
        

@click.command()
@click.argument("input_file", type=click.File(mode="r"))
@click.argument("output_file", type=click.File(mode="w"))
def sbc(input_file, output_file):
    """
    Springboard compiler.
    """
    try:
        output_file.write(f"{''.join(SpringboardProgram().from_string(input_file.read()).compile())}\n")
    except SpringboardError as e:
        click.echo(f"{e}")


if __name__ == "__main__":
    sbc()
