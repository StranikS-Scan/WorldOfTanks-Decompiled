# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/battle_selector_items.py
import datetime
import logging
from adisp import process
from gui.prb_control.entities.base.ctx import PrbAction
from account_helpers import isDemonstrator
from constants import PREBATTLE_TYPE, QUEUE_TYPE, ACCOUNT_ATTR
from gui import GUI_SETTINGS
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.prb_getters import areSpecBattlesHidden
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
from gui.shared.formatters import text_styles, icons
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from helpers import time_utils, dependency, int2roman
from shared_utils import findFirst
from skeletons.gui.game_control import IRankedBattlesController, IEventProgressionController, IEpicBattleMetaGameController, IBootcampController
from skeletons.gui.lobby_context import ILobbyContext
from gui.clans.clan_helpers import isStrongholdsEnabled
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS
from gui.game_control.epic_meta_game_ctrl import EPIC_PERF_GROUP
from gui.impl import backport
from gui.impl.gen import R
_logger = logging.getLogger(__name__)
_R_HEADER_BUTTONS = R.strings.menu.headerButtons
_R_BATTLE_TYPES = R.strings.menu.headerButtons.battle.types
_R_BATTLE_MENU = R.strings.menu.headerButtons.battle.menu
_R_ICONS = R.images.gui.maps.icons

class _SelectorItem(object):
    __slots__ = ('_label', '_data', '_order', '_selectorType', '_isVisible', '_isExtra', '_isSelected', '_isNew', '_isDisabled', '_isLocked')
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, label, data, order, selectorType=None, isVisible=True, isExtra=False):
        super(_SelectorItem, self).__init__()
        self._label = label
        self._data = data
        self._order = order
        self._isSelected = False
        self._isNew = False
        self._isLocked = False
        self._isDisabled = True
        self._isVisible = isVisible
        self._isExtra = isExtra
        self._selectorType = selectorType

    def __cmp__(self, other):
        return cmp(self.getOrder(), other.getOrder())

    def getLabel(self):
        return self._label

    def getData(self):
        return self._data

    def isSelected(self):
        return self._isSelected

    def getSelectorType(self):
        return self._selectorType

    def isDisabled(self):
        return self._isDisabled

    def isVisible(self):
        return self._isVisible

    def isExtra(self):
        return self._isExtra

    def getSmallIcon(self):
        return backport.image(_R_ICONS.battleTypes.c_40x40.dyn(self._data)())

    def getLargerIcon(self):
        return backport.image(_R_ICONS.battleTypes.c_64x64.dyn(self._data)())

    def getSpecialBGIcon(self):
        pass

    def getFightButtonLabel(self, state, playerInfo):
        label = _R_HEADER_BUTTONS.battle
        if not playerInfo.isCreator and state.isReadyActionSupported():
            label = _R_HEADER_BUTTONS.notReady if playerInfo.isReady else _R_HEADER_BUTTONS.ready
        return backport.text(label())

    def isLocked(self):
        return self._isLocked

    def isDemoButtonDisabled(self):
        return True

    def isRandomBattle(self):
        return False

    def isInSquad(self, state):
        return state.isInUnit(PREBATTLE_TYPE.SQUAD) or state.isInUnit(PREBATTLE_TYPE.EVENT) or state.isInUnit(PREBATTLE_TYPE.EPIC)

    def setLocked(self, value):
        self._isLocked = value
        if self._isLocked:
            self._isDisabled = True
            self._isSelected = False
            self._isVisible = False

    def isSelectorBtnEnabled(self):
        return self._isLocked or not self._isDisabled

    def getVO(self):
        return {'label': self.getFormattedLabel(),
         'data': self._data,
         'disabled': self._isDisabled,
         'icon': self.getLargerIcon(),
         'active': self._isSelected,
         'isNew': self.isShowNewIndicator(),
         'specialBgIcon': self.getSpecialBGIcon()}

    def isShowNewIndicator(self):
        return self._isNew

    def getFormattedLabel(self):
        return text_styles.middleTitle(self._label)

    def getOrder(self):
        return self._order

    def update(self, state):
        if self._selectorType is not None:
            self._isNew = not selectorUtils.isKnownBattleType(self._selectorType)
        if not self.isLocked():
            self._update(state)
        return

    def select(self):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            self._doSelect(dispatcher)
        else:
            _logger.error('Prebattle dispatcher is not defined')
        return

    def _update(self, state):
        raise NotImplementedError

    @process
    def _doSelect(self, dispatcher):
        yield dispatcher.doSelectAction(PrbAction(self.getData()))


class _SelectorExtraItem(_SelectorItem):

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(_SelectorExtraItem, self).__init__(label, data, order, selectorType, isVisible, isExtra=True)

    def getVO(self):
        vo = super(_SelectorExtraItem, self).getVO()
        vo.update({'mainLabel': self.getMainLabel(),
         'infoLabel': self.getInfoLabel()})
        return vo

    def getMainLabel(self):
        raise NotImplementedError

    def getInfoLabel(self):
        raise NotImplementedError

    def _update(self, state):
        raise NotImplementedError


class _DisabledSelectorItem(_SelectorItem):

    def update(self, state):
        pass

    def _update(self, state):
        pass

    def select(self):
        _logger.warning('That routine can not be invoked')


class _RandomQueueItem(_SelectorItem):

    def isRandomBattle(self):
        return True

    def isDemoButtonDisabled(self):
        return False

    def setLocked(self, value):
        self._isLocked = value
        if self._isLocked:
            self._isDisabled = True
            self._isSelected = False

    def _update(self, state):
        self._isDisabled = state.hasLockedState
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.RANDOMS)


class _CommandItem(_SelectorItem):

    def isRandomBattle(self):
        return True

    def isInSquad(self, state):
        return False

    def _update(self, state):
        isCommandBattleEnabled = self.lobbyContext.getServerSettings().isCommandBattleEnabled()
        self._isSelected = state.isInUnit(PREBATTLE_TYPE.UNIT) or state.isInUnit(PREBATTLE_TYPE.E_SPORT_COMMON)
        self._isDisabled = state.hasLockedState or not isCommandBattleEnabled
        self._isVisible = isCommandBattleEnabled


class _StrongholdsItem(_SelectorItem):

    def isRandomBattle(self):
        return True

    def isInSquad(self, state):
        return False

    def _update(self, state):
        self._isSelected = state.isInUnit(PREBATTLE_TYPE.STRONGHOLD)
        if isStrongholdsEnabled() or self._isSelected:
            self._isDisabled = state.hasLockedState
        else:
            self._isDisabled = True


class _SpecBattleItem(_SelectorItem):

    def _update(self, state):
        if state.isInSpecialPrebattle():
            self._isSelected = True
            self._isDisabled = state.hasLockedState
        else:
            self._isSelected = False
            self._isDisabled = areSpecBattlesHidden()


class _TrainingItem(_SelectorItem):

    def getFightButtonLabel(self, state, playerInfo):
        return backport.text(_R_HEADER_BUTTONS.battle())

    def _update(self, state):
        self._isSelected = state.isInLegacy(PREBATTLE_TYPE.TRAINING)
        self._isDisabled = state.hasLockedState


class _EpicTrainingItem(_SelectorItem):

    def getFightButtonLabel(self, state, playerInfo):
        return backport.text(_R_HEADER_BUTTONS.battle())

    def _update(self, state):
        settings = self.lobbyContext.getServerSettings()
        self._isSelected = state.isInLegacy(PREBATTLE_TYPE.EPIC_TRAINING)
        self._isDisabled = state.hasLockedState
        self._isVisible = settings is not None and settings.frontline.isEpicTrainingEnabled
        return

    def getFormattedLabel(self):
        title = super(_EpicTrainingItem, self).getFormattedLabel()
        descr = text_styles.main(backport.text(R.strings.menu.headerButtons.battle.types.epicTraining.descr()))
        return '{}\n{}'.format(title, descr)

    def select(self):
        super(_EpicTrainingItem, self).select()
        selectorUtils.setBattleTypeAsKnown(self._selectorType)


class _BattleTutorialItem(_SelectorItem):

    def isRandomBattle(self):
        return True

    def _update(self, state):
        self._isSelected = state.isInPreQueue(QUEUE_TYPE.TUTORIAL)
        self._isDisabled = state.hasLockedState


class _SandboxItem(_SelectorItem):

    def isRandomBattle(self):
        return True

    def _update(self, state):
        self._isDisabled = state.hasLockedState
        self._isSelected = state.isQueueSelected(queueType=QUEUE_TYPE.SANDBOX)
        self._isVisible = self.lobbyContext.getServerSettings().isSandboxEnabled()


class _EventProgressionDefaultDataProvider(_SelectorExtraItem):
    __eventProgressionController = dependency.descriptor(IEventProgressionController)

    def __init__(self):
        super(_EventProgressionDefaultDataProvider, self).__init__(label=backport.text(_R_BATTLE_TYPES.eventProgression.about(), year=datetime.datetime.now().year), data=PREBATTLE_ACTION_NAME.EPIC, order=0, selectorType=SELECTOR_BATTLE_TYPES.EVENT_PROGRESSION)
        self._isDisabled = False
        self._isNew = False

    def select(self):
        self.__eventProgressionController.openURL()

    def getFormattedLabel(self):
        return text_styles.main(self._label)

    def getSmallIcon(self):
        pass

    def getLargerIcon(self):
        pass

    def getMainLabel(self):
        return text_styles.highTitle(backport.text(_R_BATTLE_TYPES.eventProgression()))

    def getInfoLabel(self):
        return '{} {}'.format(text_styles.highTitle(self.__eventProgressionController.actualRewardPoints), icons.makeImageTag(backport.image(_R_ICONS.epicBattles.rewardPoints.c_16x16()), vSpace=-1))

    def _update(self, state):
        pass


class _EventProgressionEpicDataProvider(_SelectorExtraItem):
    __evProgCtrl = dependency.descriptor(IEventProgressionController)
    __epicCtrl = dependency.descriptor(IEpicBattleMetaGameController)
    __bootcampCtrl = dependency.descriptor(IBootcampController)

    def __init__(self):
        super(_EventProgressionEpicDataProvider, self).__init__(label=backport.text(_R_BATTLE_TYPES.epic()), data=PREBATTLE_ACTION_NAME.EPIC, order=0, selectorType=SELECTOR_BATTLE_TYPES.EVENT_PROGRESSION, isVisible=True)

    def isRandomBattle(self):
        return True

    def getMainLabel(self):
        return text_styles.highTitle(backport.text(_R_BATTLE_TYPES.eventProgression()))

    def getInfoLabel(self):
        return '{} {}'.format(text_styles.highTitle(self.__evProgCtrl.actualRewardPoints), icons.makeImageTag(backport.image(_R_ICONS.epicBattles.rewardPoints.c_16x16()), vSpace=-2))

    def getFormattedLabel(self):
        battleTypeName = super(_EventProgressionEpicDataProvider, self).getFormattedLabel()
        availabilityStr = self.__getPerformanceAlarmStr() or self.__getScheduleStr()
        return battleTypeName if availabilityStr is None else '{}\n{}'.format(battleTypeName, availabilityStr)

    def getSpecialBGIcon(self):
        return backport.image(_R_ICONS.buttons.selectorRendererExtraBGEvent()) if self.__epicCtrl.isInPrimeTime() else ''

    def isShowNewIndicator(self):
        return False

    @process
    def _doSelect(self, dispatcher):
        if self.__epicCtrl.getCurrentSeason() is not None or self.__epicCtrl.getNextSeason() is not None:
            isSuccess = yield dispatcher.doSelectAction(PrbAction(self._data))
            if isSuccess and self._isNew:
                selectorUtils.setBattleTypeAsKnown(self._selectorType)
            else:
                return
        self.__evProgCtrl.openURL()
        return

    def _update(self, state):
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.EPIC)
        self._isDisabled = not self.__epicCtrl.isEnabled() or self.__epicCtrl.isFrozen()
        self._isVisible = any((self.__epicCtrl.getCurrentSeason(), self.__epicCtrl.getNextSeason()))
        if self._selectorType is not None:
            self._isNew = not selectorUtils.isKnownBattleType(self._selectorType)
        return

    def __getScheduleStr(self):
        if self._isDisabled:
            return text_styles.error(backport.text(_R_BATTLE_TYPES.epic.extra.frozen()))
        else:
            currentSeason = self.__epicCtrl.getCurrentSeason()
            if currentSeason:
                seasonResID = R.strings.epic_battle.season.num(currentSeason.getSeasonID())
                seasonName = backport.text(seasonResID.name()) if seasonResID else None
                if currentSeason.hasActiveCycle(time_utils.getCurrentLocalServerTimestamp()):
                    cycleNumber = currentSeason.getCycleInfo().getEpicCycleNumber()
                    scheduleStr = backport.text(_R_BATTLE_TYPES.epic.extra.currentCycle(), cycle=int2roman(cycleNumber), season=seasonName)
                else:
                    nextCycle = currentSeason.getNextCycleInfo(time_utils.getCurrentLocalServerTimestamp())
                    if nextCycle is None:
                        nextCycle = currentSeason.getNextByTimeCycle(time_utils.getCurrentLocalServerTimestamp())
                    if nextCycle:
                        nextCycleStartTime = backport.getDateTimeFormat(nextCycle.startDate)
                        scheduleStr = backport.text(_R_BATTLE_TYPES.epic.extra.startsAt(), time=nextCycleStartTime)
                    else:
                        scheduleStr = None
            else:
                nextSeason = self.__epicCtrl.getNextSeason()
                nextCycle = nextSeason.getNextByTimeCycle(time_utils.getCurrentLocalServerTimestamp())
                if nextCycle:
                    startTime = backport.getDateTimeFormat(nextCycle.startDate)
                    scheduleStr = backport.text(_R_BATTLE_TYPES.epic.extra.startsAt(), time=startTime)
                else:
                    scheduleStr = None
            return text_styles.main(scheduleStr) if scheduleStr else None

    def __getPerformanceAlarmStr(self):
        currPerformanceGroup = self.__epicCtrl.getPerformanceGroup()
        attentionText, iconPath = (None, None)
        if currPerformanceGroup == EPIC_PERF_GROUP.HIGH_RISK:
            attentionText = text_styles.error(backport.text(_R_BATTLE_MENU.attention.lowPerformance()))
            iconPath = backport.image(_R_ICONS.library.marker_blocked())
        elif currPerformanceGroup == EPIC_PERF_GROUP.MEDIUM_RISK:
            attentionText = text_styles.alert(backport.text(_R_BATTLE_MENU.attention.reducedPerformance()))
            iconPath = backport.image(_R_ICONS.library.alertIcon())
        return icons.makeImageTag(iconPath, vSpace=-3) + ' ' + attentionText if attentionText and iconPath else None


class _EventProgressionItem(_SelectorExtraItem):
    __bootcampController = dependency.descriptor(IBootcampController)
    __eventProgressionController = dependency.descriptor(IEventProgressionController)

    def __init__(self, *dataProviders):
        self.__dataProviders = dataProviders or []
        self.__dataProvider = None
        self.__switchDataProvider()
        super(_EventProgressionItem, self).__init__(label=self.getLabel(), data=self.getData(), order=self.getOrder(), selectorType=self.getSelectorType(), isVisible=self.__dataProvider.isVisible())
        self._isNew = False
        return

    def getLabel(self):
        return self.__dataProvider.getLabel()

    def getData(self):
        return self.__dataProvider.getData()

    def getOrder(self):
        return self.__dataProvider.getOrder()

    def getSelectorType(self):
        return self.__dataProvider.getSelectorType()

    def getVO(self):
        return self.__dataProvider.getVO()

    def getMainLabel(self):
        return self.__dataProvider.getMainLabel()

    def getInfoLabel(self):
        return self.__dataProvider.getInfoLabel()

    def getFormattedLabel(self):
        return self.__dataProvider.getFormattedLabel()

    def isRandomBattle(self):
        return self.__dataProvider.isRandomBattle()

    def isSelected(self):
        return self.__dataProvider.isSelected()

    def isSelectorBtnEnabled(self):
        return self.__dataProvider.isSelectorBtnEnabled()

    def select(self):
        self.__dataProvider.select()

    def _update(self, state):
        self.__switchDataProvider()
        self.__dataProvider.update(state)
        self._isVisible = self.__eventProgressionController.isEnabled and not self.__bootcampController.isInBootcamp()

    def __switchDataProvider(self):
        self.__dataProvider = findFirst(lambda dp: dp.isVisible(), self.__dataProviders, _EventProgressionDefaultDataProvider())


class _BattleSelectorItems(object):

    def __init__(self, items, extraItems=None):
        super(_BattleSelectorItems, self).__init__()
        self.__items = {item.getData():item for item in items}
        self.__extraItems = {item.getData():item for item in extraItems} if extraItems else dict()
        self.__isDemonstrator = False
        self.__isDemoButtonEnabled = False

    def init(self):
        pass

    def fini(self):
        self.__items.clear()
        self.__extraItems.clear()
        self.__isDemonstrator = False
        self.__isDemoButtonEnabled = False

    def update(self, state):
        selected = self.__items[self._getDefaultPAN()]
        for item in self.__items.itervalues():
            item.update(state)
            if item.isSelected():
                selected = item

        for item in self.__extraItems.itervalues():
            item.update(state)
            if item.isSelected():
                selected = item

        if self.__isDemonstrator:
            self.__isDemoButtonEnabled = not selected.isDemoButtonDisabled()
        return selected

    def validateAccountAttrs(self, attrs):
        self.__isDemonstrator = isDemonstrator(attrs)
        locked = not attrs & ACCOUNT_ATTR.RANDOM_BATTLES
        for item in self.__items.itervalues():
            if item.isRandomBattle():
                item.setLocked(locked)

    def select(self, action):
        if action in self.__items:
            self.__items[action].select()
        elif action in self.__extraItems:
            self.__extraItems[action].select()
        else:
            _logger.error('Can not invoke action: %s', action)

    def getVOs(self):

        def getVisibleVOs(items):
            return [ item.getVO() for item in sorted(items.itervalues()) if item.isVisible() ]

        return (getVisibleVOs(self.__items),
         getVisibleVOs(self.__extraItems),
         self.__isDemonstrator,
         self.__isDemoButtonEnabled)

    def getItems(self):
        return self.__items

    def _getDefaultPAN(self):
        return _DEFAULT_PAN

    def isSelected(self, action):
        if action in self.__items:
            return self.__items[action].isSelected()
        if action in self.__extraItems:
            return self.__extraItems[action].isSelected()
        _logger.error('Action not found: %s', action)
        return False


class _SquadSelectorItems(_BattleSelectorItems):

    def _getDefaultPAN(self):
        return _DEFAULT_SQUAD_PAN


class _SimpleSquadItem(_SelectorItem):

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(_SimpleSquadItem, self).__init__(label, data, order, selectorType, isVisible)
        self._isDisabled = False
        self._isSelected = False
        self._isVisible = True

    def _update(self, state):
        self._isSelected = state.isInUnit(PREBATTLE_TYPE.SQUAD)
        self._isDisabled = state.hasLockedState and not state.isInUnit(PREBATTLE_TYPE.SQUAD)


class _EventSquadItem(_SelectorItem):

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(_EventSquadItem, self).__init__(label, data, order, selectorType, isVisible)
        self._isDisabled = False
        self._isSelected = False
        self._isVisible = True

    def _update(self, state):
        self._isSelected = state.isInUnit(PREBATTLE_TYPE.EVENT)
        self._isDisabled = state.hasLockedState and not state.isInUnit(PREBATTLE_TYPE.EVENT)

    def getSpecialBGIcon(self):
        return backport.image(_R_ICONS.lobby.eventPopoverBtnBG())


class _RankedItem(_SelectorItem):
    rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(_RankedItem, self).__init__(label, data, order, selectorType, isVisible)
        self.__hasPastSeason = False

    def isRandomBattle(self):
        return True

    def getFormattedLabel(self):
        battleTypeName = super(_RankedItem, self).getFormattedLabel()
        availabilityStr = None
        if self.rankedController.hasSuitableVehicles():
            availabilityStr = self.__getAvailabilityStr()
        return battleTypeName if availabilityStr is None else '{}\n{}'.format(battleTypeName, availabilityStr)

    def getSpecialBGIcon(self):
        return backport.image(_R_ICONS.buttons.selectorRendererBGEvent()) if self.rankedController.isAvailable() else ''

    def select(self):
        if not self.rankedController.hasSuitableVehicles():
            g_eventDispatcher.loadRankedUnreachable()
        else:
            if self.rankedController.isAvailable():
                super(_RankedItem, self).select()
            elif self.__hasPastSeason:
                self.rankedController.showRankedBattlePage(ctx={'selectedItemID': RANKEDBATTLES_CONSTS.RANKED_BATTLES_RANKS_ID})
            selectorUtils.setBattleTypeAsKnown(self._selectorType)

    def _update(self, state):
        self._isSelected = state.isInPreQueue(QUEUE_TYPE.RANKED)
        self.__hasPastSeason = self.rankedController.getPreviousSeason() is not None
        isDisabled = self.rankedController.isFrozen() and self.rankedController.getCurrentSeason() is not None
        self._isDisabled = state.hasLockedState or isDisabled
        self._isVisible = self.rankedController.isEnabled()
        return

    def __getAvailabilityStr(self):
        if self._isVisible and self.rankedController.hasAnySeason():
            resShortCut = R.strings.menu.headerButtons.battle.types.ranked
            currentSeason = self.rankedController.getCurrentSeason()
            if currentSeason is not None:
                if self.rankedController.isUnset():
                    return backport.text(resShortCut.availability.notSet())
                if self.rankedController.isFrozen():
                    return backport.text(resShortCut.availability.frozen())
                seasonName = currentSeason.getUserName() or currentSeason.getNumber()
                return backport.text(resShortCut.availability.season(), season=seasonName)
            nextSeason = self.rankedController.getNextSeason()
            if nextSeason is not None:
                timeStamp = time_utils.makeLocalServerTime(nextSeason.getStartDate())
                date = backport.getShortDateFormat(timeStamp)
                time = backport.getShortTimeFormat(timeStamp)
                return backport.text(resShortCut.availability.until(), date=date, time=time)
            return backport.text(resShortCut.availability.ended())
        else:
            return


_g_items = None
_g_squadItems = None
_DEFAULT_PAN = PREBATTLE_ACTION_NAME.RANDOM
_DEFAULT_SQUAD_PAN = PREBATTLE_ACTION_NAME.SQUAD

@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def _createItems(lobbyContext=None):
    settings = lobbyContext.getServerSettings()
    isInRoaming = settings.roaming.isInRoaming()
    items = []
    _addRandomBattleType(items)
    _addRankedBattleType(items, settings)
    _addCommandBattleType(items, settings)
    _addStrongholdsBattleType(items, isInRoaming)
    _addTrainingBattleType(items)
    _addEpicTrainingBattleType(items, settings)
    if GUI_SETTINGS.specPrebatlesVisible:
        _addSpecialBattleType(items)
    if settings is not None and settings.isSandboxEnabled() and not isInRoaming:
        _addSandboxType(items)
    extraItems = []
    _addEventProgressionExtraType(extraItems)
    return _BattleSelectorItems(items, extraItems)


def _createSquadSelectorItems():
    items = []
    _addSimpleSquadType(items)
    _addEventSquadType(items)
    return _SquadSelectorItems(items)


def _addRandomBattleType(items):
    items.append(_RandomQueueItem(backport.text(_R_BATTLE_TYPES.standart()), PREBATTLE_ACTION_NAME.RANDOM, 0))


def _addRankedBattleType(items, settings):
    visible = settings is not None and settings.rankedBattles.isEnabled
    items.append(_RankedItem(backport.text(_R_BATTLE_TYPES.ranked()), PREBATTLE_ACTION_NAME.RANKED, 1, SELECTOR_BATTLE_TYPES.RANKED, isVisible=visible))
    return


def _addCommandBattleType(items, settings):
    visible = settings is not None and settings.isCommandBattleEnabled()
    items.append(_CommandItem(backport.text(_R_BATTLE_TYPES.unit()), PREBATTLE_ACTION_NAME.E_SPORT, 3, SELECTOR_BATTLE_TYPES.UNIT, isVisible=visible))
    return


def _addStrongholdsBattleType(items, isInRoaming):
    items.append((_DisabledSelectorItem if isInRoaming else _StrongholdsItem)(backport.text(_R_BATTLE_TYPES.strongholds()), PREBATTLE_ACTION_NAME.STRONGHOLDS_BATTLES_LIST, 4, SELECTOR_BATTLE_TYPES.SORTIE))


def _addTrainingBattleType(items):
    items.append(_TrainingItem(backport.text(_R_BATTLE_TYPES.training()), PREBATTLE_ACTION_NAME.TRAININGS_LIST, 7))


def _addEpicTrainingBattleType(items, settings=None):
    visible = settings is not None and settings.frontline.isEpicTrainingEnabled
    items.append(_EpicTrainingItem(backport.text(_R_BATTLE_TYPES.epicTraining()), PREBATTLE_ACTION_NAME.EPIC_TRAINING_LIST, 10, SELECTOR_BATTLE_TYPES.EPIC, isVisible=visible))
    return


def _addSpecialBattleType(items):
    items.append(_SpecBattleItem(backport.text(_R_BATTLE_TYPES.spec()), PREBATTLE_ACTION_NAME.SPEC_BATTLES_LIST, 6))


def _addTutorialBattleType(items, isInRoaming):
    items.append((_DisabledSelectorItem if isInRoaming else _BattleTutorialItem)(backport.text(_R_BATTLE_TYPES.battleTutorial()), PREBATTLE_ACTION_NAME.BATTLE_TUTORIAL, 8))


def _addSandboxType(items):
    items.append(_SandboxItem(backport.text(_R_BATTLE_TYPES.battleTeaching()), PREBATTLE_ACTION_NAME.SANDBOX, 9))


def _addEventProgressionExtraType(items):
    items.append(_EventProgressionItem(_EventProgressionEpicDataProvider()))


def _addSimpleSquadType(items):
    items.append(_SimpleSquadItem(text_styles.middleTitle(backport.text(_R_BATTLE_TYPES.simpleSquad())), PREBATTLE_ACTION_NAME.SQUAD, 0))


def _addEventSquadType(items):
    items.append(_EventSquadItem(text_styles.middleTitle(backport.text(_R_BATTLE_TYPES.eventSquad())), PREBATTLE_ACTION_NAME.EVENT_SQUAD, 1))


def create():
    global _g_squadItems
    global _g_items
    if _g_items is None:
        _g_items = _createItems()
    else:
        _logger.warning('Item already is created')
    if _g_squadItems is None:
        _g_squadItems = _createSquadSelectorItems()
    else:
        _logger.warning('Item already is created')
    return


def clear():
    global _g_squadItems
    global _g_items
    if _g_items:
        _g_items.fini()
        _g_items = None
    if _g_squadItems:
        _g_squadItems.fini()
        _g_squadItems = None
    return


def getItems():
    return _g_items


def getSquadItems():
    return _g_squadItems
