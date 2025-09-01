# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/common/white_tiger_common/items/white_tiger_artefacts.py
from items.artefacts import VisualScriptEquipment
from items import _xml
from items.components import component_constants
from items.artefacts import Repairkit

class WTEquipment(VisualScriptEquipment):
    __slots__ = ('deploySeconds', 'consumeSeconds', 'soundPressedReady', 'soundPressedNotReady', 'soundPressedCancel')

    def __init__(self):
        super(WTEquipment, self).__init__()
        self.deploySeconds = component_constants.ZERO_INT
        self.consumeSeconds = component_constants.ZERO_INT
        self.soundPressedReady = None
        self.soundPressedNotReady = None
        self.soundPressedCancel = None
        return

    def _readBasicConfig(self, xmlCtx, section):
        super(WTEquipment, self)._readBasicConfig(xmlCtx, section)
        self.soundPressedReady = _xml.readStringOrNone(xmlCtx, section, 'soundPressedReady')
        self.soundPressedNotReady = _xml.readStringOrNone(xmlCtx, section, 'soundPressedNotReady')
        self.soundPressedCancel = _xml.readStringOrNone(xmlCtx, section, 'soundPressedCancel')
        scriptSection = section['script']
        if scriptSection:
            self.deploySeconds = _xml.readInt(xmlCtx, scriptSection, 'deploySeconds', minVal=0) if scriptSection.has_key('deploySeconds') else 0
            self.consumeSeconds = _xml.readInt(xmlCtx, scriptSection, 'consumeSeconds', minVal=0) if scriptSection.has_key('consumeSeconds') else 0


class WTRepairkit(Repairkit):
    __slots__ = ('soundPressedReady', 'soundPressedNotReady')

    def __init__(self):
        super(WTRepairkit, self).__init__()
        self.soundPressedReady = None
        self.soundPressedNotReady = None
        return

    def _readBasicConfig(self, xmlCtx, section):
        super(WTRepairkit, self)._readBasicConfig(xmlCtx, section)
        self.soundPressedReady = _xml.readStringOrNone(xmlCtx, section, 'soundPressedReady')
        self.soundPressedNotReady = _xml.readStringOrNone(xmlCtx, section, 'soundPressedNotReady')
