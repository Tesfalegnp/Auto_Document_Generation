# galaxy_ast_docs/metta_parser.py

import re
from typing import List, Dict, Any, Optional, Tuple

# -------------------------------
# Token class
# -------------------------------
class MeTTaToken:
    """Represents a single token in MeTTa code (type, value, and source position)."""
    def __init__(self, token_type: str, value: str, line: int, column: int):
        self.type = token_type   # e.g., VARIABLE, ATOM, STRING
        self.value = value       # the actual text matched (like "$x", "foo")
        self.line = line         # line number where it appears
        self.column = column     # column number where it starts

    def __repr__(self):
        return f"Token({self.type}, '{self.value}', {self.line}:{self.column})"


# -------------------------------
# AST Node class
# -------------------------------
class MeTTaNode:
    """Represents a node in the MeTTa Abstract Syntax Tree (AST)."""
    def __init__(self, node_type: str, value: str = "", line: int = 0, end_line: int = None):
        self.type = node_type        # e.g., "atom", "function_definition", "expression"
        self.value = value           # extra info (e.g., name of function)
        self.line = line             # starting line
        self.end_line = end_line or line  # ending line (updated as children are added)
        self.children = []           # child nodes
        self.start_point = (line - 1, 0)  # start position (row, col), 0-based
        self.end_point = (self.end_line - 1, 0)  # end position (row, col), 0-based

    def add_child(self, child):
        """Attach a child node and update ending line info if needed."""
        self.children.append(child)
        if child.end_line > self.end_line:
            self.end_line = child.end_line
            self.end_point = (self.end_line - 1, 0)

    def __repr__(self):
        return f"MeTTaNode({self.type}, '{self.value}', {self.line}-{self.end_line})"


# -------------------------------
# Tree wrapper class
# -------------------------------
class MeTTaTree:
    """Represents the full parsed syntax tree (AST)."""
    def __init__(self, root_node: MeTTaNode):
        self.root_node = root_node


# -------------------------------
# Lexer class
# -------------------------------
class MeTTaLexer:
    """Tokenizes raw MeTTa source code into MeTTaToken objects."""

    # Regular expression patterns for each token type in MeTTa
    TOKEN_PATTERNS = [
        ('COMMENT', r';[^\n]*'),                     # ; comment until end of line
        ('EXECUTE', r'!'),                           # Execution operator "!"
        ('LPAREN', r'\('),                           # Left parenthesis "("
        ('RPAREN', r'\)'),                           # Right parenthesis ")"
        ('LBRACKET', r'\['),                         # Left square bracket "["
        ('RBRACKET', r'\]'),                         # Right square bracket "]"
        ('ATOMESPACE', r'&[a-zA-Z_][a-zA-Z0-9_-]*'), # Atomspace reference (like &self, &kb)
        ('VARIABLE', r'\$[a-zA-Z_][a-zA-Z0-9_-]*'),  # Variables ($x, $var1)
        ('STRING', r'"([^"\\]|\\.)*"'),              # String literal (handles escape chars)
        ('NUMBER', r'-?\d+(\.\d+)?'),                # Integer or float numbers
        ('EQUALS', r'='),                            # Equal sign for definitions
        ('OPERATOR', r'[+\-*/><!=]+'),               # Operators (+, -, *, >, <, !=, etc.)
        ('ATOM', r'[a-zA-Z_][a-zA-Z0-9_-]*[!]?'),    # Identifiers/atoms (foo, println!)
        ('WHITESPACE', r'[ \t]+'),                   # Spaces and tabs
        ('NEWLINE', r'\n'),                          # Line breaks
    ]

    def __init__(self):
        # Compile a giant regex with named groups (COMMENT, EXECUTE, etc.)
        self.token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.TOKEN_PATTERNS)
        self.pattern = re.compile(self.token_regex)

    def tokenize(self, code: str) -> List[MeTTaToken]:
        """Convert source code string into a list of MeTTaTokens."""
        tokens = []
        line_num = 1
        line_start = 0

        # Iterate over regex matches in the source code
        for match in self.pattern.finditer(code):
            token_type = match.lastgroup   # Which named group matched
            token_value = match.group()    # Actual text

            # Handle special cases
            if token_type == 'NEWLINE':
                line_num += 1              # Move to next line
                line_start = match.end()
                continue
            elif token_type == 'WHITESPACE':
                continue                   # Skip whitespace

            column = match.start() - line_start
            tokens.append(MeTTaToken(token_type, token_value, line_num, column))

        return tokens


# -------------------------------
# Parser class
# -------------------------------
class MeTTaParser: 
    """Parses tokens into a hierarchical AST (Abstract Syntax Tree)."""

    def __init__(self):
        self.lexer = MeTTaLexer()
        self.tokens = []
        self.current = 0   # Index of current token being processed

    def parse(self, code_bytes: bytes) -> MeTTaTree:
        """Parse UTF-8 encoded MeTTa source code into a syntax tree."""
        try:
            code = code_bytes.decode('utf-8')
        except UnicodeDecodeError:
            # Fallback if there are bad characters
            code = code_bytes.decode('utf-8', errors='ignore')

        # Step 1: tokenize
        self.tokens = self.lexer.tokenize(code)
        self.current = 0

        # Step 2: create root program node
        root = MeTTaNode("program", "", 1)

        # Step 3: parse all top-level forms
        while not self._is_at_end():
            expr = self._parse_top_level()
            if expr:
                root.add_child(expr)

        return MeTTaTree(root)

    # -------------------------------
    # Helpers
    # -------------------------------
    def _is_at_end(self) -> bool:
        """Check if we have reached the end of the token list."""
        return self.current >= len(self.tokens)

    def _peek(self) -> Optional[MeTTaToken]:
        """Return current token without consuming it."""
        if self._is_at_end():
            return None
        return self.tokens[self.current]

    def _advance(self) -> Optional[MeTTaToken]:
        """Consume and return the current token."""
        if self._is_at_end():
            return None
        token = self.tokens[self.current]
        self.current += 1
        return token

    def _match(self, *token_types) -> bool:
        """Check if the current token is one of the given types."""
        current_token = self._peek()
        return current_token and current_token.type in token_types

    # -------------------------------
    # Parsing top-level constructs
    # -------------------------------
    def _parse_top_level(self) -> Optional[MeTTaNode]:
        """Parse a top-level element (comment, execution, or expression)."""
        current_token = self._peek()
        if not current_token:
            return None

        if current_token.type == 'COMMENT':
            return self._parse_comment()
        elif current_token.type == 'EXECUTE':
            return self._parse_execution()
        elif current_token.type == 'LPAREN':
            return self._parse_expression()
        else:
            # Unexpected token → skip
            self._advance()
            return None

    def _parse_comment(self) -> MeTTaNode:
        """Parse a comment node (; ...)."""
        token = self._advance()
        return MeTTaNode("comment", token.value.strip(), token.line)

    def _parse_execution(self) -> MeTTaNode:
        """Parse execution statement !( ... )."""
        execute_token = self._advance()  # consume "!"

        if self._match('LPAREN'):
            expr = self._parse_expression()
            if expr:
                exec_node = MeTTaNode("execution", "!", execute_token.line, expr.end_line)
                exec_node.add_child(expr)
                return exec_node

        return MeTTaNode("execution", "!", execute_token.line)

    # -------------------------------
    # Expressions
    # -------------------------------
    def _parse_expression(self) -> Optional[MeTTaNode]:
        """Parse parenthesized expression."""
        lparen = self._advance()    # consume "("
        start_line = lparen.line

        # Handle empty expression "()" 
        if self._is_at_end() or self._match('RPAREN'):
            if self._match('RPAREN'):
                self._advance()  # consume ")"
            return MeTTaNode("empty_expression", "", start_line)

        # Look at first token inside the "("
        first_token = self._peek()

        if first_token and first_token.type == 'EQUALS':
            result = self._parse_function_definition(start_line)
        else:
            result = self._parse_function_call(start_line)

        # Consume closing ")"
        if self._match('RPAREN'):
            end_token = self._advance()
            if result:
                result.end_line = end_token.line
                result.end_point = (end_token.line - 1, 0)

        return result

    def _parse_function_definition(self, start_line: int) -> MeTTaNode:
        """Parse function definition (= (signature) body...)."""
        self._advance()  # consume "="

        func_node = MeTTaNode("function_definition", "", start_line)

        # Parse signature (= (function_name params...))
        if self._match('LPAREN'):
            signature = self._parse_function_signature()
            if signature:
                func_node.add_child(signature)

        # Parse function body until ")"
        while self._peek() and not self._match('RPAREN'):
            body_expr = self._parse_any_expression()
            if body_expr:
                func_node.add_child(body_expr)

        return func_node

    def _parse_function_signature(self) -> Optional[MeTTaNode]:
        """Parse function signature (name param1 param2 ...)."""
        lparen = self._advance()  # consume "("

        if not self._peek() or self._match('RPAREN'):
            return None

        name_token = self._advance()  # function name
        sig_node = MeTTaNode("function_signature", name_token.value, name_token.line)

        # Parse parameters until ")"
        while self._peek() and not self._match('RPAREN'):
            param = self._parse_any_expression()
            if param:
                sig_node.add_child(param)

        if self._match('RPAREN'):
            end_token = self._advance()
            sig_node.end_line = end_token.line

        return sig_node

    def _parse_function_call(self, start_line: int) -> MeTTaNode:
        """Parse function call (f arg1 arg2 ...)."""
        call_node = MeTTaNode("expression", "", start_line)

        while self._peek() and not self._match('RPAREN'):
            element = self._parse_any_expression()
            if element:
                call_node.add_child(element)

        return call_node

    def _parse_any_expression(self) -> Optional[MeTTaNode]:
        """Parse either a nested expression or an atomic value."""
        current_token = self._peek()
        if not current_token:
            return None

        if current_token.type == 'LPAREN':
            return self._parse_expression()
        else:
            return self._parse_atom()

    # -------------------------------
    # Atoms
    # -------------------------------
    def _parse_atom(self) -> Optional[MeTTaNode]:
        """Parse atomic values (variable, string, number, operator, atom...)."""
        token = self._advance()
        if not token:
            return None

        if token.type == 'VARIABLE':
            return MeTTaNode("variable", token.value, token.line)
        elif token.type == 'ATOMESPACE':
            return MeTTaNode("atomespace", token.value, token.line)
        elif token.type == 'STRING':
            return MeTTaNode("string", token.value, token.line)
        elif token.type == 'NUMBER':
            return MeTTaNode("number", token.value, token.line)
        elif token.type == 'OPERATOR':
            return MeTTaNode("operator", token.value, token.line)
        elif token.type == 'ATOM':
            return MeTTaNode("atom", token.value, token.line)
        else:
            return MeTTaNode("unknown", token.value, token.line)


# -------------------------------
# Factory function
# -------------------------------
def create_metta_parser():
    """Create and return a MeTTaParser instance."""
    return MeTTaParser()
