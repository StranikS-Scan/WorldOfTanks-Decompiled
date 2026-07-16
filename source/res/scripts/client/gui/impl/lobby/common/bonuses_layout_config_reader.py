# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/common/bonuses_layout_config_reader.py
from __future__ import absolute_import
from future.utils import viewitems
import ResMgr
from items import _xml
from gui.impl.lobby.common.bonuses_layout_helpers import BonusesLayoutHelper, BonusesLayoutAttrs
_LEAST_PRIORITY_VALUE = 0
_DEFAULT_VISIBILITY = True

class BonusesLayout(object):

    def __init__(self, configFile, subTypeGetter=None, valueGetter=None):
        self.__configFile = configFile
        self.__subTypeGetter = subTypeGetter
        self.__valueGetter = valueGetter
        self.__storage = {}

    def init(self):
        self.__loadLayout()

    def fini(self):
        self.__storage.clear()

    def getPriority(self, bonus=None):
        return int(self.__getParameter(BonusesLayoutAttrs.PRIORITY, _LEAST_PRIORITY_VALUE, bonus))

    def getIsVisible(self, bonus=None):
        return bool(self.__getParameter(BonusesLayoutAttrs.VISIBILITY, _DEFAULT_VISIBILITY, bonus))

    def _parseSections(self, section, name):
        storage = {}
        if section.has_key(name):
            for sectionName, item in section[name].items():
                self._parseSectionValues(storage, sectionName, item)

        return storage

    def _parseSectionValues(self, storage, name, section):
        storage[name] = {}
        for sectionName, item in section.items():
            if sectionName == BonusesLayoutAttrs.PRIORITY:
                storage[name][sectionName] = item.asInt
            if sectionName == BonusesLayoutAttrs.VISIBILITY:
                storage[name][sectionName] = item.asBool
            if sectionName == BonusesLayoutAttrs.OVERRIDE:
                self._parseOverride(storage[name], item)
            self._parseSectionValues(storage[name], sectionName, item)

    def _parseOverride(self, storage, section):
        ids = ''
        values = {}
        for name, item in section.items():
            if name == BonusesLayoutAttrs.PRIORITY:
                values[name] = item.asInt
            if name == BonusesLayoutAttrs.VISIBILITY:
                values[name] = item.asBool
            if name in (BonusesLayoutAttrs.ID, BonusesLayoutAttrs.RARITY):
                ids = item.asString

        names = ids.split(' ')
        for name in names:
            storage[name] = {}
            for key, value in viewitems(values):
                storage[name][key] = value

    def __loadLayout(self):
        if self.__storage:
            return
        else:
            rootSection = ResMgr.openSection(self.__configFile)
            if rootSection is None:
                _xml.raiseWrongXml(None, self.__configFile, 'can not open or read')
            self.__storage = self._parseSections(rootSection, BonusesLayoutAttrs.BONUSES)
            return

    def __getParameter(self, parameterType, default, bonus):
        default = self.__storage.get(BonusesLayoutAttrs.DEFAULT, {}).get(parameterType, default)
        if bonus is None:
            return default
        else:
            bonusType = bonus.getName()
            if bonusType in self.__storage:
                value = BonusesLayoutHelper.getParameter(bonus, self.__storage[bonusType], parameterType, self.__subTypeGetter, self.__valueGetter)
                if value is not None:
                    return value
            return default
