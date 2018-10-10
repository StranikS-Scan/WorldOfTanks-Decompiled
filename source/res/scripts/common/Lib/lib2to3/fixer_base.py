# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/lib2to3/fixer_base.py
import logging
import itertools
from .patcomp import PatternCompiler
from . import pygram
from .fixer_util import does_tree_import

class BaseFix(object):
    PATTERN = None
    pattern = None
    pattern_tree = None
    options = None
    filename = None
    logger = None
    numbers = itertools.count(1)
    used_names = set()
    order = 'post'
    explicit = False
    run_order = 5
    _accept_type = None
    keep_line_order = False
    BM_compatible = False
    syms = pygram.python_symbols

    def __init__(self, options, log):
        self.options = options
        self.log = log
        self.compile_pattern()

    def compile_pattern(self):
        if self.PATTERN is not None:
            PC = PatternCompiler()
            self.pattern, self.pattern_tree = PC.compile_pattern(self.PATTERN, with_tree=True)
        return

    def set_filename(self, filename):
        self.filename = filename
        self.logger = logging.getLogger(filename)

    def match(self, node):
        results = {'node': node}
        return self.pattern.match(node, results) and results

    def transform(self, node, results):
        raise NotImplementedError()

    def new_name(self, template=u'xxx_todo_changeme'):
        name = template
        while name in self.used_names:
            name = template + unicode(self.numbers.next())

        self.used_names.add(name)
        return name

    def log_message(self, message):
        if self.first_log:
            self.first_log = False
            self.log.append('### In file %s ###' % self.filename)
        self.log.append(message)

    def cannot_convert(self, node, reason=None):
        lineno = node.get_lineno()
        for_output = node.clone()
        for_output.prefix = u''
        msg = 'Line %d: could not convert: %s'
        self.log_message(msg % (lineno, for_output))
        if reason:
            self.log_message(reason)

    def warning(self, node, reason):
        lineno = node.get_lineno()
        self.log_message('Line %d: %s' % (lineno, reason))

    def start_tree(self, tree, filename):
        self.used_names = tree.used_names
        self.set_filename(filename)
        self.numbers = itertools.count(1)
        self.first_log = True

    def finish_tree(self, tree, filename):
        pass


class ConditionalFix(BaseFix):
    skip_on = None

    def start_tree(self, *args):
        super(ConditionalFix, self).start_tree(*args)
        self._should_skip = None
        return

    def should_skip(self, node):
        if self._should_skip is not None:
            return self._should_skip
        else:
            pkg = self.skip_on.split('.')
            name = pkg[-1]
            pkg = '.'.join(pkg[:-1])
            self._should_skip = does_tree_import(pkg, name, node)
            return self._should_skip
