# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/lib2to3/fixes/fix_metaclass.py
from .. import fixer_base
from ..pygram import token
from ..fixer_util import Name, syms, Node, Leaf

def has_metaclass(parent):
    for node in parent.children:
        if node.type == syms.suite:
            return has_metaclass(node)
        if node.type == syms.simple_stmt and node.children:
            expr_node = node.children[0]
            if expr_node.type == syms.expr_stmt and expr_node.children:
                left_side = expr_node.children[0]
                if isinstance(left_side, Leaf) and left_side.value == '__metaclass__':
                    return True

    return False


def fixup_parse_tree(cls_node):
    for node in cls_node.children:
        if node.type == syms.suite:
            return

    for i, node in enumerate(cls_node.children):
        if node.type == token.COLON:
            break
    else:
        raise ValueError("No class suite and no ':'!")

    suite = Node(syms.suite, [])
    while cls_node.children[i + 1:]:
        move_node = cls_node.children[i + 1]
        suite.append_child(move_node.clone())
        move_node.remove()

    cls_node.append_child(suite)
    node = suite


def fixup_simple_stmt(parent, i, stmt_node):
    for semi_ind, node in enumerate(stmt_node.children):
        if node.type == token.SEMI:
            break
    else:
        return

    node.remove()
    new_expr = Node(syms.expr_stmt, [])
    new_stmt = Node(syms.simple_stmt, [new_expr])
    while stmt_node.children[semi_ind:]:
        move_node = stmt_node.children[semi_ind]
        new_expr.append_child(move_node.clone())
        move_node.remove()

    parent.insert_child(i, new_stmt)
    new_leaf1 = new_stmt.children[0].children[0]
    old_leaf1 = stmt_node.children[0].children[0]
    new_leaf1.prefix = old_leaf1.prefix


def remove_trailing_newline(node):
    if node.children and node.children[-1].type == token.NEWLINE:
        node.children[-1].remove()


def find_metas(cls_node):
    for node in cls_node.children:
        if node.type == syms.suite:
            break
    else:
        raise ValueError('No class suite!')

    for i, simple_node in list(enumerate(node.children)):
        if simple_node.type == syms.simple_stmt and simple_node.children:
            expr_node = simple_node.children[0]
            if expr_node.type == syms.expr_stmt and expr_node.children:
                left_node = expr_node.children[0]
                if isinstance(left_node, Leaf) and left_node.value == u'__metaclass__':
                    fixup_simple_stmt(node, i, simple_node)
                    remove_trailing_newline(simple_node)
                    yield (node, i, simple_node)


def fixup_indent(suite):
    kids = suite.children[::-1]
    while kids:
        node = kids.pop()
        if node.type == token.INDENT:
            break

    while kids:
        node = kids.pop()
        if isinstance(node, Leaf) and node.type != token.DEDENT:
            if node.prefix:
                node.prefix = u''
            return
        kids.extend(node.children[::-1])


class FixMetaclass(fixer_base.BaseFix):
    BM_compatible = True
    PATTERN = '\n    classdef<any*>\n    '

    def transform(self, node, results):
        if not has_metaclass(node):
            return
        else:
            fixup_parse_tree(node)
            last_metaclass = None
            for suite, i, stmt in find_metas(node):
                last_metaclass = stmt
                stmt.remove()

            text_type = node.children[0].type
            if len(node.children) == 7:
                if node.children[3].type == syms.arglist:
                    arglist = node.children[3]
                else:
                    parent = node.children[3].clone()
                    arglist = Node(syms.arglist, [parent])
                    node.set_child(3, arglist)
            elif len(node.children) == 6:
                arglist = Node(syms.arglist, [])
                node.insert_child(3, arglist)
            elif len(node.children) == 4:
                arglist = Node(syms.arglist, [])
                node.insert_child(2, Leaf(token.RPAR, u')'))
                node.insert_child(2, arglist)
                node.insert_child(2, Leaf(token.LPAR, u'('))
            else:
                raise ValueError('Unexpected class definition')
            meta_txt = last_metaclass.children[0].children[0]
            meta_txt.value = 'metaclass'
            orig_meta_prefix = meta_txt.prefix
            if arglist.children:
                arglist.append_child(Leaf(token.COMMA, u','))
                meta_txt.prefix = u' '
            else:
                meta_txt.prefix = u''
            expr_stmt = last_metaclass.children[0]
            expr_stmt.children[1].prefix = u''
            expr_stmt.children[2].prefix = u''
            arglist.append_child(last_metaclass)
            fixup_indent(suite)
            if not suite.children:
                suite.remove()
                pass_leaf = Leaf(text_type, u'pass')
                pass_leaf.prefix = orig_meta_prefix
                node.append_child(pass_leaf)
                node.append_child(Leaf(token.NEWLINE, u'\n'))
            elif len(suite.children) > 1 and suite.children[-2].type == token.INDENT and suite.children[-1].type == token.DEDENT:
                pass_leaf = Leaf(text_type, u'pass')
                suite.insert_child(-1, pass_leaf)
                suite.insert_child(-1, Leaf(token.NEWLINE, u'\n'))
            return
