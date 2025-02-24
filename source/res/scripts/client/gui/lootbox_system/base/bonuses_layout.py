# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/lootbox_system/base/bonuses_layout.py
import copy
import functools
import logging
import ResMgr
from gui.impl.gen.view_models.views.lobby.lootbox_system.bonus_model import BonusRarity
from gui.lootbox_system.base.bonuses_layout_helpers import BonusesHelper
from gui.lootbox_system.base.common import BonusesLayoutAttrs, DEFAULT_EVENT_NAME
from helpers import dependency
from items import _xml
from skeletons.gui.game_control import ILootBoxSystemController
_logger = logging.getLogger(__name__)
_CONFIG_FILENAME = 'gui/lootbox_system_bonuses_layout.xml'
_MAIN_SECTION_NAME = 'core'
_DEFAULT_SECTION_NAME = 'default'
_LEAST_PRIORITY = 0
_DEFAULT_RARITY = BonusRarity.COMMON
_DEFAULT_VISIBILITY = True

class BonusesLayout(object):
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)

    def __init__(self):
        self.__storage = {}

    def init(self):
        self.__loadLayout()

    def fini(self):
        self.__storage.clear()

    def getPriority(self, eventName, bonus=None):
        return int(self.__getParameter(eventName, BonusesLayoutAttrs.PRIORITY, _LEAST_PRIORITY, bonus))

    def getRarity(self, eventName, bonus=None):
        return BonusRarity(self.__getParameter(eventName, BonusesLayoutAttrs.RARITY, _DEFAULT_RARITY, bonus))

    def getIsVisible(self, eventName, bonus=None):
        return bool(self.__getParameter(eventName, BonusesLayoutAttrs.VISIBILITY, _DEFAULT_VISIBILITY, bonus))

    def __getParameter(self, eventName, parameterType, default, bonus):
        eventName = eventName if eventName in self.__storage else DEFAULT_EVENT_NAME
        eventStorage = self.__storage.get(eventName, {})
        default = eventStorage.get(_DEFAULT_SECTION_NAME, {}).get(parameterType, default)
        if not bonus:
            return default
        else:
            bonusType = bonus.getName()
            if bonusType in eventStorage:
                value = BonusesHelper.getParameter(bonus, eventStorage[bonusType], parameterType)
                if value is not None:
                    return value
            return default

    def __loadLayout(self):
        if self.__storage:
            return
        else:
            rootSection = ResMgr.openSection(_CONFIG_FILENAME)
            if rootSection is None:
                _xml.raiseWrongXml(None, _CONFIG_FILENAME, 'can not open or read')
            mainStorage = _parseSections(rootSection, _MAIN_SECTION_NAME)
            for eventName in self.__lootBoxes.eventNames + [DEFAULT_EVENT_NAME]:
                self.__storage.setdefault(eventName, {})
                mergeDicts(self.__storage[eventName], mainStorage, _parseSections(rootSection, eventName))

            return


def mergeDicts(destination, first, second=None):
    sources = (first,) if second is None else (first, second)
    return functools.reduce(_mergeDicts, sources, destination)


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
        if sectionName == BonusesLayoutAttrs.RARITY:
            storage[name][sectionName] = item.asString
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
        if name == BonusesLayoutAttrs.RARITY:
            values[name] = item.asString
        if name == BonusesLayoutAttrs.VISIBILITY:
            values[name] = item.asBool
        if name == BonusesLayoutAttrs.ID:
            ids = item.asString

    names = ids.split(' ')
    for name in names:
        storage[name] = {}
        for key, value in values.iteritems():
            storage[name][key] = value


def _mergeDicts(destination, source):
    for key in source:
        if key in destination:
            dstValue, srcValue = destination[key], source[key]
            if isinstance(dstValue, dict) and isinstance(srcValue, dict):
                _mergeDicts(dstValue, srcValue)
                continue
            if type(dstValue) is type(srcValue):
                destination[key] = copy.deepcopy(srcValue)
        destination[key] = copy.deepcopy(source[key])

    return destination
