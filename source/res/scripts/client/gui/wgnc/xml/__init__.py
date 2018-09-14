# Embedded file name: scripts/client/gui/wgnc/xml/__init__.py
import ResMgr
from gui.wgnc.errors import ParseError
from gui.wgnc.xml import actions_parsers, gui_parsers, shared_parsers

class _NotificationParser(shared_parsers.SectionParser):
    __slots__ = ('_actionsParser', '_guiParser')

    def __init__(self, actionsParser, guiParser):
        super(_NotificationParser, self).__init__()
        self._actionsParser = actionsParser
        self._guiParser = guiParser

    def getTagName(self):
        return 'notification'

    def parse(self, section):
        if section.name != self.getTagName():
            raise ParseError('Root tag "{0}" is invalid'.format(section.name))
        notifyID = section.readInt64('notification_id', 0L)
        if not notifyID:
            raise ParseError('Attribute "notification_id" is not valid.')
        ttl = section.readFloat('valid_till', 0.0)
        sub = section[self._actionsParser.getTagName()]
        if sub:
            actionsHolder = self._actionsParser.parse(sub)
        else:
            actionsHolder = None
        sub = section[self._guiParser.getTagName()]
        if sub:
            itemsHolder = self._guiParser.parse(sub)
        else:
            raise ParseError('The tag "gui" is empty.')
        return (notifyID,
         ttl,
         actionsHolder,
         itemsHolder)


_PARSER_BY_VER = {'2.0': (_NotificationParser, (actions_parsers.ActionsParser_v2, gui_parsers.GUIItemsParser_v2))}

def _parse(section):
    ver = section.readString('ver', '')
    if not ver:
        raise ParseError('Attribute "ver" is not valid.')
    if ver not in _PARSER_BY_VER:
        raise ParseError('That version {0} is not supported.'.format(ver))
    clazz, (actionsClazz, guiClazz) = _PARSER_BY_VER[ver]
    return clazz(actionsClazz(), guiClazz()).parse(section)


def fromString(xml):
    section = ResMgr.DataSection().createSectionFromString(xml)
    if not section:
        raise ParseError('Can not read notification')
    return _parse(section)


def fromSection(section):
    if not section:
        raise ParseError('Section is empty')
    return _parse(section)
