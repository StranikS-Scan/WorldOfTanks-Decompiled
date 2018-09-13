# Embedded file name: scripts/common/xmpp/Parser.py
import xml.parsers.expat

class XMPPParser(object):

    def __init__(self):
        self.stanzaStream = []
        self.stanzaStack = []
        self.stanzaComplete = []
        self.parser = xml.parsers.expat.ParserCreate()
        self.parser.StartElementHandler = self.startElement
        self.parser.EndElementHandler = self.endElement
        self.parser.CharacterDataHandler = self.charData

    def newParser(self):
        self.parser = xml.parsers.expat.ParserCreate()
        self.parser.StartElementHandler = self.startElement
        self.parser.EndElementHandler = self.endElement
        self.parser.CharacterDataHandler = self.charData

    def fini(self):
        self.parser.StartElementHandler = None
        self.parser.EndElementHandler = None
        self.parser.CharacterDataHandler = None
        return

    def feedData(self, data):
        self.parser.Parse(data, 0)

    def pop(self):
        if len(self.stanzaComplete) == 0:
            return None
        else:
            return self.stanzaComplete.pop(0)
            return None

    def startElement(self, name, attr):
        if name == 'stream:stream':
            self.stanzaStream.append({'name': name,
             'attr': attr,
             'data': '',
             'children': []})
        else:
            self.stanzaStack.append({'name': name,
             'attr': attr,
             'data': '',
             'children': []})

    def endElement(self, name):
        if len(self.stanzaStack) > 1:
            self.stanzaStack[-2]['children'].append(self.stanzaStack[-1])
            self.stanzaStack.pop()
        elif len(self.stanzaStack) == 1:
            self.stanzaComplete.append(self.stanzaStack.pop())
        else:
            self.stanzaStream.pop()

    def charData(self, data):
        self.stanzaStack[-1]['data'] += data
