# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/lib2to3/fixer_util.py
from itertools import islice
from .pgen2 import token
from .pytree import Leaf, Node
from .pygram import python_symbols as syms
from . import patcomp

def KeywordArg(keyword, value):
    return Node(syms.argument, [keyword, Leaf(token.EQUAL, u'='), value])


def LParen():
    return Leaf(token.LPAR, u'(')


def RParen():
    return Leaf(token.RPAR, u')')


def Assign(target, source):
    if not isinstance(target, list):
        target = [target]
    if not isinstance(source, list):
        source.prefix = u' '
        source = [source]
    return Node(syms.atom, target + [Leaf(token.EQUAL, u'=', prefix=u' ')] + source)


def Name(name, prefix=None):
    return Leaf(token.NAME, name, prefix=prefix)


def Attr(obj, attr):
    return [obj, Node(syms.trailer, [Dot(), attr])]


def Comma():
    return Leaf(token.COMMA, u',')


def Dot():
    return Leaf(token.DOT, u'.')


def ArgList(args, lparen=LParen(), rparen=RParen()):
    node = Node(syms.trailer, [lparen.clone(), rparen.clone()])
    if args:
        node.insert_child(1, Node(syms.arglist, args))
    return node


def Call(func_name, args=None, prefix=None):
    node = Node(syms.power, [func_name, ArgList(args)])
    if prefix is not None:
        node.prefix = prefix
    return node


def Newline():
    return Leaf(token.NEWLINE, u'\n')


def BlankLine():
    return Leaf(token.NEWLINE, u'')


def Number(n, prefix=None):
    return Leaf(token.NUMBER, n, prefix=prefix)


def Subscript(index_node):
    return Node(syms.trailer, [Leaf(token.LBRACE, u'['), index_node, Leaf(token.RBRACE, u']')])


def String(string, prefix=None):
    return Leaf(token.STRING, string, prefix=prefix)


def ListComp(xp, fp, it, test=None):
    xp.prefix = u''
    fp.prefix = u' '
    it.prefix = u' '
    for_leaf = Leaf(token.NAME, u'for')
    for_leaf.prefix = u' '
    in_leaf = Leaf(token.NAME, u'in')
    in_leaf.prefix = u' '
    inner_args = [for_leaf,
     fp,
     in_leaf,
     it]
    if test:
        test.prefix = u' '
        if_leaf = Leaf(token.NAME, u'if')
        if_leaf.prefix = u' '
        inner_args.append(Node(syms.comp_if, [if_leaf, test]))
    inner = Node(syms.listmaker, [xp, Node(syms.comp_for, inner_args)])
    return Node(syms.atom, [Leaf(token.LBRACE, u'['), inner, Leaf(token.RBRACE, u']')])


def FromImport(package_name, name_leafs):
    for leaf in name_leafs:
        leaf.remove()

    children = [Leaf(token.NAME, u'from'),
     Leaf(token.NAME, package_name, prefix=u' '),
     Leaf(token.NAME, u'import', prefix=u' '),
     Node(syms.import_as_names, name_leafs)]
    imp = Node(syms.import_from, children)
    return imp


def is_tuple(node):
    return True if isinstance(node, Node) and node.children == [LParen(), RParen()] else isinstance(node, Node) and len(node.children) == 3 and isinstance(node.children[0], Leaf) and isinstance(node.children[1], Node) and isinstance(node.children[2], Leaf) and node.children[0].value == u'(' and node.children[2].value == u')'


def is_list(node):
    return isinstance(node, Node) and len(node.children) > 1 and isinstance(node.children[0], Leaf) and isinstance(node.children[-1], Leaf) and node.children[0].value == u'[' and node.children[-1].value == u']'


def parenthesize(node):
    return Node(syms.atom, [LParen(), node, RParen()])


consuming_calls = set(['sorted',
 'list',
 'set',
 'any',
 'all',
 'tuple',
 'sum',
 'min',
 'max',
 'enumerate'])

def attr_chain(obj, attr):
    next = getattr(obj, attr)
    while next:
        yield next
        next = getattr(next, attr)


p0 = "for_stmt< 'for' any 'in' node=any ':' any* >\n        | comp_for< 'for' any 'in' node=any any* >\n     "
p1 = "\npower<\n    ( 'iter' | 'list' | 'tuple' | 'sorted' | 'set' | 'sum' |\n      'any' | 'all' | 'enumerate' | (any* trailer< '.' 'join' >) )\n    trailer< '(' node=any ')' >\n    any*\n>\n"
p2 = "\npower<\n    ( 'sorted' | 'enumerate' )\n    trailer< '(' arglist<node=any any*> ')' >\n    any*\n>\n"
pats_built = False

def in_special_context(node):
    global p2
    global p0
    global p1
    global pats_built
    if not pats_built:
        p0 = patcomp.compile_pattern(p0)
        p1 = patcomp.compile_pattern(p1)
        p2 = patcomp.compile_pattern(p2)
        pats_built = True
    patterns = [p0, p1, p2]
    for pattern, parent in zip(patterns, attr_chain(node, 'parent')):
        results = {}
        if pattern.match(parent, results) and results['node'] is node:
            return True

    return False


def is_probably_builtin(node):
    prev = node.prev_sibling
    if prev is not None and prev.type == token.DOT:
        return False
    parent = node.parent
    if parent.type in (syms.funcdef, syms.classdef):
        return False
    elif parent.type == syms.expr_stmt and parent.children[0] is node:
        return False
    else:
        return False if parent.type == syms.parameters or parent.type == syms.typedargslist and (prev is not None and prev.type == token.COMMA or parent.children[0] is node) else True


def find_indentation(node):
    while node is not None:
        if node.type == syms.suite and len(node.children) > 2:
            indent = node.children[1]
            if indent.type == token.INDENT:
                return indent.value
        node = node.parent

    return u''


def make_suite(node):
    if node.type == syms.suite:
        return node
    else:
        node = node.clone()
        parent, node.parent = node.parent, None
        suite = Node(syms.suite, [node])
        suite.parent = parent
        return suite


def find_root(node):
    while node.type != syms.file_input:
        node = node.parent
        if not node:
            raise ValueError('root found before file_input node was found.')

    return node


def does_tree_import(package, name, node):
    binding = find_binding(name, find_root(node), package)
    return bool(binding)


def is_import(node):
    return node.type in (syms.import_name, syms.import_from)


def touch_import(package, name, node):

    def is_import_stmt(node):
        return node.type == syms.simple_stmt and node.children and is_import(node.children[0])

    root = find_root(node)
    if does_tree_import(package, name, root):
        return
    else:
        insert_pos = offset = 0
        for idx, node in enumerate(root.children):
            if not is_import_stmt(node):
                continue
            for offset, node2 in enumerate(root.children[idx:]):
                if not is_import_stmt(node2):
                    break

            insert_pos = idx + offset
            break

        if insert_pos == 0:
            for idx, node in enumerate(root.children):
                if node.type == syms.simple_stmt and node.children and node.children[0].type == token.STRING:
                    insert_pos = idx + 1
                    break

        if package is None:
            import_ = Node(syms.import_name, [Leaf(token.NAME, u'import'), Leaf(token.NAME, name, prefix=u' ')])
        else:
            import_ = FromImport(package, [Leaf(token.NAME, name, prefix=u' ')])
        children = [import_, Newline()]
        root.insert_child(insert_pos, Node(syms.simple_stmt, children))
        return


_def_syms = set([syms.classdef, syms.funcdef])

def find_binding(name, node, package=None):
    for child in node.children:
        ret = None
        if child.type == syms.for_stmt:
            if _find(name, child.children[1]):
                return child
            n = find_binding(name, make_suite(child.children[-1]), package)
            if n:
                ret = n
        elif child.type in (syms.if_stmt, syms.while_stmt):
            n = find_binding(name, make_suite(child.children[-1]), package)
            if n:
                ret = n
        elif child.type == syms.try_stmt:
            n = find_binding(name, make_suite(child.children[2]), package)
            if n:
                ret = n
            else:
                for i, kid in enumerate(child.children[3:]):
                    if kid.type == token.COLON and kid.value == ':':
                        n = find_binding(name, make_suite(child.children[i + 4]), package)
                        if n:
                            ret = n

        elif child.type in _def_syms and child.children[1].value == name:
            ret = child
        elif _is_import_binding(child, name, package):
            ret = child
        elif child.type == syms.simple_stmt:
            ret = find_binding(name, child, package)
        elif child.type == syms.expr_stmt:
            if _find(name, child.children[0]):
                ret = child
        if ret:
            if not package:
                return ret
            if is_import(ret):
                return ret

    return


_block_syms = set([syms.funcdef, syms.classdef, syms.trailer])

def _find(name, node):
    nodes = [node]
    while nodes:
        node = nodes.pop()
        if node.type > 256 and node.type not in _block_syms:
            nodes.extend(node.children)
        if node.type == token.NAME and node.value == name:
            return node

    return None


def _is_import_binding(node, name, package=None):
    if node.type == syms.import_name and not package:
        imp = node.children[1]
        if imp.type == syms.dotted_as_names:
            for child in imp.children:
                if child.type == syms.dotted_as_name:
                    if child.children[2].value == name:
                        return node
                if child.type == token.NAME and child.value == name:
                    return node

        elif imp.type == syms.dotted_as_name:
            last = imp.children[-1]
            if last.type == token.NAME and last.value == name:
                return node
        elif imp.type == token.NAME and imp.value == name:
            return node
    elif node.type == syms.import_from:
        if package and unicode(node.children[1]).strip() != package:
            return None
        n = node.children[3]
        if package and _find(u'as', n):
            return None
        if n.type == syms.import_as_names and _find(name, n):
            return node
        if n.type == syms.import_as_name:
            child = n.children[2]
            if child.type == token.NAME and child.value == name:
                return node
        else:
            if n.type == token.NAME and n.value == name:
                return node
            if package and n.type == token.STAR:
                return node
    return None
