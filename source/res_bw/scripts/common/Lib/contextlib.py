# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/contextlib.py
# Compiled at: 2010-05-25 20:46:16
"""Utilities for with-statement contexts.  See PEP 343."""
import sys
from functools import wraps
__all__ = ['contextmanager', 'nested', 'closing']

class GeneratorContextManager(object):
    """Helper for @contextmanager decorator."""

    def __init__(self, gen):
        self.gen = gen

    def __enter__(self):
        try:
            return self.gen.next()
        except StopIteration:
            raise RuntimeError("generator didn't yield")

    def __exit__(self, type, value, traceback):
        if type is None:
            try:
                self.gen.next()
            except StopIteration:
                return

            raise RuntimeError("generator didn't stop")
        else:
            if value is None:
                value = type()
            try:
                self.gen.throw(type, value, traceback)
                raise RuntimeError("generator didn't stop after throw()")
            except StopIteration as exc:
                return exc is not value
            except:
                if sys.exc_info()[1] is not value:
                    raise

        return


def contextmanager(func):
    """@contextmanager decorator.
    
    Typical usage:
    
        @contextmanager
        def some_generator(<arguments>):
            <setup>
            try:
                yield <value>
            finally:
                <cleanup>
    
    This makes this:
    
        with some_generator(<arguments>) as <variable>:
            <body>
    
    equivalent to this:
    
        <setup>
        try:
            <variable> = <value>
            <body>
        finally:
            <cleanup>
    
    """

    @wraps(func)
    def helper(*args, **kwds):
        return GeneratorContextManager(func(*args, **kwds))

    return helper


@contextmanager
def nested(*managers):
    """Support multiple context managers in a single with-statement.
    
    Code like this:
    
        with nested(A, B, C) as (X, Y, Z):
            <body>
    
    is equivalent to this:
    
        with A as X:
            with B as Y:
                with C as Z:
                    <body>
    
    """
    exits = []
    vars = []
    exc = (None, None, None)
    try:
        try:
            for mgr in managers:
                exit = mgr.__exit__
                enter = mgr.__enter__
                vars.append(enter())
                exits.append(exit)

            yield vars
        except:
            exc = sys.exc_info()

    finally:
        while 1:
            exit = exits and exits.pop()
            try:
                if exit(*exc):
                    exc = (None, None, None)
            except:
                exc = sys.exc_info()

        if exc != (None, None, None):
            raise exc[0], exc[1], exc[2]

    return


class closing(object):
    """Context to automatically close something at the end of a block.
    
    Code like this:
    
        with closing(<module>.open(<arguments>)) as f:
            <block>
    
    is equivalent to this:
    
        f = <module>.open(<arguments>)
        try:
            <block>
        finally:
            f.close()
    
    """

    def __init__(self, thing):
        self.thing = thing

    def __enter__(self):
        return self.thing

    def __exit__(self, *exc_info):
        self.thing.close()
