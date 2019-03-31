# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/sets.py
# Compiled at: 2010-05-25 20:46:16
"""Classes to represent arbitrary sets (including sets of sets).

This module implements sets using dictionaries whose values are
ignored.  The usual operations (union, intersection, deletion, etc.)
are provided as both methods and operators.

Important: sets are not sequences!  While they support 'x in s',
'len(s)', and 'for x in s', none of those operations are unique for
sequences; for example, mappings support all three as well.  The
characteristic operation for sequences is subscripting with small
integers: s[i], for i in range(len(s)).  Sets don't support
subscripting at all.  Also, sequences allow multiple occurrences and
their elements have a definite order; sets on the other hand don't
record multiple occurrences and don't remember the order of element
insertion (which is why they don't support s[i]).

The following classes are provided:

BaseSet -- All the operations common to both mutable and immutable
    sets. This is an abstract class, not meant to be directly
    instantiated.

Set -- Mutable sets, subclass of BaseSet; not hashable.

ImmutableSet -- Immutable sets, subclass of BaseSet; hashable.
    An iterable argument is mandatory to create an ImmutableSet.

_TemporarilyImmutableSet -- A wrapper around a Set, hashable,
    giving the same hash value as the immutable set equivalent
    would have.  Do not use this class directly.

Only hashable objects can be added to a Set. In particular, you cannot
really add a Set as an element to another Set; if you try, what is
actually added is an ImmutableSet built from it (it compares equal to
the one you tried adding).

When you ask if `x in y' where x is a Set and y is a Set or
ImmutableSet, x is wrapped into a _TemporarilyImmutableSet z, and
what's tested is actually `z in y'.

"""
from __future__ import generators
try:
    from itertools import ifilter, ifilterfalse
except ImportError:

    def ifilter(predicate, iterable):
        if predicate is None:

            def predicate(x):
                return x

        for x in iterable:
            if predicate(x):
                yield x

        return


    def ifilterfalse(predicate, iterable):
        if predicate is None:

            def predicate(x):
                return x

        for x in iterable:
            if not predicate(x):
                yield x

        return


    try:
        (True, False)
    except NameError:
        True, False = (0 == 0, 0 != 0)

__all__ = ['BaseSet', 'Set', 'ImmutableSet']
import warnings
warnings.warn('the sets module is deprecated', DeprecationWarning, stacklevel=2)

class BaseSet(object):
    """Common base class for mutable and immutable sets."""
    __slots__ = ['_data']

    def __init__(self):
        """This is an abstract class."""
        if self.__class__ is BaseSet:
            raise TypeError, 'BaseSet is an abstract class.  Use Set or ImmutableSet.'

    def __len__(self):
        """Return the number of elements of a set."""
        return len(self._data)

    def __repr__(self):
        """Return string representation of a set.
        
        This looks like 'Set([<list of elements>])'.
        """
        return self._repr()

    __str__ = __repr__

    def _repr(self, sorted=False):
        elements = self._data.keys()
        if sorted:
            elements.sort()
        return '%s(%r)' % (self.__class__.__name__, elements)

    def __iter__(self):
        """Return an iterator over the elements or a set.
        
        This is the keys iterator for the underlying dict.
        """
        return self._data.iterkeys()

    def __cmp__(self, other):
        raise TypeError, "can't compare sets using cmp()"

    def __eq__(self, other):
        if isinstance(other, BaseSet):
            return self._data == other._data
        else:
            return False

    def __ne__(self, other):
        if isinstance(other, BaseSet):
            return self._data != other._data
        else:
            return True

    def copy(self):
        """Return a shallow copy of a set."""
        result = self.__class__()
        result._data.update(self._data)
        return result

    __copy__ = copy

    def __deepcopy__(self, memo):
        """Return a deep copy of a set; used by copy module."""
        from copy import deepcopy
        result = self.__class__()
        memo[id(self)] = result
        data = result._data
        value = True
        for elt in self:
            data[deepcopy(elt, memo)] = value

        return result

    def __or__(self, other):
        """Return the union of two sets as a new set.
        
        (I.e. all elements that are in either set.)
        """
        if not isinstance(other, BaseSet):
            return NotImplemented
        return self.union(other)

    def union(self, other):
        """Return the union of two sets as a new set.
        
        (I.e. all elements that are in either set.)
        """
        result = self.__class__(self)
        result._update(other)
        return result

    def __and__(self, other):
        """Return the intersection of two sets as a new set.
        
        (I.e. all elements that are in both sets.)
        """
        if not isinstance(other, BaseSet):
            return NotImplemented
        return self.intersection(other)

    def intersection(self, other):
        """Return the intersection of two sets as a new set.
        
        (I.e. all elements that are in both sets.)
        """
        if not isinstance(other, BaseSet):
            other = Set(other)
        if len(self) <= len(other):
            little, big = self, other
        else:
            little, big = other, self
        common = ifilter(big._data.has_key, little)
        return self.__class__(common)

    def __xor__(self, other):
        """Return the symmetric difference of two sets as a new set.
        
        (I.e. all elements that are in exactly one of the sets.)
        """
        if not isinstance(other, BaseSet):
            return NotImplemented
        return self.symmetric_difference(other)

    def symmetric_difference(self, other):
        """Return the symmetric difference of two sets as a new set.
        
        (I.e. all elements that are in exactly one of the sets.)
        """
        result = self.__class__()
        data = result._data
        value = True
        selfdata = self._data
        try:
            otherdata = other._data
        except AttributeError:
            otherdata = Set(other)._data

        for elt in ifilterfalse(otherdata.has_key, selfdata):
            data[elt] = value

        for elt in ifilterfalse(selfdata.has_key, otherdata):
            data[elt] = value

        return result

    def __sub__(self, other):
        """Return the difference of two sets as a new Set.
        
        (I.e. all elements that are in this set and not in the other.)
        """
        if not isinstance(other, BaseSet):
            return NotImplemented
        return self.difference(other)

    def difference(self, other):
        """Return the difference of two sets as a new Set.
        
        (I.e. all elements that are in this set and not in the other.)
        """
        result = self.__class__()
        data = result._data
        try:
            otherdata = other._data
        except AttributeError:
            otherdata = Set(other)._data

        value = True
        for elt in ifilterfalse(otherdata.has_key, self):
            data[elt] = value

        return result

    def __contains__(self, element):
        """Report whether an element is a member of a set.
        
        (Called in response to the expression `element in self'.)
        """
        try:
            return element in self._data
        except TypeError:
            transform = getattr(element, '__as_temporarily_immutable__', None)
            if transform is None:
                raise
            return transform() in self._data

        return

    def issubset(self, other):
        """Report whether another set contains this set."""
        self._binary_sanity_check(other)
        if len(self) > len(other):
            return False
        for elt in ifilterfalse(other._data.has_key, self):
            return False

        return True

    def issuperset(self, other):
        """Report whether this set contains another set."""
        self._binary_sanity_check(other)
        if len(self) < len(other):
            return False
        for elt in ifilterfalse(self._data.has_key, other):
            return False

        return True

    __le__ = issubset
    __ge__ = issuperset

    def __lt__(self, other):
        self._binary_sanity_check(other)
        return len(self) < len(other) and self.issubset(other)

    def __gt__(self, other):
        self._binary_sanity_check(other)
        return len(self) > len(other) and self.issuperset(other)

    def _binary_sanity_check(self, other):
        if not isinstance(other, BaseSet):
            raise TypeError, 'Binary operation only permitted between sets'

    def _compute_hash(self):
        result = 0
        for elt in self:
            result ^= hash(elt)

        return result

    def _update--- This code section failed: ---

 362       0	LOAD_FAST         'self'
           3	LOAD_ATTR         '_data'
           6	STORE_FAST        'data'

 365       9	LOAD_GLOBAL       'isinstance'
          12	LOAD_FAST         'iterable'
          15	LOAD_GLOBAL       'BaseSet'
          18	CALL_FUNCTION_2   ''
          21	JUMP_IF_FALSE     '44'

 366      24	LOAD_FAST         'data'
          27	LOAD_ATTR         'update'
          30	LOAD_FAST         'iterable'
          33	LOAD_ATTR         '_data'
          36	CALL_FUNCTION_1   ''
          39	POP_TOP           ''

 367      40	LOAD_CONST        ''
          43	RETURN_END_IF     ''

 369      44	LOAD_GLOBAL       'True'
          47	STORE_FAST        'value'

 371      50	LOAD_GLOBAL       'type'
          53	LOAD_FAST         'iterable'
          56	CALL_FUNCTION_1   ''
          59	LOAD_GLOBAL       'list'
          62	LOAD_GLOBAL       'tuple'
          65	LOAD_GLOBAL       'xrange'
          68	BUILD_TUPLE_3     ''
          71	COMPARE_OP        'in'
          74	JUMP_IF_FALSE     '209'

 374      77	LOAD_GLOBAL       'iter'
          80	LOAD_FAST         'iterable'
          83	CALL_FUNCTION_1   ''
          86	STORE_FAST        'it'

 375      89	SETUP_LOOP        '309'
          92	LOAD_GLOBAL       'True'
          95	JUMP_IF_FALSE     '205'

 376      98	SETUP_EXCEPT      '136'

 377     101	SETUP_LOOP        '128'
         104	LOAD_FAST         'it'
         107	GET_ITER          ''
         108	FOR_ITER          '127'
         111	STORE_FAST        'element'

 378     114	LOAD_FAST         'value'
         117	LOAD_FAST         'data'
         120	LOAD_FAST         'element'
         123	STORE_SUBSCR      ''
         124	JUMP_BACK         '108'
         127	POP_BLOCK         ''
       128_0	COME_FROM         '101'

 379     128	LOAD_CONST        ''
         131	RETURN_VALUE      ''
         132	POP_BLOCK         ''
         133	JUMP_BACK         '92'
       136_0	COME_FROM         '98'

 380     136	DUP_TOP           ''
         137	LOAD_GLOBAL       'TypeError'
         140	COMPARE_OP        'exception match'
         143	JUMP_IF_FALSE     '201'
         146	POP_TOP           ''
         147	POP_TOP           ''
         148	POP_TOP           ''

 381     149	LOAD_GLOBAL       'getattr'
         152	LOAD_FAST         'element'
         155	LOAD_CONST        '__as_immutable__'
         158	LOAD_CONST        ''
         161	CALL_FUNCTION_3   ''
         164	STORE_FAST        'transform'

 382     167	LOAD_FAST         'transform'
         170	LOAD_CONST        ''
         173	COMPARE_OP        'is'
         176	JUMP_IF_FALSE     '185'

 383     179	RAISE_VARARGS_0   ''
         182	JUMP_FORWARD      '185'
       185_0	COME_FROM         '182'

 384     185	LOAD_FAST         'value'
         188	LOAD_FAST         'data'
         191	LOAD_FAST         'transform'
         194	CALL_FUNCTION_0   ''
         197	STORE_SUBSCR      ''
         198	JUMP_BACK         '92'
         201	END_FINALLY       ''
       202_0	COME_FROM         '201'
         202	JUMP_BACK         '92'
         205	POP_BLOCK         ''
       206_0	COME_FROM         '89'
         206	JUMP_FORWARD      '309'

 387     209	SETUP_LOOP        '309'
         212	LOAD_FAST         'iterable'
         215	GET_ITER          ''
         216	FOR_ITER          '308'
         219	STORE_FAST        'element'

 388     222	SETUP_EXCEPT      '239'

 389     225	LOAD_FAST         'value'
         228	LOAD_FAST         'data'
         231	LOAD_FAST         'element'
         234	STORE_SUBSCR      ''
         235	POP_BLOCK         ''
         236	JUMP_BACK         '216'
       239_0	COME_FROM         '222'

 390     239	DUP_TOP           ''
         240	LOAD_GLOBAL       'TypeError'
         243	COMPARE_OP        'exception match'
         246	JUMP_IF_FALSE     '304'
         249	POP_TOP           ''
         250	POP_TOP           ''
         251	POP_TOP           ''

 391     252	LOAD_GLOBAL       'getattr'
         255	LOAD_FAST         'element'
         258	LOAD_CONST        '__as_immutable__'
         261	LOAD_CONST        ''
         264	CALL_FUNCTION_3   ''
         267	STORE_FAST        'transform'

 392     270	LOAD_FAST         'transform'
         273	LOAD_CONST        ''
         276	COMPARE_OP        'is'
         279	JUMP_IF_FALSE     '288'

 393     282	RAISE_VARARGS_0   ''
         285	JUMP_FORWARD      '288'
       288_0	COME_FROM         '285'

 394     288	LOAD_FAST         'value'
         291	LOAD_FAST         'data'
         294	LOAD_FAST         'transform'
         297	CALL_FUNCTION_0   ''
         300	STORE_SUBSCR      ''
         301	JUMP_BACK         '216'
         304	END_FINALLY       ''
       305_0	COME_FROM         '304'
         305	JUMP_BACK         '216'
         308	POP_BLOCK         ''
       309_0	COME_FROM         '206'
       309_1	COME_FROM         '209'
         309	LOAD_CONST        ''
         312	RETURN_VALUE      ''

Syntax error at or near 'POP_BLOCK' token at offset 205


class ImmutableSet(BaseSet):
    """Immutable set class."""
    __slots__ = ['_hashcode']

    def __init__(self, iterable=None):
        """Construct an immutable set from an optional iterable."""
        self._hashcode = None
        self._data = {}
        if iterable is not None:
            self._update(iterable)
        return

    def __hash__(self):
        if self._hashcode is None:
            self._hashcode = self._compute_hash()
        return self._hashcode

    def __getstate__(self):
        return (self._data, self._hashcode)

    def __setstate__(self, state):
        self._data, self._hashcode = state


class Set(BaseSet):
    """ Mutable set class."""
    __slots__ = []

    def __init__(self, iterable=None):
        """Construct a set from an optional iterable."""
        self._data = {}
        if iterable is not None:
            self._update(iterable)
        return

    def __getstate__(self):
        return (self._data,)

    def __setstate__(self, data):
        self._data = data

    __hash__ = None

    def __ior__(self, other):
        """Update a set with the union of itself and another."""
        self._binary_sanity_check(other)
        self._data.update(other._data)
        return self

    def union_update(self, other):
        """Update a set with the union of itself and another."""
        self._update(other)

    def __iand__(self, other):
        """Update a set with the intersection of itself and another."""
        self._binary_sanity_check(other)
        self._data = (self & other)._data
        return self

    def intersection_update(self, other):
        """Update a set with the intersection of itself and another."""
        if isinstance(other, BaseSet):
            self &= other
        else:
            self._data = self.intersection(other)._data

    def __ixor__(self, other):
        """Update a set with the symmetric difference of itself and another."""
        self._binary_sanity_check(other)
        self.symmetric_difference_update(other)
        return self

    def symmetric_difference_update(self, other):
        """Update a set with the symmetric difference of itself and another."""
        data = self._data
        value = True
        if not isinstance(other, BaseSet):
            other = Set(other)
        if self is other:
            self.clear()
        for elt in other:
            if elt in data:
                del data[elt]
            else:
                data[elt] = value

    def __isub__(self, other):
        """Remove all elements of another set from this set."""
        self._binary_sanity_check(other)
        self.difference_update(other)
        return self

    def difference_update(self, other):
        """Remove all elements of another set from this set."""
        data = self._data
        if not isinstance(other, BaseSet):
            other = Set(other)
        if self is other:
            self.clear()
        for elt in ifilter(data.has_key, other):
            del data[elt]

    def update(self, iterable):
        """Add all values from an iterable (such as a list or file)."""
        self._update(iterable)

    def clear(self):
        """Remove all elements from this set."""
        self._data.clear()

    def add(self, element):
        """Add an element to a set.
        
        This has no effect if the element is already present.
        """
        try:
            self._data[element] = True
        except TypeError:
            transform = getattr(element, '__as_immutable__', None)
            if transform is None:
                raise
            self._data[transform()] = True

        return

    def remove(self, element):
        """Remove an element from a set; it must be a member.
        
        If the element is not a member, raise a KeyError.
        """
        try:
            del self._data[element]
        except TypeError:
            transform = getattr(element, '__as_temporarily_immutable__', None)
            if transform is None:
                raise
            del self._data[transform()]

        return

    def discard(self, element):
        """Remove an element from a set if it is a member.
        
        If the element is not a member, do nothing.
        """
        try:
            self.remove(element)
        except KeyError:
            pass

    def pop(self):
        """Remove and return an arbitrary set element."""
        return self._data.popitem()[0]

    def __as_immutable__(self):
        return ImmutableSet(self)

    def __as_temporarily_immutable__(self):
        return _TemporarilyImmutableSet(self)


class _TemporarilyImmutableSet(BaseSet):

    def __init__(self, set):
        self._set = set
        self._data = set._data

    def __hash__(self):
        return self._set._compute_hash()