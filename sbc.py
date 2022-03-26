#!/usr/bin/env python
"""
Springboard compiler

:author: Athanasios Anastasiou
:date: Mar 2022

"""
import os
import pyparsing
import click
import urllib

class SpringboardError(Exception):
    pass


class SymbolRedefined(SpringboardError):
    pass


class SymbolUndefined(SpringboardError):
    pass


class CircularDependency(SpringboardError):
    pass


class CircularDefinition(SpringboardError):
    pass


class SpringboardProgram:
    def __init__(self):
        self._parser = self.get_parser()
        self._symbol_defs = {"+": "+", "-": "-",
                             ">": ">", "<": "<",
                             "[": "[", "]": "]",
                             ",": ",", ".": "."}
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
        Initialises a Springboard program given a string.

        :param a_program: A string that conforms to Springboard's grammar
        :type a_program: str
        :param previous_imports: A list of all imports in the main namespace to avoid circular references.
        :type previous_imports: list

        :returns: A Springboard program initialised with all its three sections.
        :rtype: SpringboardProgram

        :raises CircularDependency: If a file being imported imports a file that refers to the file being imported.
        :raises SymbolRedefined: Self explanatory.
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
        Initialises a Springboard program given a file name.

        :param a_file: The filename of a text file that contains Springboard code.
        :type a_file: str
        :param previous_imports: See `Springboard.from_string`
        :type previous_imports: list

        :returns: A SpringboardProgram object with all its three sections populated.
        :rtype: SpringboardProgram
        """
        p_imports = previous_imports + []
        with open(a_file, "rt") as fd:
            data = fd.read()
        return self.from_string(data, p_imports)

    def compile(self, a_program=None, symbols_compiled=[]):
        """
        Compiles a Springboard program to brainfuck.

        :param a_program: A string containing Springboard code.
        :type a_program: str
        :param symbols_compiled: The set of symbols whose definition requires compilation of a given symbol.
        :type symbols_compiled: list[str]

        :returns: A string that contains purely brainfuck code (i.e. composed entirely of the brainfuck grammar's symbols).
        :rtype: str

        :raises CircularDefinition: If a symbol being defined requires the compilation of a symbol being defined.
        :raises SymbolUndefined: If a symbol being defined refers to a symbol that is not defined anywhere.
        """
        source_code = a_program
        if a_program is None:
            source_code = list(self.code)
        compiled_code = ""
        # While there are symbols, keep substituting them
        for a_symbol in source_code:
            if a_symbol in symbols_compiled:
                raise CircularDefinition(f"Circular definition involving {a_symbol} and {','.join(symbols_compiled)}.")
            if a_symbol not in self._symbol_defs:
                raise SymbolUndefined(f"Symbol {a_symbol} is undefined.")
            symbol_code = self._symbol_defs[a_symbol]
            if type(symbol_code) is not str:
                self.symbol_defs[a_symbol] = "".join(self.compile(symbol_code, symbols_compiled + [a_symbol]))
            compiled_code = compiled_code + self.symbol_defs[a_symbol]
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
@click.option("-b", "--base-url", 
              type=click.STRING, 
              default="https://aanastasiou.github.io/brainfuck-visualizer/?bf=",
              help="Sets the base URL towards a try-it-online service.")
@click.option("--url/--no-url", 
              default=False,
              help="If set, returns the program encoded in URL form, ready to "
                   "be included in a link")
def sbc(input_file, output_file, base_url, url):
    """
    Springboard compiler.

    The springboard compiler accepts two arguments:\n 
    - input_file\n
    - output_file\n

    Both can be stdin/stdout, by using "-".

    Two options are provided to control posting to a try-it-online URL:\n
    - --base-url\n
    - --url
    
    Examples:\n
       - echo "+>+[-<+>]"|./sbc.py - -\n
       - echo "+>+[-<+>]"|./sbc.py - - --url

    The default base URL is: https://aanastasiou.github.io/brainfuck-visualizer/?bf=
    """
    try:
        # Generate unoptimised code (contains successive <> or +-)
        code = ''.join(SpringboardProgram().from_string(input_file.read()).compile())
        # TODO: HIGH, Sort the parse actions in the following rules
        r1 = pyparsing.Regex("[<>][<>]+").set_parse_action(lambda s, l, t: (">" if str(t).count(">") > str(t).count("<") else "<") * abs(str(t).count(">") - str(t).count("<")))
        r2 = pyparsing.Regex("[\+\-][\+\-]+").set_parse_action(lambda s, l, t: ("+" if str(t).count("+") > str(t).count("-") else "-") * abs(str(t).count("+") - str(t).count("-")))
        # Optimise the code by simplifying continuous segments of <> or +- characters
        optimised_code = r2.transform_string(r1.transform_string(code))
        if url:
            optimised_code = f"{base_url}{urllib.parse.quote(optimised_code)}"
        output_file.write(f"{optimised_code}\n")
    except SpringboardError as e:
        click.echo(f"{e}")


if __name__ == "__main__":
    sbc()
