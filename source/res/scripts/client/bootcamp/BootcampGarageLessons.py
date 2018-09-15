# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/BootcampGarageLessons.py
from debug_utils_bootcamp import LOG_CURRENT_EXCEPTION_BOOTCAMP
from helpers import dependency
from skeletons.gui.game_control import IBootcampController
from skeletons.gui.shared import IItemsCache
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from nations import NAMES as NATION_NAMES
from ResMgr import openSection
XML_LESSONS_PATH = 'scripts/bootcamp_docs/garage_lessons/lessons.xml'
XML_CONDITIONS_PATH = 'scripts/bootcamp_docs/garage_lessons/conditions.xml'
XML_BATTLE_RESULTS_PATH = 'scripts/bootcamp_docs/garage_lessons/battle_results.xml'
actionConfigsXML = ['scripts/bootcamp_docs/garage_lessons/message_actions.xml',
 'scripts/bootcamp_docs/garage_lessons/highlight_button_actions.xml',
 'scripts/bootcamp_docs/garage_lessons/init_actions.xml',
 'scripts/bootcamp_docs/garage_lessons/show_actions.xml',
 'scripts/bootcamp_docs/garage_lessons/callback_actions.xml']

class _FillStruct(object):

    def __init__(self, key, vtype, funcs=None, default=None):
        self._key = key
        self._vtype = vtype
        funcs = funcs or []
        if not isinstance(funcs, list):
            funcs = [funcs]
        self._funcs = funcs
        self._default = default

    def __call__(self, section, container):
        if section.has_key(self._key):
            container[self._key] = self._vtype()
            for func in self._funcs:
                func(section[self._key], container[self._key])

        elif self._default is not None:
            container[self._key] = self._default
        return


class _FillValue(_FillStruct):

    def __call__(self, section, container):
        if section.has_key(self._key):
            container[self._key] = getattr(section[self._key], self._vtype)
            for func in self._funcs:
                func(section[self._key], container[self._key])

        elif self._default is not None:
            container[self._key] = self._default
        return


class ACTION_PARAM:
    ID = 'id'
    NAME = 'name'
    PRESET = 'preset'
    ICON = 'icon'
    LABEL = 'label'
    TEXT = 'text'
    NATIONS = 'nations'
    NATIONS_DATA = 'nations_data'
    NATION = 'nation'
    NATION_ID = 'nation_id'
    BACKGROUND = 'background'
    BOTTOM_RENDERER = 'bottom_renderer'
    EXTRA = 'extra'
    EXTRA_TEXT = 'extraText'
    EXTRA_ICON = 'extraIcon'
    EXTRA_TEXT_BODY = 'text'
    EXTRA_TEXT_ID = 'id'
    ELEMENT = 'element'
    VISIBLE = 'visible'
    SHOW = 'show'
    PREV_HINT = 'prev_hint'
    NEXT_HINT = 'next_hint'
    CALLBACK = 'callback'
    CONDITIONAL_ACTION = 'conditional_action'
    SAVE = 'save'
    FORCE = 'force'
    ONLY_FIRST_BOOTCAMP = 'only_first_bootcamp'
    ONLY_FIRST_BOOTCAMP_BOTTOM = 'only_first_bootcamp_bottom'


class LESSON_PARAM:
    LESSON_ID = 'id'
    ACTION_START = 'action_start'
    ACTION_FINISH = 'action_finish'


def readConfigFile(path):
    config = openSection(path)
    if config is None:
        raise Exception("Can't open config file (%s)" % path)
    return config


class GarageLessons:

    def __init__(self):
        self.__lessons = {}
        self.__battleResults = {}
        self.readLessonsFile(XML_LESSONS_PATH)
        self.readBattleResultsFile(XML_BATTLE_RESULTS_PATH)

    def getLesson(self, lessonId):
        try:
            if lessonId in self.__lessons:
                return self.__lessons[lessonId]
            raise Exception('Lesson not found - {0}.'.format(lessonId))
        except:
            LOG_CURRENT_EXCEPTION_BOOTCAMP()
            raise

    def getBattleResult(self, lessonId):
        if lessonId in self.__battleResults:
            return self.__battleResults[lessonId]
        raise Exception('Battle results not found. Lesson - {0}.'.format(lessonId))

    def readLessonsFile(self, path):
        lessonsConfig = readConfigFile(path)
        for name, section in lessonsConfig.items():
            if name == 'lesson':
                lesson_id = section[LESSON_PARAM.LESSON_ID].asInt
                self.__lessons[lesson_id] = {}
                self.__lessons[lesson_id][LESSON_PARAM.ACTION_START] = section[LESSON_PARAM.ACTION_START].asString
                self.__lessons[lesson_id][LESSON_PARAM.ACTION_FINISH] = section[LESSON_PARAM.ACTION_FINISH].asString

    def readBattleResultsData(self, datas, section):
        for dataName, dataSection in section.items():
            dataSectionDict = {}
            _FillValue('id', 'asString', default='')(dataSection, dataSectionDict)
            _FillValue('label', 'asString', default='')(dataSection, dataSectionDict)
            _FillValue('description', 'asString', default='')(dataSection, dataSectionDict)
            _FillValue('icon', 'asString')(dataSection, dataSectionDict)
            _FillValue('iconTooltip', 'asString')(dataSection, dataSectionDict)
            datas.append(dataSectionDict)

    def readBattleResultsFile(self, path):
        resultsConfig = readConfigFile(path)
        for name, section in resultsConfig.items():
            if name == 'lesson':
                lesson_id = section[LESSON_PARAM.LESSON_ID].asInt
                currentBattle = self.__battleResults[lesson_id] = {}
                medals = currentBattle['medals'] = []
                unlocks = currentBattle['unlocks'] = []
                self.readBattleResultsData(medals, section['medals'])
                self.readBattleResultsData(unlocks, section['unlocks'])


class GarageActions:
    bootcampCtrl = dependency.descriptor(IBootcampController)

    def __init__(self):
        self.__conditions = {}
        self.readConditionsFile(XML_CONDITIONS_PATH)
        self.__actions = {}
        for actionConfig in actionConfigsXML:
            self.parseXML(actionConfig)

    def getAction(self, actionName):
        try:
            if actionName in self.__actions:
                return self.__actions[actionName]
            raise Exception('Action not found - {0}.'.format(actionName))
        except:
            LOG_CURRENT_EXCEPTION_BOOTCAMP()
            raise

    def readMessageNationData(self, nationSection, currentAction):
        currentNation = {}
        default_nation = NATION_NAMES[self.bootcampCtrl.nation]
        _FillValue(ACTION_PARAM.NATION_ID, 'asString', default=default_nation)(nationSection, currentNation)
        _FillValue(ACTION_PARAM.PRESET, 'asString', default='')(nationSection, currentNation)
        _FillValue(ACTION_PARAM.ICON, 'asString', default='')(nationSection, currentNation)
        _FillValue(ACTION_PARAM.LABEL, 'asString', default='')(nationSection, currentNation)
        _FillValue(ACTION_PARAM.TEXT, 'asString', default='')(nationSection, currentNation)
        _FillValue(ACTION_PARAM.BACKGROUND, 'asString', default='')(nationSection, currentNation)
        _FillValue(ACTION_PARAM.BOTTOM_RENDERER, 'asInt', default=-1)(nationSection, currentNation)
        currentNation['bottom'] = []
        if currentNation[ACTION_PARAM.BOTTOM_RENDERER] != -1:
            for name, dataSection in nationSection['bottom'].items():
                if name == 'data':
                    currentData = {}
                    _FillValue('icon', 'asString', default='')(dataSection, currentData)
                    _FillValue('label', 'asString', default='')(dataSection, currentData)
                    _FillValue('label_format', 'asString', default=None)(dataSection, currentData)
                    _FillValue('description', 'asString', default='')(dataSection, currentData)
                    _FillValue('description_format', 'asString', default=None)(dataSection, currentData)
                    _FillValue('content_data', 'asString', default='')(dataSection, currentData)
                    _FillValue('content_renderer', 'asString', default='')(dataSection, currentData)
                    _FillValue('iconTooltip', 'asString', default='')(dataSection, currentData)
                    _FillValue('labelTooltip', 'asString', default='')(dataSection, currentData)
                    currentNation['bottom'].append(currentData)

        currentAction[ACTION_PARAM.NATIONS_DATA][currentNation[ACTION_PARAM.NATION_ID]] = currentNation
        return

    def parseXML(self, path):
        configXML = readConfigFile(path)
        for name, actionSection in configXML.items():
            if name == 'action':
                actionName = actionSection[ACTION_PARAM.NAME].asString
                currentAction = self.__actions[actionName] = {}
                currentAction[ACTION_PARAM.NAME] = actionName
                _FillValue(ACTION_PARAM.VISIBLE, 'asString')(actionSection, currentAction)
                if actionName.startswith('msg'):
                    _FillValue(ACTION_PARAM.NATIONS, 'asString', default=False)(actionSection, currentAction)
                    currentAction[ACTION_PARAM.NATIONS_DATA] = {}
                    if currentAction[ACTION_PARAM.NATIONS]:
                        for sectionName, nationSection in actionSection.items():
                            if sectionName == ACTION_PARAM.NATION:
                                self.readMessageNationData(nationSection, currentAction)

                    else:
                        self.readMessageNationData(actionSection, currentAction)
                _FillValue(ACTION_PARAM.SHOW, 'asString')(actionSection, currentAction)
                _FillValue(ACTION_PARAM.ELEMENT, 'asString')(actionSection, currentAction)
                _FillValue(ACTION_PARAM.PREV_HINT, 'asString')(actionSection, currentAction)
                _FillValue(ACTION_PARAM.NEXT_HINT, 'asString')(actionSection, currentAction)
                _FillValue(ACTION_PARAM.CALLBACK, 'asString')(actionSection, currentAction)
                _FillValue(ACTION_PARAM.CONDITIONAL_ACTION, 'asString')(actionSection, currentAction)
                _FillValue(ACTION_PARAM.SAVE, 'asBool', default=False)(actionSection, currentAction)
                _FillValue(ACTION_PARAM.ONLY_FIRST_BOOTCAMP, 'asBool', default=False)(actionSection, currentAction)
                _FillValue(ACTION_PARAM.ONLY_FIRST_BOOTCAMP_BOTTOM, 'asBool', default=False)(actionSection, currentAction)
                _FillValue(ACTION_PARAM.FORCE, 'asBool', default=False)(actionSection, currentAction)
                if actionSection.has_key('show_condition'):
                    showConditionSection = actionSection['show_condition']
                    showCondition = currentAction['show_condition'] = {}
                    _FillValue('view', 'asString')(showConditionSection, showCondition)
                    _FillValue('name', 'asString')(showConditionSection, showCondition)
                    _FillValue('result', 'asBool')(showConditionSection, showCondition)
                    _FillValue('prevHint', 'asString')(showConditionSection, showCondition)
                    showCondition['views'] = showCondition['view'].split(',')
                    conditionName = showCondition['name']
                    if conditionName in self.__conditions:
                        condition = self.__conditions[conditionName]
                        showCondition['condition'] = ConditionFactory(condition)

    def readConditionsFile(self, path):
        conditionsConfig = readConfigFile(path)
        for name, section in conditionsConfig.items():
            if name == 'condition':
                conditionName = section['name'].asString
                currentCondition = self.__conditions[conditionName] = {}
                currentCondition['name'] = conditionName
                _FillValue('type', 'asString')(section, currentCondition)
                _FillValue('state', 'asString')(section, currentCondition)
                _FillValue('vehicle', 'asString', default=None)(section, currentCondition)

        return


class Condition(object):
    types = []

    def __init__(self, conditionDict):
        self._conditionDict = conditionDict

    def checkCondition(self, nationData):
        pass

    def recheckOnItemSync(self):
        return False


class Module(Condition):

    def checkCondition(self, nationData):
        vehicleAlias = self._conditionDict['vehicle']
        vehicleCD = nationData[vehicleAlias]
        itemsCache = dependency.instance(IItemsCache)
        vehicle = itemsCache.items.getItemByCD(vehicleCD)
        vehInvID = vehicle.invID
        if vehInvID == -1:
            return False
        state = self._conditionDict['state']
        if state == 'unlock':
            vehicle = itemsCache.items.getVehicle(vehInvID)
            unlocks = itemsCache.items.stats.unlocks
            unlockedItemsGetter = g_techTreeDP.getUnlockedVehicleItems(vehicle, unlocks)
            return nationData['module'] in unlockedItemsGetter
        if state == 'inventory':
            vehicle = itemsCache.items.getVehicle(vehInvID)
            item = itemsCache.items.getItemByCD(nationData['module'])
            return item.isInstalled(vehicle)
        return False


class Vehicle(Condition):

    def checkCondition(self, nationData):
        itemsCache = dependency.instance(IItemsCache)
        vehicleAlias = self._conditionDict['vehicle']
        vehicleCD = nationData[vehicleAlias]
        state = self._conditionDict['state']
        vehicle = itemsCache.items.getItemByCD(vehicleCD)
        if state == 'unlock':
            return vehicle.isUnlocked
        return vehicle.invID != -1 if state == 'inventory' else False


class Perk(Condition):

    def checkCondition(self, nationData):
        vehicleAlias = self._conditionDict['vehicle']
        vehicleCD = nationData[vehicleAlias]
        state = self._conditionDict['state']
        itemsCache = dependency.instance(IItemsCache)
        vehicle = itemsCache.items.getItemByCD(vehicleCD)
        if vehicle.invID == -1:
            return False
        if state == 'skills':
            searchPerk = nationData['perk']
            for slotIdx, tman in vehicle.crew:
                if tman.isInTank and tman.vehicleInvID != vehicle.invID:
                    continue
                if tman.descriptor.role == 'commander':
                    for skill in tman.skills:
                        if skill.name == searchPerk:
                            return True

            return False


class Consumable(Condition):

    def checkCondition(self, nationData):
        vehicleAlias = self._conditionDict['vehicle']
        vehicleCD = nationData[vehicleAlias]
        state = self._conditionDict['state']
        itemsCache = dependency.instance(IItemsCache)
        vehicle = itemsCache.items.getItemByCD(vehicleCD)
        if vehicle.invID == -1:
            return False
        else:
            if state == 'inventory':
                consumables = vehicle.equipment.regularConsumables
                for eq in consumables:
                    if eq is not None:
                        return True

            return False

    def recheckOnItemSync(self):
        return True


class Equipment(Condition):

    def checkCondition(self, nationData):
        vehicleAlias = self._conditionDict['vehicle']
        vehicleCD = nationData[vehicleAlias]
        state = self._conditionDict['state']
        itemsCache = dependency.instance(IItemsCache)
        vehicle = itemsCache.items.getItemByCD(vehicleCD)
        if vehicle.invID == -1:
            return False
        else:
            if state == 'inventory':
                optionalDevices = vehicle.descriptor.optionalDevices
                searchEquipment = nationData['equipment']
                for device in optionalDevices:
                    if device is not None and device.compactDescr == searchEquipment:
                        return True

            return False


class BattleType(Condition):

    def checkCondition(self, nationData):
        vehicleAlias = self._conditionDict['vehicle']
        vehicleCD = nationData[vehicleAlias]
        state = self._conditionDict['state']
        itemsCache = dependency.instance(IItemsCache)
        vehicle = itemsCache.items.getItemByCD(vehicleCD)
        if vehicle.invID == -1:
            return False
        if state == 'menu':
            from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
            try:
                items = battle_selector_items.getItems()
                if items.isSelected('random'):
                    return True
            except:
                return False

        return False


class HasView(Condition):
    bootcampCtrl = dependency.descriptor(IBootcampController)

    def checkCondition(self, nationData):
        vehicleAlias = self._conditionDict['vehicle']
        vehicleCD = nationData[vehicleAlias]
        state = self._conditionDict['state']
        itemsCache = dependency.instance(IItemsCache)
        vehicle = itemsCache.items.getItemByCD(vehicleCD)
        if vehicle.invID == -1:
            return False
        name = 'hide' + state
        settings = self.bootcampCtrl.getLobbySettings()
        if name in settings:
            if not settings[name]:
                return True
        return False


def ConditionFactory(conditionDict):
    conditionType = conditionDict['type']
    if conditionType == 'module':
        return Module(conditionDict)
    elif conditionType == 'vehicle':
        return Vehicle(conditionDict)
    elif conditionType == 'perk':
        return Perk(conditionDict)
    elif conditionType == 'consumable':
        return Consumable(conditionDict)
    elif conditionType == 'equipment':
        return Equipment(conditionDict)
    elif conditionType == 'battle_type':
        return BattleType(conditionDict)
    else:
        return HasView(conditionDict) if conditionType == 'has_view' else None
