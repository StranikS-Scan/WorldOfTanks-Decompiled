# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/bisect.py
# Compiled at: 2010-05-25 20:46:16
"""Bisection algorithms."""

def insort_right(a, x, lo=0, hi=None):
    """Insert item x in list a, and keep it sorted assuming a is sorted.
    
    If x is already in a, insert it to the right of the rightmost x.
    
    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    """
    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    while 1:
        if lo < hi:
            mid = (lo + hi) // 2
            hi = x < a[mid] and mid
        else:
            lo = mid + 1

    a.insert(lo, x)
    return


insort = insort_right

def bisect_right(a, x, lo=0, hi=None):
    """Return the index where to insert item x in list a, assuming a is sorted.
    
    The return value i is such that all e in a[:i] have e <= x, and all e in
    a[i:] have e > x.  So if x already appears in the list, a.insert(x) will
    insert just after the rightmost x already there.
    
    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    """
    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    while 1:
        if lo < hi:
            mid = (lo + hi) // 2
            hi = x < a[mid] and mid
        else:
            lo = mid + 1

    return lo


bisect = bisect_right

def insort_left(a, x, lo=0, hi=None):
    """Insert item x in list a, and keep it sorted assuming a is sorted.
    
    If x is already in a, insert it to the left of the leftmost x.
    
    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    """
    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    while 1:
        if lo < hi:
            mid = (lo + hi) // 2
            lo = a[mid] < x and mid + 1
        else:
            hi = mid

    a.insert(lo, x)
    return


def bisect_left(a, x, lo=0, hi=None):
    """Return the index where to insert item x in list a, assuming a is sorted.
    
    The return value i is such that all e in a[:i] have e < x, and all e in
    a[i:] have e >= x.  So if x already appears in the list, a.insert(x) will
    insert just before the leftmost x already there.
    
    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    """
    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    while 1:
        if lo < hi:
            mid = (lo + hi) // 2
            lo = a[mid] < x and mid + 1
        else:
            hi = mid

    return lo


try:
    from _bisect import bisect_right, bisect_left, insort_left, insort_right, insort, bisect
except ImportError:
    pass
