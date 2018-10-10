# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/lib2to3/pytree.py
__author__ = 'Guido van Rossum <guido@python.org>'
import sys
import warnings
from StringIO import StringIO
HUGE = 2147483647
_type_reprs = {}

def type_repr(type_num):
    global _type_reprs
    if not _type_reprs:
        from .pygram import python_symbols
        for name, val in python_symbols.__dict__.items():
            if type(val) == int:
                _type_reprs[val] = name

    return _type_reprs.setdefault(type_num, type_num)


class Base(object):
    type = None
    parent = None
    children = ()
    was_changed = False
    was_checked = False

    def __new__(cls, *args, **kwds):
        return object.__new__(cls)

    def __eq__(self, other):
        return NotImplemented if self.__class__ is not other.__class__ else self._eq(other)

    __hash__ = None

    def __ne__(self, other):
        return NotImplemented if self.__class__ is not other.__class__ else not self._eq(other)

    def _eq(self, other):
        raise NotImplementedError

    def clone(self):
        raise NotImplementedError

    def post_order(self):
        raise NotImplementedError

    def pre_order(self):
        raise NotImplementedError

    def set_prefix(self, prefix):
        warnings.warn('set_prefix() is deprecated; use the prefix property', DeprecationWarning, stacklevel=2)
        self.prefix = prefix

    def get_prefix(self):
        warnings.warn('get_prefix() is deprecated; use the prefix property', DeprecationWarning, stacklevel=2)
        return self.prefix

    def replace(self, new):
        if not isinstance(new, list):
            new = [new]
        l_children = []
        found = False
        for ch in self.parent.children:
            if ch is self:
                if new is not None:
                    l_children.extend(new)
                found = True
            l_children.append(ch)

        self.parent.changed()
        self.parent.children = l_children
        for x in new:
            x.parent = self.parent

        self.parent = None
        return

    def get_lineno(self):
        node = self
        while not isinstance(node, Leaf):
            if not node.children:
                return
            node = node.children[0]

        return node.lineno

    def changed(self):
        if self.parent:
            self.parent.changed()
        self.was_changed = True

    def remove(self):
        if self.parent:
            for i, node in enumerate(self.parent.children):
                if node is self:
                    self.parent.changed()
                    del self.parent.children[i]
                    self.parent = None
                    return i

        return

    @property
    def next_sibling(self):
        if self.parent is None:
            return
        else:
            for i, child in enumerate(self.parent.children):
                if child is self:
                    try:
                        return self.parent.children[i + 1]
                    except IndexError:
                        return

            return

    @property
    def prev_sibling(self):
        if self.parent is None:
            return
        else:
            for i, child in enumerate(self.parent.children):
                if child is self:
                    if i == 0:
                        return
                    return self.parent.children[i - 1]

            return

    def leaves(self):
        for child in self.children:
            for x in child.leaves():
                yield x

    def depth(self):
        return 0 if self.parent is None else 1 + self.parent.depth()

    def get_suffix(self):
        next_sib = self.next_sibling
        return u'' if next_sib is None else next_sib.prefix

    if sys.version_info < (3, 0):

        def __str__(self):
            return unicode(self).encode('ascii')


class Node(Base):

    def __init__(self, type, children, context=None, prefix=None, fixers_applied=None):
        self.type = type
        self.children = list(children)
        for ch in self.children:
            ch.parent = self

        if prefix is not None:
            self.prefix = prefix
        if fixers_applied:
            self.fixers_applied = fixers_applied[:]
        else:
            self.fixers_applied = None
        return

    def __repr__(self):
        return '%s(%s, %r)' % (self.__class__.__name__, type_repr(self.type), self.children)

    def __unicode__(self):
        return u''.join(map(unicode, self.children))

    if sys.version_info > (3, 0):
        __str__ = __unicode__

    def _eq(self, other):
        return (self.type, self.children) == (other.type, other.children)

    def clone(self):
        return Node(self.type, [ ch.clone() for ch in self.children ], fixers_applied=self.fixers_applied)

    def post_order(self):
        for child in self.children:
            for node in child.post_order():
                yield node

        yield self

    def pre_order(self):
        yield self
        for child in self.children:
            for node in child.pre_order():
                yield node

    def _prefix_getter(self):
        return '' if not self.children else self.children[0].prefix

    def _prefix_setter(self, prefix):
        if self.children:
            self.children[0].prefix = prefix

    prefix = property(_prefix_getter, _prefix_setter)

    def set_child(self, i, child):
        child.parent = self
        self.children[i].parent = None
        self.children[i] = child
        self.changed()
        return

    def insert_child(self, i, child):
        child.parent = self
        self.children.insert(i, child)
        self.changed()

    def append_child(self, child):
        child.parent = self
        self.children.append(child)
        self.changed()


class Leaf(Base):
    _prefix = ''
    lineno = 0
    column = 0

    def __init__(self, type, value, context=None, prefix=None, fixers_applied=[]):
        if context is not None:
            self._prefix, (self.lineno, self.column) = context
        self.type = type
        self.value = value
        if prefix is not None:
            self._prefix = prefix
        self.fixers_applied = fixers_applied[:]
        return

    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__, self.type, self.value)

    def __unicode__(self):
        return self.prefix + unicode(self.value)

    if sys.version_info > (3, 0):
        __str__ = __unicode__

    def _eq(self, other):
        return (self.type, self.value) == (other.type, other.value)

    def clone(self):
        return Leaf(self.type, self.value, (self.prefix, (self.lineno, self.column)), fixers_applied=self.fixers_applied)

    def leaves(self):
        yield self

    def post_order(self):
        yield self

    def pre_order(self):
        yield self

    def _prefix_getter(self):
        return self._prefix

    def _prefix_setter(self, prefix):
        self.changed()
        self._prefix = prefix

    prefix = property(_prefix_getter, _prefix_setter)


def convert(gr, raw_node):
    type, value, context, children = raw_node
    if children or type in gr.number2symbol:
        if len(children) == 1:
            return children[0]
        return Node(type, children, context=context)
    else:
        return Leaf(type, value, context=context)


class BasePattern(object):
    type = None
    content = None
    name = None

    def __new__(cls, *args, **kwds):
        return object.__new__(cls)

    def __repr__(self):
        args = [type_repr(self.type), self.content, self.name]
        while args and args[-1] is None:
            del args[-1]

        return '%s(%s)' % (self.__class__.__name__, ', '.join(map(repr, args)))

    def optimize(self):
        return self

    def match(self, node, results=None):
        if self.type is not None and node.type != self.type:
            return False
        else:
            if self.content is not None:
                r = None
                if results is not None:
                    r = {}
                if not self._submatch(node, r):
                    return False
                if r:
                    results.update(r)
            if results is not None and self.name:
                results[self.name] = node
            return True

    def match_seq(self, nodes, results=None):
        return False if len(nodes) != 1 else self.match(nodes[0], results)

    def generate_matches(self, nodes):
        r = {}
        if nodes and self.match(nodes[0], r):
            yield (1, r)


class LeafPattern(BasePattern):

    def __init__(self, type=None, content=None, name=None):
        if type is not None:
            pass
        if content is not None:
            pass
        self.type = type
        self.content = content
        self.name = name
        return

    def match(self, node, results=None):
        return False if not isinstance(node, Leaf) else BasePattern.match(self, node, results)

    def _submatch(self, node, results=None):
        return self.content == node.value


class NodePattern(BasePattern):
    wildcards = False

    def __init__(self, type=None, content=None, name=None):
        if type is not None:
            pass
        if content is not None:
            content = list(content)
            for i, item in enumerate(content):
                if isinstance(item, WildcardPattern):
                    self.wildcards = True

        self.type = type
        self.content = content
        self.name = name
        return

    def _submatch(self, node, results=None):
        if self.wildcards:
            for c, r in generate_matches(self.content, node.children):
                if c == len(node.children):
                    if results is not None:
                        results.update(r)
                    return True

            return False
        elif len(self.content) != len(node.children):
            return False
        else:
            for subpattern, child in zip(self.content, node.children):
                if not subpattern.match(child, results):
                    return False

            return True


class WildcardPattern(BasePattern):

    def __init__(self, content=None, min=0, max=HUGE, name=None):
        if content is not None:
            content = tuple(map(tuple, content))
            for alt in content:
                pass

        self.content = content
        self.min = min
        self.max = max
        self.name = name
        return

    def optimize(self):
        subpattern = None
        if self.content is not None and len(self.content) == 1 and len(self.content[0]) == 1:
            subpattern = self.content[0][0]
        if self.min == 1 and self.max == 1:
            if self.content is None:
                return NodePattern(name=self.name)
            if subpattern is not None and self.name == subpattern.name:
                return subpattern.optimize()
        return WildcardPattern(subpattern.content, self.min * subpattern.min, self.max * subpattern.max, subpattern.name) if self.min <= 1 and isinstance(subpattern, WildcardPattern) and subpattern.min <= 1 and self.name == subpattern.name else self

    def match(self, node, results=None):
        return self.match_seq([node], results)

    def match_seq(self, nodes, results=None):
        for c, r in self.generate_matches(nodes):
            if c == len(nodes):
                if results is not None:
                    results.update(r)
                    if self.name:
                        results[self.name] = list(nodes)
                return True

        return False

    def generate_matches(self, nodes):
        if self.content is None:
            for count in xrange(self.min, 1 + min(len(nodes), self.max)):
                r = {}
                if self.name:
                    r[self.name] = nodes[:count]
                yield (count, r)

        elif self.name == 'bare_name':
            yield self._bare_name_matches(nodes)
        else:
            if hasattr(sys, 'getrefcount'):
                save_stderr = sys.stderr
                sys.stderr = StringIO()
            try:
                try:
                    for count, r in self._recursive_matches(nodes, 0):
                        if self.name:
                            r[self.name] = nodes[:count]
                        yield (count, r)

                except RuntimeError:
                    for count, r in self._iterative_matches(nodes):
                        if self.name:
                            r[self.name] = nodes[:count]
                        yield (count, r)

            finally:
                if hasattr(sys, 'getrefcount'):
                    sys.stderr = save_stderr

        return

    def _iterative_matches(self, nodes):
        nodelen = len(nodes)
        if 0 >= self.min:
            yield (0, {})
        results = []
        for alt in self.content:
            for c, r in generate_matches(alt, nodes):
                yield (c, r)
                results.append((c, r))

        while results:
            new_results = []
            for c0, r0 in results:
                if c0 < nodelen and c0 <= self.max:
                    for alt in self.content:
                        for c1, r1 in generate_matches(alt, nodes[c0:]):
                            if c1 > 0:
                                r = {}
                                r.update(r0)
                                r.update(r1)
                                yield (c0 + c1, r)
                                new_results.append((c0 + c1, r))

            results = new_results

    def _bare_name_matches(self, nodes):
        count = 0
        r = {}
        done = False
        max = len(nodes)
        while not done and count < max:
            done = True
            for leaf in self.content:
                if leaf[0].match(nodes[count], r):
                    count += 1
                    done = False
                    break

        r[self.name] = nodes[:count]
        return (count, r)

    def _recursive_matches(self, nodes, count):
        if count >= self.min:
            yield (0, {})
        if count < self.max:
            for alt in self.content:
                for c0, r0 in generate_matches(alt, nodes):
                    for c1, r1 in self._recursive_matches(nodes[c0:], count + 1):
                        r = {}
                        r.update(r0)
                        r.update(r1)
                        yield (c0 + c1, r)


class NegatedPattern(BasePattern):

    def __init__(self, content=None):
        if content is not None:
            pass
        self.content = content
        return

    def match(self, node):
        return False

    def match_seq(self, nodes):
        return len(nodes) == 0

    def generate_matches(self, nodes):
        if self.content is None:
            if len(nodes) == 0:
                yield (0, {})
        else:
            for c, r in self.content.generate_matches(nodes):
                return

            yield (0, {})
        return


def generate_matches(patterns, nodes):
    if not patterns:
        yield (0, {})
    else:
        p, rest = patterns[0], patterns[1:]
        for c0, r0 in p.generate_matches(nodes):
            if not rest:
                yield (c0, r0)
            for c1, r1 in generate_matches(rest, nodes[c0:]):
                r = {}
                r.update(r0)
                r.update(r1)
                yield (c0 + c1, r)
