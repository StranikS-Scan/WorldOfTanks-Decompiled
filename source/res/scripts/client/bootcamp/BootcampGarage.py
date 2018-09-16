# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/BootcampGarage.py
import BigWorld
from functools import partial
from BootCampEvents import g_bootcampEvents
from BootcampConstants import BOOTCAMP_MESSAGE_WINDOW, MESSAGE_BOTTOM_RENDERER, getBootcampInternalHideElementName
from constants import QUEUE_TYPE
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP, LOG_CURRENT_EXCEPTION_BOOTCAMP, LOG_ERROR_BOOTCAMP
from helpers import dependency, aop
from skeletons.gui.game_control import IBootcampController
from skeletons.gui.shared import IItemsCache
from helpers.i18n import makeString
from math import ceil
from helpers import i18n, time_utils
from copy import deepcopy
from gui.Scaleform.genConsts.NODE_STATE_FLAGS import NODE_STATE_FLAGS
from gui.Scaleform.daapi.view.lobby.techtree.settings import NODE_STATE
from nations import NAMES as NATION_NAMES
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control import prbEntityProperty
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from PlayerEvents import g_playerEvents
from BootcampGarageLessons import ACTION_PARAM, LESSON_PARAM, GarageLessons, GarageActions
from Bootcamp import g_bootcamp
from gui.Scaleform.Waiting import Waiting
from shared_utils import BoundMethodWeakref
from aop.in_garage import PointcutBattleSelectorHintText
from adisp import process, async
import SoundGroups

class MakeSandboxSelectedAspect(aop.Aspect):

    def atReturn(self, cd):
        original_return_value = cd.returned
        original_return_value.entityTypeID = QUEUE_TYPE.SANDBOX
        return original_return_value


class MakeSandboxSelected(aop.Pointcut):

    def __init__(self):
        aop.Pointcut.__init__(self, 'gui.prb_control.dispatcher', '_PreBattleDispatcher', 'getFunctionalState', aspects=(MakeSandboxSelectedAspect,))


class ACTION_TYPE_NAME():
    UNKNOWN_STR = 'unknown'
    INIT_STR = 'init'
    SHOW_MESSAGE_STR = 'msg'
    SHOW_ELEMENT_STR = 'show'
    HIGHLIGHT_BUTTON_STR = 'highlightButton'
    CALLBACK_STR = 'callback'
    CONDITIONAL_STR = 'conditional'


class ACTION_TYPE():
    UNKNOWN = 0
    CALLBACK = 1
    SHOW_MESSAGE = 2
    SHOW_ELEMENT = 3
    HIGHLIGHT_BUTTON = 4
    HIGHLIGHT_VEHICLE = 5
    INIT = 6
    CONDITIONAL = 7


def getActionType(actionName):
    if actionName.startswith(ACTION_TYPE_NAME.CALLBACK_STR):
        return ACTION_TYPE.CALLBACK
    if actionName.startswith(ACTION_TYPE_NAME.SHOW_MESSAGE_STR):
        return ACTION_TYPE.SHOW_MESSAGE
    if actionName.startswith(ACTION_TYPE_NAME.SHOW_ELEMENT_STR):
        return ACTION_TYPE.SHOW_ELEMENT
    if actionName.startswith(ACTION_TYPE_NAME.HIGHLIGHT_BUTTON_STR):
        return ACTION_TYPE.HIGHLIGHT_BUTTON
    if actionName.startswith(ACTION_TYPE_NAME.INIT_STR):
        return ACTION_TYPE.INIT
    return ACTION_TYPE.CONDITIONAL if actionName.startswith(ACTION_TYPE_NAME.CONDITIONAL_STR) else ACTION_TYPE.UNKNOWN


class CyclicController():

    def __init__(self):
        self.__elements = set()

    def checkCyclic(self, element, info):
        LOG_DEBUG_DEV_BOOTCAMP('[checkCyclic] Element {0}'.format(element))
        if element == '':
            raise Exception('[checkCyclic] Empty element found!')
        if element in self.__elements:
            raise Exception('[checkCyclic] Infinite cycle found! Aborting! Info - {0}'.format(info))
        self.__elements.add(element)


class BootcampGarageActions():

    def __init__(self):
        self.viewActions = {}
        self.__garageLessons = GarageLessons()
        self.__garageActions = GarageActions()
        self.actionStart = None
        self.actionFinish = None
        self.__lessonFinished = False
        return

    def getLessonById(self, lessonId):
        return self.__garageLessons.getLesson(lessonId)

    def getBattleResultsById(self, lessonId):
        return self.__garageLessons.getBattleResult(lessonId)

    def getActionByName(self, actionName, isSaveToServer=True):
        action = self.__garageActions.getAction(actionName)
        if isSaveToServer:
            self.__lessonFinished = actionName == self.actionFinish
            if self.__lessonFinished or ACTION_PARAM.SAVE in action and action[ACTION_PARAM.SAVE]:
                g_bootcampGarage.setCheckpoint(actionName)
                g_bootcampGarage.saveCheckpointToServer()
                if self.__lessonFinished:
                    g_bootcampGarage.clear()
        return action

    def isLessonFinished(self):
        return self.__lessonFinished

    def getViewActions(self, viewAlias):
        return self.viewActions.get(viewAlias, []) + self.viewActions.get('all', [])

    def setViewAction(self, viewAlias, action):
        if viewAlias not in self.viewActions:
            self.viewActions[viewAlias] = []
        self.viewActions[viewAlias].append(action)

    def resetViewAction(self, viewAlias):
        if viewAlias in self.viewActions:
            del self.viewActions[viewAlias]

    def clearAllViewActions(self):
        self.viewActions.clear()


class BootcampGarageLesson(object):
    itemsCache = dependency.descriptor(IItemsCache)
    bootcampCtrl = dependency.descriptor(IBootcampController)

    def __init__(self):
        self.__started = False
        self.__lessonId = 0
        self.__checkpoint = ''
        self.__account = None
        self.__lobbyAssistant = None
        self.__bootcampGarageActions = None
        self.__prevHint = None
        self.__nextHint = None
        self.__hardcodeHint = None
        self.__secondVehicleInvID = None
        self.__isInPreview = False
        self.isLessonSuspended = False
        self.__callbacks = {'onBattleReady': BoundMethodWeakref(self.onBattleReady),
         'onBootcampFinished': BoundMethodWeakref(self.finishBootcamp),
         'setBattleSelectorHintText': BoundMethodWeakref(self.setBattleSelectorHintText),
         'clear': BoundMethodWeakref(self.clear),
         'showFinalVideo': BoundMethodWeakref(self.showFinalVideo),
         'disableResearchButton': BoundMethodWeakref(self.disableResearchButton),
         'enableResearchButton': BoundMethodWeakref(self.enableResearchButton),
         'disableVehiclePreviewBuyButton': BoundMethodWeakref(self.disableVehiclePreviewBuyButton),
         'enableVehiclePreviewBuyButton': BoundMethodWeakref(self.enableVehiclePreviewBuyButton)}
        self.__hintsLoaded = False
        self.__hangarLoaded = False
        self.__battleSelectorHintPointcutIndex = None
        self._actions = {ACTION_TYPE.INIT: BoundMethodWeakref(self.initAction),
         ACTION_TYPE.CALLBACK: BoundMethodWeakref(self.callbackAction),
         ACTION_TYPE.SHOW_MESSAGE: BoundMethodWeakref(self.showMessage),
         ACTION_TYPE.SHOW_ELEMENT: BoundMethodWeakref(self.showElement),
         ACTION_TYPE.HIGHLIGHT_BUTTON: BoundMethodWeakref(self.highlightButton),
         ACTION_TYPE.CONDITIONAL: BoundMethodWeakref(self.conditionalAction)}
        self.__showActionsHistory = []
        self.__deferredAliases = []
        self.__itemCacheSyncCallbacks = []
        return

    @prbEntityProperty
    def prbEntity(self):
        pass

    @property
    def isLessonFinished(self):
        garageActions = self.getBootcampGarageActions()
        return garageActions.isLessonFinished()

    @property
    def canGoToBattle(self):
        prbEntity = self.prbEntity
        if prbEntity is None:
            return False
        else:
            result = prbEntity.canPlayerDoAction()
            canDo, canDoMsg = result.isValid, result.restriction
            return canDo

    def onBattleReady(self):
        g_bootcampEvents.onBattleReady()

    def clear(self):
        self.__started = False
        self.__prevHint = None
        self.__nextHint = None
        self.__hardcodeHint = None
        self.isLessonSuspended = False
        self.__account = None
        self.__showActionsHistory = []
        self.__hintsLoaded = False
        self.__hangarLoaded = False
        g_bootcamp.removePointcut(self.__battleSelectorHintPointcutIndex)
        self.__battleSelectorHintPointcutIndex = None
        self.__bootcampGarageActions.clearAllViewActions()
        return

    def getBootcampGarageActions(self):
        if self.__bootcampGarageActions is None:
            self.__bootcampGarageActions = BootcampGarageActions()
        return self.__bootcampGarageActions

    def start(self):
        if self.__started:
            return
        else:
            self.__started = True
            self.isLessonSuspended = False
            self.__showActionsHistory = []
            self.__bootcampGarageActions = None
            self.getBootcampGarageActions()
            lesson = self.__bootcampGarageActions.getLessonById(self.__lessonId)
            self.__bootcampGarageActions.actionStart = lesson[LESSON_PARAM.ACTION_START]
            self.__bootcampGarageActions.actionFinish = lesson[LESSON_PARAM.ACTION_FINISH]
            lastLesson = g_bootcamp.getContextIntParameter('lastLessonNum')
            if self.__lessonId == lastLesson:
                self.__prevHint = None
                self.__nextHint = None
                self.__hardcodeHint = None
            if self.__checkpoint != '':
                self.enableCheckpointGUI()
                currentAction = self.runCheckpoint()
            else:
                currentAction = self.__bootcampGarageActions.actionStart
                startCallback = self.getCallbackByName(currentAction)
                startCallback()
            if self.__lessonId != lastLesson:
                self.setAllViewActions(currentAction)
            if currentAction != self.__bootcampGarageActions.actionFinish:
                g_bootcampEvents.onBattleNotReady()
            g_bootcampEvents.onEnterPreview += self.onEnterPreview
            g_bootcampEvents.onExitPreview += self.onExitPreview
            return

    def init(self, lessonId, account):
        garageActions = self.getBootcampGarageActions()
        garageActions.clearAllViewActions()
        self.__checkpoint = ''
        self.__prevHint = None
        self.__nextHint = None
        self.__hardcodeHint = None
        self.__lessonId = lessonId
        self.__account = account
        self.__showActionsHistory = []
        self.__secondVehicleInvID = None
        self.__updateSecondVehicleInvID()
        return

    def onInventoryUpdate(self, _, __):
        self.runViewAlias(VIEW_ALIAS.LOBBY_HANGAR)

    def runCheckpoint(self):
        LOG_DEBUG_DEV_BOOTCAMP('Run checkpoint {0}'.format(self.__checkpoint))
        self.runCustomAction(self.__checkpoint)
        return self.__checkpoint

    def setCheckpoint(self, checkpoint):
        self.__checkpoint = checkpoint

    def saveCheckpointToServer(self):
        if g_playerEvents.isPlayerEntityChanging:
            LOG_DEBUG_DEV_BOOTCAMP('events.isPlayerEntityChanging', g_playerEvents.isPlayerEntityChanging)
            return
        else:
            if self.__account is not None:
                self.__account.base.saveBootcampCheckpoint(self.__checkpoint, self.__lessonId)
            return

    def enableCheckpointGUI(self):
        actionStart = self.__bootcampGarageActions.actionStart
        checkpoint = self.__checkpoint
        currentAction = actionStart
        visibleElements = []
        cyclicController = CyclicController()
        cyclicError = 'enableCheckpointGUI, lessonId - {0}, currentAction - {1}'
        LOG_DEBUG_DEV_BOOTCAMP('Start to enableCheckpointGUI, lessonId - {0}, currentAction - {1}, checkpoint - {2}'.format(self.__lessonId, currentAction, self.__checkpoint))
        while currentAction != checkpoint:
            cyclicController.checkCyclic(currentAction, cyclicError.format(self.__lessonId, currentAction))
            if currentAction is None:
                return
            currentAction = self.collectVisibleElements(currentAction, visibleElements)

        for action in self.__showActionsHistory:
            self.collectVisibleElements(action, visibleElements)

        if visibleElements:
            self.enableGarageGUIElements(visibleElements)
        return

    def collectVisibleElements(self, currentAction, visibleElements):
        action = self.__bootcampGarageActions.getActionByName(currentAction, False)
        nextHint = action[ACTION_PARAM.NEXT_HINT]
        actionType = getActionType(currentAction)
        elements = []
        if actionType == ACTION_TYPE.INIT:
            elements = action[ACTION_PARAM.VISIBLE].split(' ')
        elif actionType == ACTION_TYPE.SHOW_ELEMENT:
            elements = action[ACTION_PARAM.SHOW].split(' ')
        if elements:
            visibleElements.extend(elements)
        return nextHint

    def runViewAlias(self, viewAlias):
        lastLesson = g_bootcamp.getContextIntParameter('lastLessonNum')
        if not self.isLessonSuspended and self.__lessonId != lastLesson:
            viewActions = self.__bootcampGarageActions.getViewActions(viewAlias)
            for action in viewActions:
                name = action[ACTION_PARAM.NAME]
                condition = action['show_condition']['condition']
                nationData = self.getNationData()
                if getActionType(name) == ACTION_TYPE.SHOW_MESSAGE:
                    if name in self.__showActionsHistory:
                        continue
                if condition.recheckOnItemSync() and viewAlias not in self.__deferredAliases:
                    self.__deferredAliases.append(viewAlias)
                if condition.checkCondition(nationData) == action['show_condition']['result']:
                    if 'prevHint' in action['show_condition']:
                        if self.__prevHint != action['show_condition']['prevHint']:
                            continue
                    if getActionType(name) == ACTION_TYPE.HIGHLIGHT_BUTTON and name == self.__prevHint:
                        return True
                    self.hideAllHints()
                    callbackAction = self.getCallbackByName(name)
                    callbackAction()
                    return True

        return False

    def hideAllHints(self):
        self.__prevHint = None
        self.__hardcodeHint = None
        g_eventBus.handleEvent(events.LoadViewEvent(events.BootcampEvent.REMOVE_ALL_HIGHLIGHTS, None, None), EVENT_BUS_SCOPE.LOBBY)
        return

    @process
    def onViewLoaded(self, view, _):
        if view is not None and view.settings is not None:
            alias = view.settings.alias
            doStart = False
            if not self.__hintsLoaded and alias == VIEW_ALIAS.BOOTCAMP_LOBBY_HIGHLIGHTS:
                self.__hintsLoaded = True
                doStart = self.__hangarLoaded
            if not self.__hangarLoaded and alias == VIEW_ALIAS.LOBBY_HANGAR:
                self.__hangarLoaded = True
                doStart = self.__hintsLoaded
            if doStart:
                self.start()
                return
            if alias != VIEW_ALIAS.LOBBY_MENU and alias != VIEW_ALIAS.BOOTCAMP_MESSAGE_WINDOW:
                if self.isLessonSuspended and alias == VIEW_ALIAS.LOBBY_HANGAR:
                    secondVehicleSelected = yield self.isSecondVehicleSelectedAsync()
                    if not secondVehicleSelected:
                        self.checkSecondVehicleHintEnabled()
                        self.highlightLobbyHint('SecondTank', True, True)
                        return
                if self.__checkpoint != self.__bootcampGarageActions.actionFinish:
                    visibleElements = []
                    for action in self.__showActionsHistory:
                        self.collectVisibleElements(action, visibleElements)

                    if visibleElements:
                        self.changeGarageGUIElementsVisibility(visibleElements, False)
                    self.hideExcessElements()
                    foundHints = False
                    VIEWS_WITH_CONDITIONAL_HINTS = (VIEW_ALIAS.PERSONAL_CASE, VIEW_ALIAS.VEHICLE_PREVIEW)
                    if alias not in VIEWS_WITH_CONDITIONAL_HINTS:
                        foundHints = self.runViewAlias(alias)
                    VIEWS_TO_HIGHLIGHT_RETURN_FROM = (VIEW_ALIAS.LOBBY_RESEARCH, VIEW_ALIAS.LOBBY_TECHTREE)
                    if not foundHints and alias in VIEWS_TO_HIGHLIGHT_RETURN_FROM:
                        self.checkReturnToHangar()
                elif self.canGoToBattle:
                    LOG_DEBUG_DEV_BOOTCAMP('onViewLoaded - calling onBattleReady (view {0})'.format(alias))
                    self.onBattleReady()
        return

    def onViewClosed(self, viewAlias):
        if viewAlias in self.__deferredAliases:
            self.__deferredAliases.remove(viewAlias)

    def setAllViewActions(self, currentActionName):
        cyclicController = CyclicController()
        cyclicError = 'setAllViewActions, lessonId - {0}, currentAction - {1}'
        LOG_DEBUG_DEV_BOOTCAMP('Start to setAllViewActions, lessonId - {0}, currentAction - {1}, checkpoint - {2}'.format(self.__lessonId, currentActionName, self.__bootcampGarageActions.actionFinish))
        self.__bootcampGarageActions.clearAllViewActions()
        allViewActionsSet = False
        while not allViewActionsSet:
            cyclicController.checkCyclic(currentActionName, cyclicError.format(self.__lessonId, currentActionName))
            action = self.__bootcampGarageActions.getActionByName(currentActionName, False)
            if 'show_condition' in action:
                views = action['show_condition']['views']
                for view in views:
                    self.__bootcampGarageActions.setViewAction(view, action)

            if currentActionName == self.__bootcampGarageActions.actionFinish:
                allViewActionsSet = True
            if not allViewActionsSet:
                currentActionName = action[ACTION_PARAM.NEXT_HINT]

    def runCustomAction(self, customAction):
        callback = self.getCallbackByName(customAction)
        if callback:
            callback()

    def getCallbackByName(self, callbackName):
        LOG_DEBUG_DEV_BOOTCAMP('__getCallback - {0}'.format(callbackName))
        if self.isLessonSuspended:
            return
        elif not callbackName:
            return
        else:
            actionType = getActionType(callbackName)
            action = self._actions.get(actionType, None)
            return partial(action, callbackName) if action else None

    def initAction(self, actionName):
        if actionName is None:
            return
        else:
            initAction = self.__bootcampGarageActions.getActionByName(actionName)
            visibleElements = initAction[ACTION_PARAM.VISIBLE].split(' ')
            if visibleElements:
                self.enableGarageGUIElements(visibleElements)
            nextHint = initAction[ACTION_PARAM.NEXT_HINT]
            callback = self.getCallbackByName(nextHint)
            if callback is not None:
                callback()
            return

    def callbackAction(self, actionName):
        if actionName is None:
            return
        else:
            callbackAction = self.__bootcampGarageActions.getActionByName(actionName)
            if callbackAction['callback'] in self.__callbacks:
                callback = self.__callbacks[callbackAction['callback']]
                callback()
            nextHint = callbackAction[ACTION_PARAM.NEXT_HINT]
            callback = self.getCallbackByName(nextHint)
            if callback is not None:
                callback()
            return

    def showMessage(self, actionName):
        if actionName is None:
            return
        else:
            ctx = {'messages': [],
             'voiceovers': []}
            actionType = ACTION_TYPE.SHOW_MESSAGE
            cyclicController = CyclicController()
            cyclicError = 'showMessage, lessonId - {0}, currentAction - {1}'
            while actionType == ACTION_TYPE.SHOW_MESSAGE:
                cyclicController.checkCyclic(actionName, cyclicError.format(self.__lessonId, actionName))
                message = self.__bootcampGarageActions.getActionByName(actionName)
                hextHint = message[ACTION_PARAM.NEXT_HINT]
                hextHintType = getActionType(hextHint)
                nation = NATION_NAMES[self.getNation()]
                voiceover = message[ACTION_PARAM.NATIONS_DATA][nation].get(ACTION_PARAM.VOICEOVER, None)
                if not voiceover:
                    voiceover = message.get(ACTION_PARAM.VOICEOVER, None)
                ctx[ACTION_PARAM.VOICEOVERS].append(voiceover)
                callback = None
                if hextHintType != ACTION_TYPE.SHOW_MESSAGE:
                    actionType = hextHintType
                    callback = self.getCallbackByName(hextHint)
                    if callback is not None:
                        ctx['removedCallback'] = callback
                else:
                    actionName = hextHint
                showBottomData = True
                showRewardMessage = True
                if not self.bootcampCtrl.needAwarding():
                    showBottomData = not bool(message[ACTION_PARAM.ONLY_FIRST_BOOTCAMP_BOTTOM])
                    showRewardMessage = not bool(message[ACTION_PARAM.ONLY_FIRST_BOOTCAMP])
                if showRewardMessage:
                    ctx['messages'].append(self._createMessageContext(message, showBottomData))
                if callback is not None:
                    callback()
                    return

            self.suspendLesson()
            g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BOOTCAMP_MESSAGE_WINDOW, None, ctx), EVENT_BUS_SCOPE.LOBBY)
            return

    def showElement(self, actionName):
        if actionName is None or actionName in self.__showActionsHistory:
            return
        else:
            self.__showActionsHistory.append(actionName)
            showAction = self.__bootcampGarageActions.getActionByName(actionName)
            voiceover = showAction.get(ACTION_PARAM.VOICEOVER, '')
            if voiceover:
                SoundGroups.g_instance.playSound2D(voiceover)
            hextHint = showAction[ACTION_PARAM.NEXT_HINT]
            callback = None
            if hextHint:
                callback = self.getCallbackByName(hextHint)
            showElements = showAction[ACTION_PARAM.SHOW].split(' ')
            if showElements:
                self.showGarageGUIElements(showElements, callback)
            if showAction[ACTION_PARAM.FORCE]:
                self.showNextHint()
            else:
                self.suspendLesson()
            return

    def highlightButton(self, actionName, hideHint=False):
        if actionName is None:
            return
        else:
            highlight = self.__bootcampGarageActions.getActionByName(actionName)
            hintAction = events.BootcampEvent.REMOVE_HIGHLIGHT
            highlightElement = highlight[ACTION_PARAM.ELEMENT]
            if not hideHint:
                hintAction = events.BootcampEvent.ADD_HIGHLIGHT
                self.__prevHint = actionName
                self.__nextHint = highlight[ACTION_PARAM.NEXT_HINT]
                self.__hardcodeHint = None
            g_eventBus.handleEvent(events.LoadViewEvent(hintAction, None, highlightElement), EVENT_BUS_SCOPE.LOBBY)
            if highlight[ACTION_PARAM.FORCE]:
                self.showNextHint()
            return

    def conditionalAction(self, actionName):
        action = self.__bootcampGarageActions.getActionByName(actionName)
        condition = action['show_condition']['condition']
        nationData = self.getNationData()
        if condition.checkCondition(nationData) == action['show_condition']['result']:
            conditionalAction = action[ACTION_PARAM.CONDITIONAL_ACTION]
            callbackAction = self.getCallbackByName(conditionalAction)
            callbackAction()
            return
        else:
            nextHint = action[ACTION_PARAM.NEXT_HINT]
            callback = self.getCallbackByName(nextHint)
            if callback is not None:
                callback()
            return

    def preprocessBottomData(self, data):
        ctx = g_bootcamp.getContext()
        if data.get('label_format', None) is not None:
            if 'bonuses' in ctx:
                lessonBonuses = ctx['bonuses']['battle'][self.__lessonId - 1]
                labelFormat = data['label_format']
                if labelFormat == 'getCredits':
                    nationId = ctx['nation']
                    nationsData = lessonBonuses.get('nations', None)
                    if nationsData is not None:
                        formatedValue = BigWorld.wg_getIntegralFormat(nationsData[NATION_NAMES[nationId]]['credits']['win'][0])
                        data['label'] = data['label'].format(formatedValue)
                elif labelFormat == 'getExperience':
                    nationId = ctx['nation']
                    nationsData = lessonBonuses.get('nations', None)
                    if nationsData is not None:
                        formatedValue = BigWorld.wg_getIntegralFormat(nationsData[NATION_NAMES[nationId]]['xp']['win'][0])
                        data['label'] = data['label'].format(formatedValue)
                elif labelFormat == 'getGold':
                    data['label'] = data['label'].format(lessonBonuses['gold'])
                elif labelFormat == 'getPremiumHours':
                    hours = lessonBonuses['premium']
                    timeInSeconds = hours * time_utils.ONE_HOUR
                    if timeInSeconds > time_utils.ONE_DAY:
                        time = ceil(timeInSeconds / time_utils.ONE_DAY)
                        timeMetric = i18n.makeString('#menu:header/account/premium/days')
                    else:
                        time = ceil(timeInSeconds / time_utils.ONE_HOUR)
                        timeMetric = i18n.makeString('#menu:header/account/premium/hours')
                    data['label'] = data['label'].format(str(int(time)) + ' ' + timeMetric)
                elif labelFormat == 'getRepairKits':
                    data['label'] = data['label'].format(lessonBonuses['equipment']['largeRepairkit']['count'])
                elif labelFormat == 'getFirstAid':
                    data['label'] = data['label'].format(lessonBonuses['equipment']['largeMedkit']['count'])
                elif labelFormat == 'getFireExtinguisher':
                    data['label'] = data['label'].format(lessonBonuses['equipment']['handExtinguishers']['count'])
        data['label'] = makeString(data['label'])
        data['description'] = makeString(data['description'])
        data['content_data'] = None
        return

    def startLobbyAssistance(self):
        if self.__lobbyAssistant is None:
            from Assistant import LobbyAssistant
            hints = {}
            if self.bootcampCtrl.getLessonNum() == 1:
                hints = {'hintRotateLobby': {'time_completed': 3.0,
                                     'timeout': 1.0,
                                     'angle': 180.0,
                                     'cooldown_after': 0.0,
                                     'message': ''}}
            self.__lobbyAssistant = LobbyAssistant(hints)
            self.__lobbyAssistant.start()
        return

    def stopLobbyAssistance(self):
        if self.__lobbyAssistant is not None:
            self.__lobbyAssistant.stop()
            self.__lobbyAssistant = None
        return

    def updateLobbyLobbySettings(self, elementsList, isHide=False):
        if elementsList is not None:
            for element in elementsList:
                elementHide = getBootcampInternalHideElementName(element)
                self.bootcampCtrl.updateLobbySettingsVisibility(elementHide, isHide)

        return

    def changeGarageGUIElementsVisibility(self, elementsList, isHide, update=True):
        lobbySettings = self.bootcampCtrl.getLobbySettings()
        self.updateLobbyLobbySettings(elementsList, isHide)
        if update:
            g_eventBus.handleEvent(events.LoadViewEvent(events.BootcampEvent.SET_VISIBLE_ELEMENTS, None, lobbySettings), EVENT_BUS_SCOPE.LOBBY)
        return

    def disableGarageGUIElements(self, elementsList):
        self.changeGarageGUIElementsVisibility(elementsList, True)

    def enableGarageGUIElements(self, elementsList):
        self.changeGarageGUIElementsVisibility(elementsList, False)

    def showGarageGUIElements(self, elementsList, callback):
        self.startLobbyAssistance()
        LOG_DEBUG_DEV_BOOTCAMP('showGarageGUIElements', elementsList)
        g_eventBus.handleEvent(events.LoadViewEvent(events.BootcampEvent.SHOW_NEW_ELEMENTS, None, {'keys': elementsList,
         'callback': callback}), EVENT_BUS_SCOPE.LOBBY)
        self.changeGarageGUIElementsVisibility(elementsList, False, update=False)
        return

    def showNextHint(self):
        self.__showHint(self.__nextHint)

    def showPrevHint(self):
        self.__showHint(self.__prevHint)

    def getPrevHint(self):
        return self.__prevHint

    def hideHint(self):
        if self.__prevHint is not None:
            LOG_DEBUG_DEV_BOOTCAMP('hideHint - {0}'.format(self.__prevHint))
            callback = self.getCallbackByName(self.__prevHint)
            self.__prevHint = None
            if callback is not None:
                callback(True)
        return

    def hidePrevShowNextHint(self):
        self.hideHint()
        self.showNextHint()

    def suspendLesson(self):
        self.isLessonSuspended = True
        self.hideAllHints()

    def resumeLesson(self):
        self.isLessonSuspended = False

    def highlightLobbyHint(self, lobbyHint, isShow=True, isForce=False):
        newHardcodeHint = lobbyHint if isShow else None
        if not self.isLessonSuspended and newHardcodeHint != self.__hardcodeHint or isForce:
            if isShow:
                self.hideAllHints()
            self.__hardcodeHint = newHardcodeHint
            actionType = events.BootcampEvent.REMOVE_HIGHLIGHT
            if isShow:
                actionType = events.BootcampEvent.ADD_HIGHLIGHT
            g_eventBus.handleEvent(events.LoadViewEvent(actionType, None, lobbyHint), EVENT_BUS_SCOPE.LOBBY)
        return

    def setBattleSelectorHintText(self):
        if self.__battleSelectorHintPointcutIndex is None:
            self.__battleSelectorHintPointcutIndex = g_bootcamp.addPointcut(PointcutBattleSelectorHintText)
            g_eventDispatcher.updateUI()
        return

    def removeBattleSelectorHintText(self):
        if self.__battleSelectorHintPointcutIndex is not None:
            g_bootcamp.removePointcut(self.__battleSelectorHintPointcutIndex)
            self.__battleSelectorHintPointcutIndex = None
            g_eventDispatcher.updateUI()
        return

    def showBootcampGraduateMessage(self):
        self.resumeLesson()
        self.runCustomAction('msgBootcampGraduate')

    def toDefaultAccount(self):
        self.clear()
        g_bootcampEvents.onRequestBootcampFinish()

    def finishBootcamp(self):
        Waiting.show('login')
        self.clear()
        g_bootcampEvents.onGarageLessonFinished(self.__lessonId)
        self.toDefaultAccount()
        g_bootcampEvents.onEnterPreview -= self.onEnterPreview
        g_bootcampEvents.onExitPreview -= self.onExitPreview

    def onEnterPreview(self):
        self.__isInPreview = True

    def onExitPreview(self):
        self.__isInPreview = False
        self.showPrevHint()

    def isInPreview(self):
        return self.__isInPreview

    def showFinalVideo(self):
        g_bootcamp.showFinalVideo()

    def getNationData(self):
        return g_bootcamp.getNationData()

    def getNation(self):
        return self.bootcampCtrl.nation

    def getSecondVehicleInvId(self):
        """ Returns inventory ID of the second vehicle that the player must purchase according to Bootcamp flow.
        
        :return: None if inventory cache is not synced yet,
                 -1 if there is no second vehicle in inventory,
                 valid inventory ID otherwise.
        """
        return self.__secondVehicleInvID

    def isSecondVehicleSelected(self):
        invID = self.getSecondVehicleInvId()
        if invID is None:
            return False
        elif invID == -1:
            return True
        else:
            from CurrentVehicle import g_currentVehicle
            return invID == g_currentVehicle.invID

    @async
    @process
    def isSecondVehicleSelectedAsync(self, callback):
        yield self.__waitForItemCacheSync()
        callback(self.isSecondVehicleSelected())

    @process
    def selectLessonVehicle(self):
        selected = yield self.isSecondVehicleSelectedAsync()
        if not selected:
            invID = self.getSecondVehicleInvId()
            assert invID is not None
            from CurrentVehicle import g_currentVehicle
            g_currentVehicle.selectVehicle(invID)
        return

    def checkReturnToHangar(self):
        if self.isLessonSuspended:
            g_bootcampGarage.highlightLobbyHint('HangarButton', True, True)
        elif self.isLessonFinished:
            if self.canGoToBattle:
                LOG_DEBUG_DEV_BOOTCAMP("checkReturnToHangar - hiding 'HangarButton' highlight (isLessonFinished and canGoToBattle)")
                g_bootcampGarage.highlightLobbyHint('HangarButton', False, True)
            else:
                LOG_DEBUG_DEV_BOOTCAMP("checkReturnToHangar - highlighting 'HangarButton' (isLessonFinished and not canGoToBattle)")
                g_bootcampGarage.highlightLobbyHint('HangarButton', True, True)
        elif self.__lessonId == g_bootcamp.getContextIntParameter('randomBattleLesson'):
            name = 'hideHeaderBattleSelector'
            if name in self.bootcampCtrl.getLobbySettings():
                if self.bootcampCtrl.getLobbySettings()[name]:
                    g_bootcampGarage.highlightLobbyHint('HangarButton', True, True)
                    return
            try:
                items = battle_selector_items.getItems()
                if not items.isSelected('random'):
                    return
            except:
                LOG_CURRENT_EXCEPTION_BOOTCAMP()
                LOG_ERROR_BOOTCAMP('battle_selector_items exception')

            g_bootcampGarage.highlightLobbyHint('HangarButton', True, True)
        else:
            g_bootcampGarage.highlightLobbyHint('HangarButton', True, True)

    @process
    def hideExcessElements(self):
        selected = yield self.isSecondVehicleSelectedAsync()
        if not selected:
            excessElements = ['HangarEquipment',
             'HangarOptionalDevices',
             'HangarQuestControl',
             'HeaderBattleSelector']
            self.disableGarageGUIElements(excessElements)
            g_bootcampEvents.onRequestCloseTechnicalMaintenance()

    @process
    def checkSecondVehicleHintEnabled(self):
        self.hideExcessElements()
        selected = yield self.isSecondVehicleSelectedAsync()
        if selected:
            self.highlightLobbyHint('SecondTank', False, True)
            self.enableCheckpointGUI()
            self.resumeLesson()
            self.runCheckpoint()
            self.runViewAlias(VIEW_ALIAS.LOBBY_HANGAR)
        else:
            g_bootcampEvents.onBattleNotReady()
            self.suspendLesson()
            self.highlightLobbyHint('SecondTank', True, True)

    def getBattleResultsExtra(self, lessonId):
        return self.__bootcampGarageActions.getBattleResultsById(lessonId)

    def updateNode(self, node):
        node.setState(NODE_STATE_FLAGS.UNLOCKED)

    def setSecondVehicleNode(self, secondVehicleNode):
        self.updateNode(secondVehicleNode)
        secondVehicleNode.setState(NODE_STATE.addIfNot(secondVehicleNode.getState(), NODE_STATE_FLAGS.WAS_IN_BATTLE))

    def setModuleNode(self, moduleNode):
        self.updateNode(moduleNode)
        moduleNode.setState(NODE_STATE.addIfNot(moduleNode.getState(), NODE_STATE_FLAGS.IN_INVENTORY))

    def initSubscriptions(self):
        self.itemsCache.onSyncCompleted += self.__onItemCacheSyncCompleted

    def destroySubscriptions(self):
        self.itemsCache.onSyncCompleted -= self.__onItemCacheSyncCompleted

    def disableResearchButton(self):
        g_bootcampEvents.onRequestChangeResearchButtonState(False)

    def enableResearchButton(self):
        g_bootcampEvents.onRequestChangeResearchButtonState(True)

    def disableVehiclePreviewBuyButton(self):
        g_bootcampEvents.onRequestChangeVehiclePreviewBuyButtonState(False)

    def enableVehiclePreviewBuyButton(self):
        g_bootcampEvents.onRequestChangeVehiclePreviewBuyButtonState(True)

    def _createMessageContext(self, message, showBottomData):
        nationId = self.getNation()
        messageNation = message[ACTION_PARAM.NATIONS_DATA][NATION_NAMES[nationId]]
        m_ctx = {'messagePreset': BOOTCAMP_MESSAGE_WINDOW[messageNation[ACTION_PARAM.PRESET]],
         'label': makeString(messageNation[ACTION_PARAM.LABEL]),
         'iconPath': messageNation[ACTION_PARAM.ICON],
         'message': ''}
        if showBottomData:
            m_ctx['message'] = makeString(messageNation[ACTION_PARAM.TEXT])
        if messageNation[ACTION_PARAM.BACKGROUND]:
            m_ctx[ACTION_PARAM.BACKGROUND] = messageNation[ACTION_PARAM.BACKGROUND]
        if messageNation[ACTION_PARAM.BOTTOM_RENDERER] != -1 and showBottomData:
            bottomRenderer = MESSAGE_BOTTOM_RENDERER[messageNation[ACTION_PARAM.BOTTOM_RENDERER]]
            m_ctx['bottomRenderer'] = bottomRenderer
            m_ctx['bottomData'] = []
            for bottom in messageNation['bottom']:
                processedBottom = dict(bottom)
                self.preprocessBottomData(processedBottom)
                bottomDataElement = {'label': processedBottom['label'],
                 'icon': processedBottom['icon'],
                 'description': processedBottom['description'],
                 'contentData': processedBottom['content_data'],
                 'iconTooltip': processedBottom['iconTooltip'],
                 'labelTooltip': processedBottom['labelTooltip']}
                m_ctx['bottomData'].append(bottomDataElement)

        return m_ctx

    def __showHint(self, hintName):
        if hintName is not None:
            LOG_DEBUG_DEV_BOOTCAMP('showNextHint - {0}'.format(hintName))
            callback = self.getCallbackByName(hintName)
            if callback is not None:
                callback()
        return

    @async
    def __waitForItemCacheSync(self, callback):
        if self.itemsCache.isSynced():
            callback(True)
        else:
            self.__itemCacheSyncCallbacks.append(lambda : callback(self.itemsCache.isSynced()))

    def __onItemCacheSyncCompleted(self, *_):
        self.__updateSecondVehicleInvID()
        callbacks = self.__itemCacheSyncCallbacks
        self.__itemCacheSyncCallbacks = []
        for callback in callbacks:
            callback()

        BigWorld.callback(0.01, self.__processDeferredAliases)

    def __updateSecondVehicleInvID(self):
        if self.itemsCache.isSynced():
            nationData = self.getNationData()
            vehicleCD = nationData['vehicle_second']
            vehicle = self.itemsCache.items.getItemByCD(vehicleCD)
            self.__secondVehicleInvID = vehicle.invID

    def __processDeferredAliases(self):
        for alias in self.__deferredAliases:
            self.runViewAlias(alias)

        del self.__deferredAliases[:]


g_bootcampGarage = BootcampGarageLesson()
