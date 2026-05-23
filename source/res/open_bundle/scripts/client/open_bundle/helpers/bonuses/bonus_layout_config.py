# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/helpers/bonuses/bonus_layout_config.py
from __future__ import absolute_import
import ResMgr
from future.utils import viewitems
from items import _xml
from open_bundle.helpers.bonuses.bonuses_constants import BonusesLayoutAttrs
from open_bundle.helpers.bonuses.bonuses_layout_helper import BonusesHelper
_PRIORITY_CONFIG_FILE = 'open_bundle/gui/bonuses_layout.xml'
_LEAST_PRIORITY_VALUE = 0
_DEFAULT_VISIBILITY = True

class BonusLayoutConfig(object):

    def __init__(self):
        self.__storage = {}

    def init(self):
        self.__loadLayout()

    def clear(self):
        self.__storage.clear()

    def getPriority(self, bonus=None):
        return int(self.__getParameter(BonusesLayoutAttrs.PRIORITY, _LEAST_PRIORITY_VALUE, bonus))

    def getIsVisible(self, bonus=None):
        return bool(self.__getParameter(BonusesLayoutAttrs.VISIBILITY, _DEFAULT_VISIBILITY, bonus))

    def __getParameter(self, parameterType, default, bonus):
        default = self.__storage.get(BonusesLayoutAttrs.DEFAULT, {}).get(parameterType, default)
        if not bonus:
            return default
        else:
            bonusType = bonus.getName()
            if bonusType in self.__storage:
                value = BonusesHelper.getParameter(bonus, self.__storage[bonusType], parameterType)
                if value is not None:
                    return value
            return default

    def __loadLayout(self):
        if self.__storage:
            return
        else:
            rootSection = ResMgr.openSection(_PRIORITY_CONFIG_FILE)
            if rootSection is None:
                _xml.raiseWrongXml(None, _PRIORITY_CONFIG_FILE, 'can not open or read')
            self.__storage = _parseSections(rootSection, BonusesLayoutAttrs.BONUSES)
            return


def _parseSections(section, name):
    storage = {}
    if section.has_key(name):
        for sectionName, item in section[name].items():
            _parseSectionValues(storage, sectionName, item)

    return storage


def _parseSectionValues(storage, name, section):
    storage[name] = {}
    for sectionName, item in section.items():
        if sectionName == BonusesLayoutAttrs.PRIORITY:
            storage[name][sectionName] = item.asInt
        if sectionName == BonusesLayoutAttrs.VISIBILITY:
            storage[name][sectionName] = item.asBool
        if sectionName == BonusesLayoutAttrs.OVERRIDE:
            _parseOverride(storage[name], item)
        _parseSectionValues(storage[name], sectionName, item)


def _parseOverride(storage, section):
    ids = ''
    values = {}
    for name, item in section.items():
        if name == BonusesLayoutAttrs.PRIORITY:
            values[name] = item.asInt
        if name == BonusesLayoutAttrs.VISIBILITY:
            values[name] = item.asBool
        if name == BonusesLayoutAttrs.ID:
            ids = item.asString

    names = ids.split(' ')
    for name in names:
        storage[name] = {}
        for key, value in viewitems(values):
            storage[name][key] = value
