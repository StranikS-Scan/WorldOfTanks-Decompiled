# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/common/halloween_common/items/hw_artefacts.py
from items.artefacts import Equipment
from items.components import component_constants
from soft_exception import SoftException
from items import _xml

class EventEquipment(Equipment):
    __slots__ = ('durationSeconds', 'cooldownSeconds', 'reuseCount', 'activationWWSoundFeedback', 'deactivationWWSoundFeedback', 'soundNotificationActive')

    def __init__(self):
        super(EventEquipment, self).__init__()
        self.durationSeconds = component_constants.ZERO_FLOAT
        self.cooldownSeconds = component_constants.ZERO_FLOAT
        self.reuseCount = component_constants.ZERO_INT
        self.activationWWSoundFeedback = None
        self.deactivationWWSoundFeedback = None
        self.soundNotificationActive = None
        return

    def _readBasicConfig(self, xmlCtx, section):
        super(EventEquipment, self)._readBasicConfig(xmlCtx, section)
        self.activationWWSoundFeedback = _xml.readStringOrNone(xmlCtx, section, 'activationWWSoundFeedback')
        self.deactivationWWSoundFeedback = _xml.readStringOrNone(xmlCtx, section, 'deactivationWWSoundFeedback')
        self.soundNotificationActive = _xml.readStringOrNone(xmlCtx, section, 'soundNotificationActive')

    def _readConfig(self, xmlCtx, section):
        super(EventEquipment, self)._readConfig(xmlCtx, section)
        try:
            self.durationSeconds = _xml.readFloat(xmlCtx, section, 'durationSeconds')
            self.cooldownSeconds = _xml.readFloat(xmlCtx, section, 'cooldownSeconds')
            self.reuseCount = _xml.readInt(xmlCtx, section, 'reuseCount')
        except SoftException:
            pass


class BuffEquipment(EventEquipment):
    __slots__ = ('buffNames',)

    def __init__(self):
        super(BuffEquipment, self).__init__()
        self.buffNames = None
        return

    def _readConfig(self, xmlCtx, section):
        super(BuffEquipment, self)._readConfig(xmlCtx, section)
        self.buffNames = self._readBuffs(xmlCtx, section, 'buffs')

    @staticmethod
    def _readBuffs(xmlCtx, section, subsectionName):
        buffNames = _xml.readStringOrEmpty(xmlCtx, section, subsectionName).split()
        return frozenset(buffNames)


class SuperShell(BuffEquipment):
    __slots__ = ('shotsCount', 'ownerBuffNames', 'ownerDurationSeconds')

    def __init__(self):
        super(SuperShell, self).__init__()
        self.shotsCount = 1
        self.ownerBuffNames = None
        self.ownerDurationSeconds = component_constants.ZERO_FLOAT
        return

    def _readConfig(self, xmlCtx, section):
        super(SuperShell, self)._readConfig(xmlCtx, section)
        self.shotsCount = _xml.readInt(xmlCtx, section, 'shotsCount')
        self.ownerBuffNames = self._readBuffs(xmlCtx, section, 'ownerBuffs')
        self.ownerDurationSeconds = _xml.readFloat(xmlCtx, section, 'ownerDurationSeconds', component_constants.ZERO_FLOAT)


class HpRepairAndCrewHealEquipment(BuffEquipment):
    __slots__ = ('isInterruptable',)

    def __init__(self):
        super(HpRepairAndCrewHealEquipment, self).__init__()
        self.isInterruptable = False

    def _readConfig(self, xmlCtx, section):
        super(HpRepairAndCrewHealEquipment, self)._readConfig(xmlCtx, section)
        self.isInterruptable = _xml.readBool(xmlCtx, section, 'isInterruptable')
