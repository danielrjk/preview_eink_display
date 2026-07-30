"""
Resource limits for the code submitted through the editor.

Submitted code previously ran with no ceiling on time or size, so a single
request could occupy a worker indefinitely. Two cases were reproducible:

  * `while True: pass` never returns.
  * `tela.fillRect(0, 0, 100000000, 128, 1)` iterates every off-screen column.
    Measured 2.57s at width 100_000, so 10**8 is hours of CPU per request.

The wall-clock ceiling here is enforced with sys.settrace, which fires between
Python statements. That is portable, unlike signal.SIGALRM, which does not
exist on Windows, and unlike resource.setrlimit, which is POSIX only and
process wide rather than per request.

Known limitation: the trace hook runs between statements, so it cannot
interrupt a single long operation inside one statement. `'a' * 10**12` is
still one allocation the interpreter performs before the next hook fires.
Bounding memory as well means running submitted code in a separate process
with resource.setrlimit applied in the child; that is the next step if this
is ever hardened further, and it is the only way to get a hard guarantee.
"""

import os
import sys
import time
from contextlib import contextmanager


def _env_int(name, default):
    try:
        value = int(os.environ.get(name, ''))
    except ValueError:
        return default
    return value if value > 0 else default


# Generous for drawing on a 296x128 display; the slowest legitimate operation
# measured is well under a second.
TIME_LIMIT_SECONDS = _env_int('EINK_TIME_LIMIT_SECONDS', 5)

# Bounds the work done before execution even starts: parsing, the regex
# passes in the transpiler, and the AST walk.
MAX_CODE_CHARS = _env_int('EINK_MAX_CODE_CHARS', 20_000)
MAX_CODE_LINES = _env_int('EINK_MAX_CODE_LINES', 1_000)

# Checking the clock on every traced event is measurably slower than checking
# it periodically, and the granularity costs nothing at a multi-second limit.
_CLOCK_CHECK_INTERVAL = 2_000


class ExecutionTimeout(BaseException):
    """
    Raised when submitted code exceeds TIME_LIMIT_SECONDS.

    Inherits BaseException, not Exception, for the same reason
    KeyboardInterrupt does: a broad `except Exception` in submitted code must
    not be able to swallow it and keep looping. Whether the deadline happens
    to fall on a line inside a try block should not decide if the limit works.
    """


class CodeTooLarge(Exception):
    """Raised when a submission is too large to be worth executing."""


def check_size(code):
    """Reject oversized submissions before any parsing happens."""
    if len(code) > MAX_CODE_CHARS:
        raise CodeTooLarge(
            f'o codigo excede {MAX_CODE_CHARS} caracteres'
        )
    if code.count('\n') + 1 > MAX_CODE_LINES:
        raise CodeTooLarge(
            f'o codigo excede {MAX_CODE_LINES} linhas'
        )


@contextmanager
def time_limit(seconds=None):
    """
    Abort the enclosed block once `seconds` of wall clock have elapsed.

    Implemented with a trace hook, so it interrupts between statements. Loops
    of any depth are covered, including ones inside the drawing classes, since
    those frames are Python too.

    The hook is installed per thread, so concurrent requests do not interfere.
    Any previously installed hook is restored on exit, which keeps this from
    fighting a debugger or coverage tool.
    """
    limit = TIME_LIMIT_SECONDS if seconds is None else seconds
    deadline = time.monotonic() + limit
    countdown = [_CLOCK_CHECK_INTERVAL]

    def tracer(frame, event, arg):
        countdown[0] -= 1
        if countdown[0] <= 0:
            countdown[0] = _CLOCK_CHECK_INTERVAL
            if time.monotonic() > deadline:
                raise ExecutionTimeout(
                    f'o codigo excedeu o limite de {limit}s'
                )
        return tracer

    previous = sys.gettrace()
    sys.settrace(tracer)
    try:
        yield
    finally:
        sys.settrace(previous)
