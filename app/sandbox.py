"""
Sandbox for the code submitted through the editor.

The previewer executes code typed by an anonymous visitor. Handing that to
exec() with an unrestricted namespace is remote code execution, so this module
constrains it two ways before anything runs:

  1. An allowlist of AST node types. Anything not explicitly permitted is
     rejected, so new Python syntax cannot silently widen the sandbox.
  2. A replacement __builtins__ containing only harmless callables.

Both are required. Passing a globals dict without a '__builtins__' key does
NOT restrict anything: CPython inserts the real builtins module, leaving
__import__ and open reachable.

Names and attributes beginning with an underscore are refused. That single
rule blocks the standard escape route, which is to walk from any object to
its type and back out to the interpreter, for example via __class__ and
__subclasses__. 'format' and 'mro' are refused for the same reason: str.format
can traverse attributes named inside the format string, where the AST cannot
see them.

This module does not bound how long the code runs or how much memory it
allocates. That is a separate concern; see the execution limits work.
"""

import ast

# --- Syntax -----------------------------------------------------------------

# Deliberately a positive list. Anything absent here is rejected.
_ALLOWED_NODES = frozenset({
    # Structure
    ast.Module, ast.Expr, ast.Pass,
    # Binding
    ast.Assign, ast.AugAssign, ast.Name, ast.Load, ast.Store, ast.Starred,
    # Control flow
    ast.If, ast.For, ast.While, ast.Break, ast.Continue, ast.IfExp,
    # Callables. Bodies are validated by the same rules, so these add no risk.
    ast.FunctionDef, ast.Lambda, ast.Return, ast.arguments, ast.arg,
    ast.Call, ast.keyword,
    # Attribute access, filtered further by _check_attribute below
    ast.Attribute,
    # Literals and containers
    ast.Constant, ast.JoinedStr, ast.FormattedValue,
    ast.List, ast.Tuple, ast.Dict, ast.Set, ast.Subscript, ast.Slice,
    # Comprehensions
    ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp,
    ast.comprehension,
    # Operators
    ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
    ast.LShift, ast.RShift, ast.BitOr, ast.BitXor, ast.BitAnd, ast.MatMult,
    ast.USub, ast.UAdd, ast.Not, ast.Invert,
    ast.And, ast.Or,
    ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
    ast.In, ast.NotIn, ast.Is, ast.IsNot,
})

# Reachable without a leading underscore, so the underscore rule misses them.
_BLOCKED_ATTRS = frozenset({
    'format',      # "{0.__class__}".format(x) traverses attributes at runtime
    'format_map',
    'mro',         # type(x).mro() reaches every loaded class
})

# CPython exposes interpreter internals through these prefixes rather than
# dunders, so the underscore rule does not cover them. A generator's gi_frame
# yields a frame, whose f_back walks up the call stack and whose f_builtins is
# the real builtins module of whatever frame it lands in; tb_frame does the
# same from a traceback. Blocking the prefixes closes the whole family at once
# instead of chasing individual attribute names.
_BLOCKED_ATTR_PREFIXES = (
    'f_',      # frame: f_back, f_globals, f_builtins, f_locals, f_code
    'gi_',     # generator: gi_frame, gi_code
    'cr_',     # coroutine: cr_frame, cr_code
    'ag_',     # async generator: ag_frame, ag_code
    'tb_',     # traceback: tb_frame, tb_next
    'co_',     # code object: co_consts, co_code
    'func_',   # legacy function attributes
)

# Friendlier messages than "node type X is not allowed" for the cases a user
# is most likely to hit by accident.
_NODE_EXPLANATIONS = {
    ast.Import: 'imports are not available here',
    ast.ImportFrom: 'imports are not available here',
    ast.ClassDef: 'class definitions are not available here',
    ast.With: '"with" blocks are not available here',
    ast.Try: '"try" blocks are not available here',
    ast.Raise: '"raise" is not available here',
    ast.Global: '"global" is not available here',
    ast.Nonlocal: '"nonlocal" is not available here',
    ast.Delete: '"del" is not available here',
    ast.Assert: '"assert" is not available here',
    ast.Await: '"await" is not available here',
    ast.Yield: '"yield" is not available here',
    ast.YieldFrom: '"yield from" is not available here',
    ast.NamedExpr: 'the walrus operator is not available here',
}


class SandboxError(Exception):
    """Raised when submitted code uses something outside the sandbox."""

    def __init__(self, message, lineno=None):
        super().__init__(message)
        self.lineno = lineno


# --- Runtime namespace ------------------------------------------------------

# Only callables that cannot touch the interpreter, the filesystem or the
# network. Notably absent: __import__, open, eval, exec, compile, getattr,
# setattr, globals, locals, vars, dir, type, input, help, breakpoint.
SAFE_BUILTINS = {
    'abs': abs, 'all': all, 'any': any, 'bool': bool, 'chr': chr,
    'dict': dict, 'divmod': divmod, 'enumerate': enumerate, 'float': float,
    'int': int, 'len': len, 'list': list, 'max': max, 'min': min,
    'ord': ord, 'pow': pow, 'print': print, 'range': range,
    'reversed': reversed, 'round': round, 'set': set, 'sorted': sorted,
    'str': str, 'sum': sum, 'tuple': tuple, 'zip': zip,
    'True': True, 'False': False, 'None': None,
}


def _check_name(identifier, node):
    if identifier.startswith('_'):
        raise SandboxError(
            f'name "{identifier}" is not available here',
            getattr(node, 'lineno', None),
        )


def _check_attribute(node):
    attr = node.attr
    if attr.startswith('_'):
        raise SandboxError(
            f'attribute "{attr}" is not available here',
            getattr(node, 'lineno', None),
        )
    if attr in _BLOCKED_ATTRS:
        raise SandboxError(
            f'attribute "{attr}" is not available here; '
            f'use an f-string instead',
            getattr(node, 'lineno', None),
        )
    if attr.startswith(_BLOCKED_ATTR_PREFIXES):
        raise SandboxError(
            f'attribute "{attr}" is not available here',
            getattr(node, 'lineno', None),
        )


def validate(tree):
    """Walk the tree and raise SandboxError on the first disallowed node."""
    for node in ast.walk(tree):
        node_type = type(node)

        if node_type not in _ALLOWED_NODES:
            explanation = _NODE_EXPLANATIONS.get(node_type)
            if explanation is None:
                explanation = f'{node_type.__name__} is not available here'
            raise SandboxError(explanation, getattr(node, 'lineno', None))

        if node_type is ast.Name:
            _check_name(node.id, node)
        elif node_type is ast.Attribute:
            _check_attribute(node)
        elif node_type is ast.arg:
            _check_name(node.arg, node)
        elif node_type is ast.FunctionDef:
            _check_name(node.name, node)
            if node.decorator_list:
                raise SandboxError(
                    'decorators are not available here',
                    getattr(node, 'lineno', None),
                )
    return tree


def compile_checked(code, filename='<user-code>'):
    """
    Parse, validate and compile submitted code.

    Raises SyntaxError for malformed code and SandboxError for code that
    parses but uses something outside the sandbox.
    """
    tree = ast.parse(code, filename=filename, mode='exec')
    validate(tree)
    return compile(tree, filename, 'exec')


def build_globals(api):
    """
    Wrap the drawing API in a globals dict with restricted builtins.

    The '__builtins__' key must be present. Without it CPython supplies the
    real builtins module and the sandbox is void.
    """
    namespace = {'__builtins__': dict(SAFE_BUILTINS)}
    namespace.update(api)
    return namespace
