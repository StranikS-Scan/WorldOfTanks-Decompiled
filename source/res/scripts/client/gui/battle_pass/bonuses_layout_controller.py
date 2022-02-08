# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/bonuses_layout_controller.py
import typing
import ResMgr
from items import _xml
from gui.battle_pass.battle_pass_bonuses_helper import BonusesHelper
from gui.battle_pass.battle_pass_constants import BonusesLayoutConsts
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import SimpleBonus
_PRIORITY_CONFIG_FILE = 'gui/battle_pass_bonuses_layout.xml'
_LEAST_PRIORITY_VALUE = 0
_DEFAULT_VISIBILITY = True
_DEFAULT_BIG_ICON = 'None'

class BonusesLayoutController(object):

    def __init__(self):
        self.__storage = {}
        self.__defaultPriority = _LEAST_PRIORITY_VALUE
        self.__defaultVisibility = _DEFAULT_VISIBILITY
        self.__defaultBigIcon = _DEFAULT_BIG_ICON

    def init(self):
        self.__loadLayout()

    def getPriority(self, bonus=None):
        if not bonus:
            return self.__defaultPriority
        else:
            bonusType = bonus.getName()
            if bonusType in self.__storage:
                value = BonusesHelper.getParameter(bonus, self.__storage[bonusType], BonusesLayoutConsts.PRIORITY_KEY)
                if value is not None:
                    return value
            return self.__defaultPriority

    def getIsVisible(self, bonus=None):
        if not bonus:
            return self.__defaultVisibility
        else:
            bonusType = bonus.getName()
            if bonusType in self.__storage:
                value = BonusesHelper.getParameter(bonus, self.__storage[bonusType], BonusesLayoutConsts.VISIBILITY_KEY)
                if value is not None:
                    return value
            return self.__defaultVisibility

    def getBigIcon(self, bonus=None):
        if not bonus:
            return self.__defaultBigIcon
        else:
            bonusType = bonus.getName()
            if bonusType in self.__storage:
                value = BonusesHelper.getParameter(bonus, self.__storage[bonusType], BonusesLayoutConsts.BIG_ICON_KEY)
                if value is not None:
                    return value
            return self.__defaultBigIcon

    def __loadLayout(self):
        if self.__storage:
            return
        else:
            section = ResMgr.openSection(_PRIORITY_CONFIG_FILE)
            if section is None:
                _xml.raiseWrongXml(None, _PRIORITY_CONFIG_FILE, 'can not open or read')
            if section.has_key('bonuses'):
                for name, item in section['bonuses'].items():
                    self.__parseSection(self.__storage, name, item)

                self.__defaultPriority = self.__storage.get('default', {}).get(BonusesLayoutConsts.PRIORITY_KEY, _LEAST_PRIORITY_VALUE)
                self.__defaultVisibility = self.__storage.get('default', {}).get(BonusesLayoutConsts.VISIBILITY_KEY, _DEFAULT_VISIBILITY)
                self.__defaultBigIcon = self.__storage.get('default', {}).get(BonusesLayoutConsts.BIG_ICON_KEY, _DEFAULT_BIG_ICON)
            ResMgr.purge(_PRIORITY_CONFIG_FILE, True)
            return

    @classmethod
    def __parseSection(cls, storage, name, section):
        storage[name] = {}
        for sectionName, item in section.items():
            if sectionName in BonusesLayoutConsts.MAIN_KEYS:
                if sectionName in BonusesLayoutConsts.INT_VALUES:
                    storage[name][sectionName] = item.asInt
                elif sectionName in BonusesLayoutConsts.BOOL_VALUES:
                    storage[name][sectionName] = item.asBool
                elif sectionName == BonusesLayoutConsts.BIG_ICON_KEY:
                    storage[name][sectionName] = item.asString
            if sectionName == BonusesLayoutConsts.OVERRIDE_KEY:
                cls.__parseOverride(storage[name], item)
            cls.__parseSection(storage[name], sectionName, item)

    @classmethod
    def __parseOverride(cls, storage, section):
        ids = ''
        values = {}
        for name, item in section.items():
            if name in BonusesLayoutConsts.MAIN_KEYS:
                if name in BonusesLayoutConsts.INT_VALUES:
                    values[name] = item.asInt
                elif name in BonusesLayoutConsts.BOOL_VALUES:
                    values[name] = item.asBool
                elif name == BonusesLayoutConsts.BIG_ICON_KEY:
                    values[name] = item.asString
            if name in (BonusesLayoutConsts.ID_KEY, BonusesLayoutConsts.LEVEL_KEY):
                ids = item.asString

        names = ids.split(' ')
        for name in names:
            storage[name] = {}
            for key, value in values.iteritems():
                storage[name][key] = value
