#!/usr/bin/env python3
"""Jack Compiler - Tokenizer, Parser, and Code Generator"""

import os
import re
import sys
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple

# ==================== TOKENIZER ====================
class TokenType(Enum):
    KEYWORD = "KEYWORD"
    SYMBOL = "SYMBOL"
    IDENTIFIER = "IDENTIFIER"
    INT_CONST = "INT_CONST"
    STRING_CONST = "STRING_CONST"
    EOF = "EOF"

@dataclass
class Token:
    type: TokenType
    value: str
    line: int = 0

class Tokenizer:
    KEYWORDS = {
        'class', 'constructor', 'function', 'method', 'field', 'static',
        'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null',
        'this', 'let', 'do', 'if', 'else', 'while', 'return'
    }
    SYMBOLS = set('{}()[].,;=+-*/<>&|~')

    def __init__(self, code: str):
        self.code = code
        self.pos = 0
        self.line = 1
        self.tokens: List[Token] = []

    def tokenize(self) -> List[Token]:
        while self.pos < len(self.code):
            self._skip_whitespace_and_comments()
            if self.pos >= len(self.code):
                break

            if self.code[self.pos] == '"':
                self._read_string()
            elif self.code[self.pos].isdigit():
                self._read_number()
            elif self.code[self.pos].isalpha() or self.code[self.pos] == '_':
                self._read_identifier()
            elif self.code[self.pos] in self.SYMBOLS:
                self.tokens.append(Token(TokenType.SYMBOL, self.code[self.pos], self.line))
                self.pos += 1
            else:
                self.pos += 1

        self.tokens.append(Token(TokenType.EOF, '', self.line))
        return self.tokens

    def _skip_whitespace_and_comments(self):
        while self.pos < len(self.code):
            if self.code[self.pos].isspace():
                if self.code[self.pos] == '\n':
                    self.line += 1
                self.pos += 1
            elif self.pos + 1 < len(self.code) and self.code[self.pos:self.pos+2] == '//':
                while self.pos < len(self.code) and self.code[self.pos] != '\n':
                    self.pos += 1
            elif self.pos + 1 < len(self.code) and self.code[self.pos:self.pos+2] == '/*':
                self.pos += 2
                while self.pos + 1 < len(self.code):
                    if self.code[self.pos:self.pos+2] == '*/':
                        self.pos += 2
                        break
                    if self.code[self.pos] == '\n':
                        self.line += 1
                    self.pos += 1
            else:
                break

    def _read_string(self):
        self.pos += 1
        start = self.pos
        while self.pos < len(self.code) and self.code[self.pos] != '"':
            self.pos += 1
        value = self.code[start:self.pos]
        self.tokens.append(Token(TokenType.STRING_CONST, value, self.line))
        self.pos += 1

    def _read_number(self):
        start = self.pos
        while self.pos < len(self.code) and self.code[self.pos].isdigit():
            self.pos += 1
        value = self.code[start:self.pos]
        self.tokens.append(Token(TokenType.INT_CONST, value, self.line))

    def _read_identifier(self):
        start = self.pos
        while self.pos < len(self.code) and (self.code[self.pos].isalnum() or self.code[self.pos] == '_'):
            self.pos += 1
        value = self.code[start:self.pos]
        if value in self.KEYWORDS:
            self.tokens.append(Token(TokenType.KEYWORD, value, self.line))
        else:
            self.tokens.append(Token(TokenType.IDENTIFIER, value, self.line))

# ==================== SYMBOL TABLE ====================
class SymbolKind(Enum):
    STATIC = "static"
    FIELD = "field"
    ARG = "arg"
    VAR = "var"

@dataclass
class Symbol:
    name: str
    type: str
    kind: SymbolKind
    index: int

class SymbolTable:
    def __init__(self):
        self.class_symbols: Dict[str, Symbol] = {}
        self.subroutine_symbols: Dict[str, Symbol] = {}
        self.static_count = 0
        self.field_count = 0
        self.arg_count = 0
        self.var_count = 0

    def start_subroutine(self):
        self.subroutine_symbols.clear()
        self.arg_count = 0
        self.var_count = 0

    def define(self, name: str, type: str, kind: SymbolKind):
        symbol = Symbol(name, type, kind, self._get_count(kind))
        if kind in [SymbolKind.STATIC, SymbolKind.FIELD]:
            self.class_symbols[name] = symbol
        else:
            self.subroutine_symbols[name] = symbol

    def _get_count(self, kind: SymbolKind) -> int:
        if kind == SymbolKind.STATIC:
            self.static_count += 1
            return self.static_count - 1
        elif kind == SymbolKind.FIELD:
            self.field_count += 1
            return self.field_count - 1
        elif kind == SymbolKind.ARG:
            self.arg_count += 1
            return self.arg_count - 1
        elif kind == SymbolKind.VAR:
            self.var_count += 1
            return self.var_count - 1

    def lookup(self, name: str) -> Optional[Symbol]:
        if name in self.subroutine_symbols:
            return self.subroutine_symbols[name]
        return self.class_symbols.get(name)

    def var_count(self, kind: SymbolKind) -> int:
        if kind == SymbolKind.VAR:
            return self.var_count
        elif kind == SymbolKind.ARG:
            return self.arg_count
        return 0

# ==================== CODE GENERATOR ====================
class CodeGenerator:
    def __init__(self, class_name: str):
        self.class_name = class_name
        self.output: List[str] = []
        self.label_counter = 0

    def write(self, cmd: str):
        self.output.append(cmd)

    def write_push(self, segment: str, index: int):
        self.write(f"push {segment} {index}")

    def write_pop(self, segment: str, index: int):
        self.write(f"pop {segment} {index}")

    def write_arithmetic(self, op: str):
        op_map = {'+': 'add', '-': 'sub', '*': 'call Math.multiply 2', '/': 'call Math.divide 2',
                  '&': 'and', '|': 'or', '<': 'lt', '>': 'gt', '=': 'eq', '~': 'not', '-neg': 'neg'}
        self.write(op_map.get(op, op))

    def write_call(self, name: str, nargs: int):
        self.write(f"call {name} {nargs}")

    def write_function(self, name: str, nlocals: int):
        self.write(f"function {name} {nlocals}")

    def write_return(self):
        self.write("return")

    def write_label(self, label: str):
        self.write(f"label {label}")

    def write_goto(self, label: str):
        self.write(f"goto {label}")

    def write_if(self, label: str):
        self.write(f"if-goto {label}")

    def get_unique_label(self, prefix: str = "LABEL") -> str:
        label = f"{prefix}_{self.label_counter}"
        self.label_counter += 1
        return label

    def get_code(self) -> str:
        return '\n'.join(self.output)

# ==================== PARSER ====================
class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = tokens[0] if tokens else Token(TokenType.EOF, '')
        self.symbol_table = SymbolTable()
        self.code_gen = None
        self.class_name = ""
        self.subroutine_name = ""

    def parse(self) -> str:
        self.compile_class()
        return self.code_gen.get_code()

    def advance(self):
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
            self.current_token = self.tokens[self.pos]

    def peek(self) -> Token:
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return Token(TokenType.EOF, '')

    def expect(self, *args) -> Token:
        # Can be called as expect(TokenType) or expect(TokenType, value) or expect(TokenType, TokenType, ...)
        if len(args) == 0:
            raise ValueError("expect() requires at least one argument")
        
        # Check if last arg is a string (value to match)
        types = []
        value = None
        
        for arg in args:
            if isinstance(arg, str):
                value = arg
            elif isinstance(arg, TokenType):
                types.append(arg)
        
        if not types:
            raise ValueError("expect() requires at least one TokenType")
        
        # Check if current token matches one of the types
        if self.current_token.type not in types:
            raise SyntaxError(f"Expected {types}, got {self.current_token.type}")
        
        # Check value if provided
        if value and self.current_token.value != value:
            raise SyntaxError(f"Expected '{value}', got '{self.current_token.value}'")
        
        token = self.current_token
        self.advance()
        return token

    def match(self, *values) -> bool:
        return self.current_token.value in values

    def compile_class(self):
        self.expect(TokenType.KEYWORD, 'class')
        self.class_name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.SYMBOL, '{')
        self.code_gen = CodeGenerator(self.class_name)

        while self.match('static', 'field'):
            self.compile_class_var_dec()

        while self.match('constructor', 'function', 'method'):
            self.compile_subroutine_dec()

        self.expect(TokenType.SYMBOL, '}')

    def compile_class_var_dec(self):
        kind = SymbolKind.STATIC if self.match('static') else SymbolKind.FIELD
        self.advance()
        # Type can be keyword (int, char, boolean) or identifier (class name)
        var_type = self.current_token.value
        self.advance()
        
        while True:
            var_name = self.expect(TokenType.IDENTIFIER).value
            self.symbol_table.define(var_name, var_type, kind)
            if not self.match(','):
                break
            self.advance()
        
        self.expect(TokenType.SYMBOL, ';')

    def compile_subroutine_dec(self):
        subroutine_type = self.current_token.value
        self.advance()
        return_type = self.current_token.value
        self.advance()
        self.subroutine_name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.SYMBOL, '(')
        
        self.symbol_table.start_subroutine()
        
        if subroutine_type == 'method':
            self.symbol_table.define('this', self.class_name, SymbolKind.ARG)
        
        self.compile_parameter_list()
        self.expect(TokenType.SYMBOL, ')')
        self.expect(TokenType.SYMBOL, '{')
        
        while self.match('var'):
            self.compile_var_dec()
        
        func_name = f"{self.class_name}.{self.subroutine_name}"
        nlocals = self.symbol_table.var_count.__self__.var_count if hasattr(self.symbol_table.var_count, '_self_') else 0
        # Count locals manually
        nlocals = sum(1 for s in self.symbol_table.subroutine_symbols.values() if s.kind == SymbolKind.VAR)
        
        self.code_gen.write_function(func_name, nlocals)
        
        if subroutine_type == 'method':
            self.code_gen.write_push('argument', 0)
            self.code_gen.write_pop('pointer', 0)
        elif subroutine_type == 'constructor':
            nfields = sum(1 for s in self.symbol_table.class_symbols.values() if s.kind == SymbolKind.FIELD)
            self.code_gen.write_push('constant', nfields)
            self.code_gen.write_call('Memory.alloc', 1)
            self.code_gen.write_pop('pointer', 0)
        
        self.compile_statements()
        self.expect(TokenType.SYMBOL, '}')

    def compile_parameter_list(self):
        if not self.match(')'):
            while True:
                param_type = self.current_token.value
                self.advance()
                param_name = self.expect(TokenType.IDENTIFIER).value
                self.symbol_table.define(param_name, param_type, SymbolKind.ARG)
                if not self.match(','):
                    break
                self.advance()

    def compile_var_dec(self):
        self.expect(TokenType.KEYWORD, 'var')
        var_type = self.current_token.value
        self.advance()
        
        while True:
            var_name = self.expect(TokenType.IDENTIFIER).value
            self.symbol_table.define(var_name, var_type, SymbolKind.VAR)
            if not self.match(','):
                break
            self.advance()
        
        self.expect(TokenType.SYMBOL, ';')

    def compile_statements(self):
        while self.match('let', 'if', 'while', 'do', 'return'):
            if self.match('let'):
                self.compile_let()
            elif self.match('if'):
                self.compile_if()
            elif self.match('while'):
                self.compile_while()
            elif self.match('do'):
                self.compile_do()
            elif self.match('return'):
                self.compile_return()

    def compile_let(self):
        self.expect(TokenType.KEYWORD, 'let')
        var_name = self.expect(TokenType.IDENTIFIER).value
        symbol = self.symbol_table.lookup(var_name)
        
        is_array = False
        if self.match('['):
            is_array = True
            self.advance()
            self.compile_expression()
            self.expect(TokenType.SYMBOL, ']')
            self.code_gen.write_push(self._segment_for(symbol.kind), symbol.index)
            self.code_gen.write_arithmetic('+')
        
        self.expect(TokenType.SYMBOL, '=')
        self.compile_expression()
        self.expect(TokenType.SYMBOL, ';')
        
        if is_array:
            self.code_gen.write_pop('temp', 0)
            self.code_gen.write_pop('pointer', 1)
            self.code_gen.write_push('temp', 0)
            self.code_gen.write_pop('that', 0)
        else:
            self.code_gen.write_pop(self._segment_for(symbol.kind), symbol.index)

    def compile_if(self):
        self.expect(TokenType.KEYWORD, 'if')
        self.expect(TokenType.SYMBOL, '(')
        self.compile_expression()
        self.expect(TokenType.SYMBOL, ')')
        
        label_false = self.code_gen.get_unique_label('IF_FALSE')
        label_end = self.code_gen.get_unique_label('IF_END')
        
        self.code_gen.write_arithmetic('~')
        self.code_gen.write_if(label_false)
        
        self.expect(TokenType.SYMBOL, '{')
        self.compile_statements()
        self.expect(TokenType.SYMBOL, '}')
        
        self.code_gen.write_goto(label_end)
        self.code_gen.write_label(label_false)
        
        if self.match('else'):
            self.advance()
            self.expect(TokenType.SYMBOL, '{')
            self.compile_statements()
            self.expect(TokenType.SYMBOL, '}')
        
        self.code_gen.write_label(label_end)

    def compile_while(self):
        self.expect(TokenType.KEYWORD, 'while')
        self.expect(TokenType.SYMBOL, '(')
        
        label_loop = self.code_gen.get_unique_label('WHILE_LOOP')
        label_end = self.code_gen.get_unique_label('WHILE_END')
        
        self.code_gen.write_label(label_loop)
        
        self.compile_expression()
        self.expect(TokenType.SYMBOL, ')')
        
        self.code_gen.write_arithmetic('~')
        self.code_gen.write_if(label_end)
        
        self.expect(TokenType.SYMBOL, '{')
        self.compile_statements()
        self.expect(TokenType.SYMBOL, '}')
        
        self.code_gen.write_goto(label_loop)
        self.code_gen.write_label(label_end)

    def compile_do(self):
        self.expect(TokenType.KEYWORD, 'do')
        self.compile_subroutine_call()
        self.code_gen.write_pop('temp', 0)
        self.expect(TokenType.SYMBOL, ';')

    def compile_return(self):
        self.expect(TokenType.KEYWORD, 'return')
        if not self.match(';'):
            self.compile_expression()
        else:
            self.code_gen.write_push('constant', 0)
        self.expect(TokenType.SYMBOL, ';')
        self.code_gen.write_return()

    def compile_expression(self):
        self.compile_term()
        while self.match('+', '-', '*', '/', '&', '|', '<', '>', '='):
            op = self.current_token.value
            self.advance()
            self.compile_term()
            self.code_gen.write_arithmetic(op)

    def compile_term(self):
        if self.current_token.type == TokenType.INT_CONST:
            self.code_gen.write_push('constant', int(self.current_token.value))
            self.advance()
        elif self.current_token.type == TokenType.STRING_CONST:
            string_val = self.current_token.value
            self.code_gen.write_push('constant', len(string_val))
            self.code_gen.write_call('String.new', 1)
            for char in string_val:
                self.code_gen.write_push('constant', ord(char))
                self.code_gen.write_call('String.appendChar', 2)
            self.advance()
        elif self.match('true', 'false', 'null', 'this'):
            keyword = self.current_token.value
            if keyword == 'true':
                self.code_gen.write_push('constant', 1)
                self.code_gen.write_arithmetic('~')
            elif keyword in ['false', 'null']:
                self.code_gen.write_push('constant', 0)
            elif keyword == 'this':
                self.code_gen.write_push('pointer', 0)
            self.advance()
        elif self.match('-', '~'):
            op = self.current_token.value
            self.advance()
            self.compile_term()
            self.code_gen.write_arithmetic('-neg' if op == '-' else '~')
        elif self.current_token.type == TokenType.IDENTIFIER:
            ident = self.current_token.value
            self.advance()
            
            if self.match('['):
                symbol = self.symbol_table.lookup(ident)
                self.advance()
                self.compile_expression()
                self.expect(TokenType.SYMBOL, ']')
                self.code_gen.write_push(self._segment_for(symbol.kind), symbol.index)
                self.code_gen.write_arithmetic('+')
                self.code_gen.write_pop('pointer', 1)
                self.code_gen.write_push('that', 0)
            elif self.match('(', '.'):
                self.pos -= 1
                self.current_token = self.tokens[self.pos]
                self.current_token.value = ident
                self.current_token.type = TokenType.IDENTIFIER
                self.compile_subroutine_call()
            else:
                symbol = self.symbol_table.lookup(ident)
                self.code_gen.write_push(self._segment_for(symbol.kind), symbol.index)
        elif self.match('('):
            self.advance()
            self.compile_expression()
            self.expect(TokenType.SYMBOL, ')')

    def compile_subroutine_call(self):
        name = self.expect(TokenType.IDENTIFIER).value
        nargs = 0
        
        if self.match('.'):
            self.advance()
            method = self.expect(TokenType.IDENTIFIER).value
            
            # Check if name is a variable (object instance)
            symbol = self.symbol_table.lookup(name)
            if symbol:
                # It's a method call on an object: obj.method()
                self.code_gen.write_push(self._segment_for(symbol.kind), symbol.index)
                nargs = 1
                name = f"{symbol.type}.{method}"
            else:
                # It's a static function call: ClassName.method()
                name = f"{name}.{method}"
        else:
            # Method call on self
            self.code_gen.write_push('pointer', 0)
            nargs = 1
            name = f"{self.class_name}.{name}"
        
        self.expect(TokenType.SYMBOL, '(')
        nargs += self.compile_expression_list()
        self.expect(TokenType.SYMBOL, ')')
        self.code_gen.write_call(name, nargs)

    def compile_expression_list(self) -> int:
        count = 0
        if not self.match(')'):
            self.compile_expression()
            count = 1
            while self.match(','):
                self.advance()
                self.compile_expression()
                count += 1
        return count

    def _segment_for(self, kind: SymbolKind) -> str:
        if kind == SymbolKind.FIELD:
            return 'this'
        elif kind == SymbolKind.STATIC:
            return 'static'
        elif kind == SymbolKind.ARG:
            return 'argument'
        elif kind == SymbolKind.VAR:
            return 'local'

# ==================== MAIN ====================
def compile_file(input_file: str, output_file: str):
    with open(input_file, 'r') as f:
        code = f.read()
    
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
    
    parser = Parser(tokens)
    vm_code = parser.parse()
    
    with open(output_file, 'w') as f:
        f.write(vm_code)
    
    print(f"Compiled {input_file} -> {output_file}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python compiler.py <file.jack or directory>")
        sys.exit(1)
    
    path = sys.argv[1]
    
    if os.path.isfile(path):
        if path.endswith('.jack'):
            output = path.replace('.jack', '.vm')
            compile_file(path, output)
    elif os.path.isdir(path):
        files = sorted([f for f in os.listdir(path) if f.endswith('.jack')])
        for file in files:
            input_path = os.path.join(path, file)
            output_path = os.path.join(path, file.replace('.jack', '.vm'))
            try:
                compile_file(input_path, output_path)
            except Exception as e:
                print(f"Error compiling {file}: {e}", file=sys.stderr)

if __name__ == '_main_':
    main()