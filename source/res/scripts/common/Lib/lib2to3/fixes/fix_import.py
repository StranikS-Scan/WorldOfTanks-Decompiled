# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/lib2to3/fixes/fix_import.py
from .. import fixer_base
from os.path import dirname, join, exists, sep
from ..fixer_util import FromImport, syms, token

def traverse_imports(names):
    pending = [names]
    while pending:
        node = pending.pop()
        if node.type == token.NAME:
            yield node.value
        if node.type == syms.dotted_name:
            yield ''.join([ ch.value for ch in node.children ])
        if node.type == syms.dotted_as_name:
            pending.append(node.children[0])
        if node.type == syms.dotted_as_names:
            pending.extend(node.children[::-2])
        raise AssertionError('unknown node type')


class FixImport(fixer_base.BaseFix):
    BM_compatible = True
    PATTERN = "\n    import_from< 'from' imp=any 'import' ['('] any [')'] >\n    |\n    import_name< 'import' imp=any >\n    "

    def start_tree(self, tree, name):
        super(FixImport, self).start_tree(tree, name)
        self.skip = 'absolute_import' in tree.future_features

    def transform(self, node, results):
        if self.skip:
            return
        imp = results['imp']
        if node.type == syms.import_from:
            while not hasattr(imp, 'value'):
                imp = imp.children[0]

            if self.probably_a_local_import(imp.value):
                imp.value = u'.' + imp.value
                imp.changed()
        else:
            have_local = False
            have_absolute = False
            for mod_name in traverse_imports(imp):
                if self.probably_a_local_import(mod_name):
                    have_local = True
                have_absolute = True

            if have_absolute:
                if have_local:
                    self.warning(node, 'absolute and local imports together')
                return
            new = FromImport(u'.', [imp])
            new.prefix = node.prefix
            return new

    def probably_a_local_import(self, imp_name):
        if imp_name.startswith(u'.'):
            return False
        imp_name = imp_name.split(u'.', 1)[0]
        base_path = dirname(self.filename)
        base_path = join(base_path, imp_name)
        if not exists(join(dirname(base_path), '__init__.py')):
            return False
        for ext in ['.py',
         sep,
         '.pyc',
         '.so',
         '.sl',
         '.pyd']:
            if exists(base_path + ext):
                return True

        return False
