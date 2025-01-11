# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/common/grinch_common/shared_helpers.py
import weakref

def safeWeakProxy(entity):
    return entity if type(entity).__name__ == 'weakproxy' else weakref.proxy(entity)
