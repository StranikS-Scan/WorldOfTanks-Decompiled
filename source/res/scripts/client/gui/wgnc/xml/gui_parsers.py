# Embedded file name: scripts/client/gui/wgnc/xml/gui_parsers.py
from debug_utils import LOG_WARNING
from gui.wgnc.settings import WGNC_POP_UP_PRIORITIES
from gui.wgnc.xml.format_by_tags import formatText
from gui.wgnc.xml.shared_parsers import ParsersCollection, SectionParser
from gui.wgnc import gui_items

class _ButtonsParser(SectionParser):

    def getTagName(self):
        return 'buttons'

    def parse(self, section):
        result = []
        for name, sub in section.items():
            if name != 'button':
                continue
            label = sub.asString
            if not label:
                LOG_WARNING('Button section is not valid, label is empty', sub.asBinary)
                continue
            actions = sub.readString('actions')
            if not actions:
                LOG_WARNING('Button section is not valid, actions is empty', sub.asBinary)
                continue
            result.append((label, actions))

        return result


class _PopUpParser(SectionParser):

    def getTagName(self):
        return 'popup'

    def parse(self, section):
        body = formatText(self._readString('body', section))
        priority = self._readString('priority', section)
        if priority not in WGNC_POP_UP_PRIORITIES:
            LOG_WARNING('Priority of pop up is not valid, uses default priority', priority)
            priority = 'medium'
        topic = section.readString('topic', '')
        icon = section.readString('icon', '')
        bg = section.readString('bg', '')
        sub = _ButtonsParser()
        if sub.getTagName() in section.keys():
            buttons = sub.parse(section[sub.getTagName()])
        else:
            buttons = None
        return gui_items.PopUpItem(body, topic, priority, buttons, icon, bg)


class _WindowParser(SectionParser):
    __slots__ = ('_itemClass',)

    def __init__(self, itemClass = gui_items.WindowItem):
        super(_WindowParser, self).__init__()
        self._itemClass = itemClass

    def getTagName(self):
        return 'window'

    def parse(self, section):
        name = self._readString('name', section)
        body = formatText(self._readString('body', section))
        topic = section.readString('topic', '')
        isModal = section.readBool('modal', False)
        isHidden = section.readBool('hidden', True)
        sub = _ButtonsParser()
        if sub.getTagName() in section.keys():
            buttons = sub.parse(section[sub.getTagName()])
        else:
            buttons = None
        return self._itemClass(name, body, topic, buttons, isModal, isHidden)


class _ReferrerParser(SectionParser):

    def getTagName(self):
        return 'referrer'

    def parse(self, section):
        name = self._readString('name', section)
        return gui_items.ReferrerItem(name, section.readInt('invitations_count', False), section.readBool('hidden', True))


class _FenixParser(SectionParser):

    def getTagName(self):
        return 'fenix'

    def parse(self, section):
        name = self._readString('name', section)
        referrer = self._readString('name_referrer', section)
        return gui_items.ReferralItem(name, referrer, False, section.readBool('hidden', True))


class _RecruitParser(SectionParser):

    def getTagName(self):
        return 'recruit'

    def parse(self, section):
        name = self._readString('name', section)
        referrer = self._readString('name_referrer', section)
        return gui_items.ReferralItem(name, referrer, True, section.readBool('hidden', True))


class _PollParser(_WindowParser):

    def __init__(self, itemClass = gui_items.PollItem):
        super(_PollParser, self).__init__(itemClass)

    def getTagName(self):
        return 'poll'


class _GUIItemsParser(ParsersCollection):

    def getTagName(self):
        return 'gui'

    def parse(self, section):
        items = []
        for item in super(_GUIItemsParser, self).parse(section):
            items.append(item)

        return gui_items.GUIHolder(items)


class GUIItemsParser_v2(_GUIItemsParser):

    def __init__(self):
        super(GUIItemsParser_v2, self).__init__((_PopUpParser(),
         _WindowParser(),
         _ReferrerParser(),
         _ReferrerParser(),
         _FenixParser(),
         _RecruitParser(),
         _PollParser()))
