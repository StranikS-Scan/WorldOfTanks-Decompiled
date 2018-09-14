# Embedded file name: scripts/client/gui/wgnc/xml/shared_parsers.py
from debug_utils import LOG_WARNING
from gui.wgnc.errors import ParseError

class SectionParser(object):
    __slots__ = ()

    def getTagName(self):
        raise NotImplementedError

    def parse(self, section):
        raise NotImplementedError

    def _readString(self, name, section):
        value = section.readString(name, '')
        if not value:
            raise ParseError('The {0} of section "{1}" is not defined.'.format(name, self.getTagName()))
        return value


class ParsersCollection(SectionParser):
    __slots__ = ('_parsers',)

    def __init__(self, seq):
        super(ParsersCollection, self).__init__()
        self._parsers = dict(map(lambda parser: (parser.getTagName(), parser), seq))

    def clear(self):
        self._parsers.clear()

    def parse(self, section):
        for name, sub in section.items():
            if name in self._parsers:
                parser = self._parsers[name]
                yield parser.parse(sub)
            else:
                LOG_WARNING('Tag {0} is not supported. It is ignored.'.format(name))

    def _createResult(self):
        raise NotImplementedError
