# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/rlcompleter.py
import __builtin__
import __main__
__all__ = ['Completer']

class Completer:

    def __init__(self, namespace=None):
        if namespace and not isinstance(namespace, dict):
            raise TypeError, 'namespace must be a dictionary'
        if namespace is None:
            self.use_main_ns = 1
        else:
            self.use_main_ns = 0
            self.namespace = namespace
        return

    def complete(self, text, state):
        if self.use_main_ns:
            self.namespace = __main__.__dict__
        if state == 0:
            if '.' in text:
                self.matches = self.attr_matches(text)
            else:
                self.matches = self.global_matches(text)
        try:
            return self.matches[state]
        except IndexError:
            return None

        return None

    def _callable_postfix(self, val, word):
        if hasattr(val, '__call__'):
            word = word + '('
        return word

    def global_matches(self, text):
        import keyword
        matches = []
        n = len(text)
        for word in keyword.kwlist:
            if word[:n] == text:
                matches.append(word)

        for nspace in [__builtin__.__dict__, self.namespace]:
            for word, val in nspace.items():
                if word[:n] == text and word != '__builtins__':
                    matches.append(self._callable_postfix(val, word))

        return matches

    def attr_matches(self, text):
        import re
        m = re.match('(\\w+(\\.\\w+)*)\\.(\\w*)', text)
        if not m:
            return []
        expr, attr = m.group(1, 3)
        try:
            thisobject = eval(expr, self.namespace)
        except Exception:
            return []

        words = dir(thisobject)
        if '__builtins__' in words:
            words.remove('__builtins__')
        if hasattr(thisobject, '__class__'):
            words.append('__class__')
            words.extend(get_class_members(thisobject.__class__))
        matches = []
        n = len(attr)
        for word in words:
            if word[:n] == attr and hasattr(thisobject, word):
                val = getattr(thisobject, word)
                word = self._callable_postfix(val, '%s.%s' % (expr, word))
                matches.append(word)

        return matches


def get_class_members(klass):
    ret = dir(klass)
    if hasattr(klass, '__bases__'):
        for base in klass.__bases__:
            ret = ret + get_class_members(base)

    return ret


try:
    import readline
except ImportError:
    pass
else:
    readline.set_completer(Completer().complete)
