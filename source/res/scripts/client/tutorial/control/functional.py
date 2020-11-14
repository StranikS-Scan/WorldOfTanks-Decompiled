# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/functional.py
import re
import BigWorld
import Event
from helpers import dependency
from tutorial.control import TutorialProxyHolder, game_vars
from tutorial.control.context import GlobalStorage
from tutorial.data import chapter
from tutorial.data.conditions import CONDITION_TYPE
from tutorial.gui import GUI_EFFECT_NAME
from tutorial.logger import LOG_ERROR, LOG_DEBUG
from gui.prb_control.events_dispatcher import g_eventDispatcher as prebattleControl
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from skeletons.gui.shared import IItemsCache
from skeletons.account_helpers.settings_core import ISettingsCore
from CurrentVehicle import g_currentVehicle

class FunctionalCondition(TutorialProxyHolder):

    def isConditionOk(self, condition):
        return False


class FunctionalFlagCondition(FunctionalCondition):

    def isConditionOk(self, condition):
        result = self._tutorial.getFlags().isActiveFlag(condition.getID())
        return result if condition.isPositiveState() else not result


class FunctionalGlobalFlagCondition(FunctionalCondition):

    def isConditionOk(self, condition):
        result = GlobalStorage(condition.getID(), False).value()
        return result if condition.isPositiveState() else not result


class FunctionalWindowOnSceneCondition(FunctionalCondition):

    def isConditionOk(self, condition):
        result = self._gui.isTutorialWindowDisplayed(condition.getID())
        return result if condition.isPositiveState() else not result


class FunctionalComponentOnSceneCondition(FunctionalCondition):

    def isConditionOk(self, condition):
        itemsOnScene = self._gui.getItemsOnScene()
        result = condition.getID() in itemsOnScene
        return result if condition.isPositiveState() else not result


class FunctionalCurrentSceneCondition(FunctionalCondition):

    def isConditionOk(self, condition):
        currentSceneID = self._gui.getSceneID()
        result = currentSceneID == condition.getID()
        return result if condition.isPositiveState() else not result


class FunctionalViewPresentCondition(FunctionalCondition):

    def isConditionOk(self, condition):
        layer = condition.getLayer()
        viewAlias = condition.getViewAlias()
        result = self._gui.isViewPresent(layer, criteria={POP_UP_CRITERIA.VIEW_ALIAS: viewAlias})
        return result if condition.isPositiveState() else not result


class FunctionalConnectedItemCondition(FunctionalCondition):
    __settingsCore = dependency.descriptor(ISettingsCore)

    def isConditionOk(self, condition):
        shownHints = self.__settingsCore.serverSettings.getOnceOnlyHintsSettings()
        isHintShown = shownHints.get(condition.getID(), None)
        if isHintShown is None:
            LOG_DEBUG('invalid hintID in condition: ', condition.getID())
            return False
        else:
            return False if isHintShown != condition.isShown() else True


class FunctionalComplexConditionAnd(FunctionalCondition):

    def isConditionOk(self, conditions):
        return FunctionalConditions(conditions.getConditionList()).evaluateWithAND()


class FunctionalComplexConditionOr(FunctionalCondition):

    def isConditionOk(self, conditions):
        return FunctionalConditions(conditions.getConditionList()).evaluateWithOR()


class FunctionalVarDefinedCondition(FunctionalCondition):

    def isConditionOk(self, condition):
        variables = self._tutorial.getVars()
        value = variables.get(condition.getID(), default=None)
        if condition.isPositiveState():
            result = value is not None
        else:
            result = value is None
        return result


class FunctionalVarCompareCondition(FunctionalCondition):

    def isConditionOk(self, condition):
        variables = self._tutorial.getVars()
        value = variables.get(condition.getID(), default=None)
        other = variables.get(condition.getCompareID(), default=None)
        if condition.isPositiveState():
            result = value == other
        else:
            result = value != other
        return result


class FunctionalEffectTriggeredCondition(FunctionalCondition):

    def isConditionOk(self, condition):
        result = self._tutorial.isEffectTriggered(condition.getID())
        return result if condition.isPositiveState() else not result


class FunctionalGameItemSimpleStateCondition(FunctionalCondition):

    def isConditionOk(self, condition):
        getter = game_vars.getItemStateGetter(condition.getBaseState())
        if getter:
            varID = condition.getID()
            value = self._tutorial.getVars().get(varID, default=varID)
            try:
                result = getter(value)
            except Exception as e:
                LOG_ERROR('Can not resolve condition', varID, e.message)
                return False

            if condition.isPositiveState():
                return result
            return not result
        LOG_ERROR('State of item can not be resolved', condition)
        return False


class FunctionalGameItemRelateStateCondition(FunctionalCondition):

    def isConditionOk(self, condition):
        getter = game_vars.getItemStateGetter(condition.getBaseState())
        if getter:
            tvars = self._tutorial.getVars()
            varID = condition.getID()
            value = tvars.get(varID, default=varID)
            otherIDs = (tvars.get(x, default=x) for x in condition.getOtherIDs())
            try:
                result = getter(value, *otherIDs)
            except Exception as e:
                LOG_ERROR('Can not resolve condition', varID, e.message)
                return False

            if condition.isPositiveState():
                return result
            return not result
        LOG_ERROR('State of item can not be resolved', condition)
        return False


class FunctionalBonusReceivedCondition(FunctionalCondition):

    def isConditionOk(self, condition):
        chapterItem = self._descriptor.getChapter(condition.getID())
        if chapterItem is None:
            chapterID = self._tutorial.getVars().get(condition.getID())
            chapterItem = self._descriptor.getChapter(chapterID)
        if chapterItem is None:
            LOG_ERROR('Chapter is not found', condition.getID())
            return False
        else:
            result = chapterItem.isBonusReceived(self._bonuses.getCompleted())
            return result if condition.isPositiveState() else not result


class FunctionalServiceCondition(FunctionalCondition):

    def isConditionOk(self, condition):
        serviceClass = condition.getServiceClass()
        if serviceClass is None:
            LOG_ERROR('Service cannot be loaded!', condition.getID(), condition.getPath())
            return False
        else:
            service = dependency.instance(serviceClass)
            if not hasattr(service, 'isEnabled'):
                LOG_ERROR('Service does not implement isEnabled method!', service)
                return False
            result = service.isEnabled()
            return result if condition.isPositiveState() else not result


class FunctionalClassCondition(FunctionalCondition):

    def isConditionOk(self, condition):
        conditionClass = condition.getConditionClass()
        if conditionClass is None:
            LOG_ERROR('Condition cannot be loaded!', condition.getID(), condition.getPath())
            return False
        else:
            conditionInstance = conditionClass()
            if not hasattr(conditionInstance, 'check'):
                LOG_ERROR('Condition does not implement check method!', conditionInstance)
                return False
            result = conditionInstance.check(condition.getArguments())
            return result if condition.isPositiveState() else not result


_SUPPORTED_CONDITIONS = {CONDITION_TYPE.FLAG: FunctionalFlagCondition,
 CONDITION_TYPE.GLOBAL_FLAG: FunctionalGlobalFlagCondition,
 CONDITION_TYPE.WINDOW_ON_SCENE: FunctionalWindowOnSceneCondition,
 CONDITION_TYPE.VAR_DEFINED: FunctionalVarDefinedCondition,
 CONDITION_TYPE.VAR_COMPARE: FunctionalVarCompareCondition,
 CONDITION_TYPE.EFFECT_TRIGGERED: FunctionalEffectTriggeredCondition,
 CONDITION_TYPE.GAME_ITEM_SIMPLE_STATE: FunctionalGameItemSimpleStateCondition,
 CONDITION_TYPE.GAME_ITEM_RELATE_STATE: FunctionalGameItemRelateStateCondition,
 CONDITION_TYPE.BONUS_RECEIVED: FunctionalBonusReceivedCondition,
 CONDITION_TYPE.SERVICE: FunctionalServiceCondition,
 CONDITION_TYPE.CLASS_CONDITION: FunctionalClassCondition,
 CONDITION_TYPE.COMPONENT_ON_SCENE: FunctionalComponentOnSceneCondition,
 CONDITION_TYPE.CURRENT_SCENE: FunctionalCurrentSceneCondition,
 CONDITION_TYPE.VIEW_PRESENT: FunctionalViewPresentCondition,
 CONDITION_TYPE.CONNECTED_ITEM: FunctionalConnectedItemCondition,
 CONDITION_TYPE.CONDITION_AND: FunctionalComplexConditionAnd,
 CONDITION_TYPE.CONDITION_OR: FunctionalComplexConditionOr}

def _areAllConditionsOk(item):
    return FunctionalConditions(item.getConditions()).allConditionsOk()


class FunctionalConditions(TutorialProxyHolder):

    def __init__(self, conditions):
        super(FunctionalConditions, self).__init__()
        self._conditions = conditions

    def allConditionsOk(self):
        if self._conditions is None:
            return True
        else:
            ok = self.evaluateWithAND()
            for eitherCondition in self._conditions.eitherBlocks():
                if ok:
                    ok = FunctionalConditions(eitherCondition).evaluateWithOR()

            return ok

    def evaluateWithAND(self):
        if self._conditions is None:
            return True
        else:
            result = True
            for condition in self._conditions:
                if result:
                    result = self.isConditionActive(condition)

            return result

    def evaluateWithOR(self):
        if self._conditions is None:
            return True
        else:
            result = False
            for condition in self._conditions:
                if not result:
                    result = self.isConditionActive(condition)

            return result

    def isConditionActive(self, condition):
        functional = None
        if self._tutorial is not None:
            functional = self._ctrlFactory.createCustomFuncCondition(condition)
        if functional is None:
            condType = condition.getType()
            if condType in _SUPPORTED_CONDITIONS:
                functional = _SUPPORTED_CONDITIONS[condType]
                functional = functional()
            else:
                LOG_ERROR('Condition is not found', condType)
                functional = FunctionalCondition()
        return functional.isConditionOk(condition)


class FunctionalVarSet(object):

    def __init__(self, varSet):
        super(FunctionalVarSet, self).__init__()
        self._varSet = varSet

    def getFirstActual(self):
        if self._varSet is None:
            return
        else:
            for var, conditions in self._varSet:
                result = FunctionalConditions(conditions).allConditionsOk()
                if result:
                    return var

            return


class FunctionalEffect(TutorialProxyHolder):

    def __init__(self, effect):
        super(FunctionalEffect, self).__init__()
        self._effect = effect
        self.__isGlobal = False

    def setGlobal(self, isGlobal):
        self.__isGlobal = isGlobal

    def isGlobal(self):
        return self.__isGlobal

    def triggerEffect(self):
        raise NotImplementedError('method triggerEffect is not implemented')

    def getEffect(self):
        return self._effect

    def getTargetID(self):
        return self._effect.getTargetID()

    def getTarget(self):
        targetID = self.getTargetID()
        return self._data.getHasIDEntity(targetID)

    def isInstantaneous(self):
        return True

    def isStillRunning(self):
        return False

    def stop(self):
        pass

    def isAllConditionsOK(self):
        result = True
        return FunctionalConditions(self._effect.getConditions()).allConditionsOk() if self._effect is not None else result


class FunctionalEffectsGroup(FunctionalEffect):

    def triggerEffect(self):
        effects = filter(_areAllConditionsOk, self._effect.getEffects())
        if effects:
            self._tutorial.storeEffectsInQueue(effects, benefit=True, isGlobal=self.isGlobal())
        return True


class FunctionalActivateEffect(FunctionalEffect):

    def triggerEffect(self):
        targetID = self._effect.getTargetID()
        flags = self._tutorial.getFlags()
        if not flags.isActiveFlag(targetID):
            flags.activateFlag(targetID)
            LOG_DEBUG('invalidateFlags from FunctionalActivateEffect', targetID)
            self._tutorial.invalidateFlags()
        return True


class FunctionalDeactivateEffect(FunctionalEffect):

    def triggerEffect(self):
        targetID = self._effect.getTargetID()
        flags = self._tutorial.getFlags()
        if flags.isActiveFlag(targetID):
            flags.deactivateFlag(targetID)
            LOG_DEBUG('invalidateFlags from FunctionalDeactivateEffect', targetID)
            self._tutorial.invalidateFlags()
        return True


class FunctionalGlobalActivateEffect(FunctionalEffect):

    def triggerEffect(self):
        GlobalStorage.setValue(self._effect.getTargetID(), True)
        return True


class FunctionalGlobalDeactivateEffect(FunctionalEffect):

    def triggerEffect(self):
        GlobalStorage.setValue(self._effect.getTargetID(), False)
        return True


class FunctionalRefuseTrainingEffect(FunctionalEffect):

    def triggerEffect(self):
        self._tutorial.refuse()
        return True

    def isStillRunning(self):
        return True

    def isInstantaneous(self):
        return False


class FunctionalNextChapterEffect(FunctionalEffect):

    def triggerEffect(self):
        nextChapter = self._effect.getTargetID()
        if not nextChapter:
            nextChapter = self._descriptor.getInitialChapterID(completed=self._bonuses.getCompleted())
        if self._tutorial._currentChapter != nextChapter:
            self._gui.showWaiting('chapter-loading', isSingle=True)
            self._gui.clear()
            self._tutorial.goToNextChapter(nextChapter)
        return True


class FunctionalRunTriggerEffect(FunctionalEffect):

    def isInstantaneous(self):
        return False

    def isStillRunning(self):
        trigger = self.getTarget()
        return trigger.isRunning if trigger is not None else False

    def triggerEffect(self):
        trigger = self.getTarget()
        if trigger is not None:
            trigger.run()
            return True
        else:
            LOG_ERROR('Trigger not found', self._effect.getTargetID())
            return False

    def getTarget(self):
        return self._data.getTrigger(self._effect.getTargetID())


class FunctionalRequestBonusEffect(FunctionalEffect):

    def isInstantaneous(self):
        return False

    def isStillRunning(self):
        return self._bonuses.isStillRunning()

    def triggerEffect(self):
        self._bonuses.request(chapterID=self._effect.getTargetID())
        return True


class FunctionalSetGuiItemPropertiesEffect(FunctionalEffect):

    def triggerEffect(self):
        itemID = self._effect.getTargetID()
        props = self._effect.getProps()
        return self._gui.playEffect(GUI_EFFECT_NAME.SET_ITEM_PROPS, (itemID, props))


class FunctionalFinishTrainingEffect(FunctionalEffect):

    def triggerEffect(self):
        self._tutorial.stop(finished=True)
        return True

    def isStillRunning(self):
        return True

    def isInstantaneous(self):
        return False


class FunctionalGuiCommandEffect(FunctionalEffect):

    def triggerEffect(self):
        targetID = self._effect.getTargetID()
        command = self._gui.config.getCommand(targetID)
        if command is not None:
            argOverrides = self._effect.getArgOverrides()
            if argOverrides:
                if isinstance(command.args, dict):
                    newArgs = command.args.copy()
                    newArgs.update(argOverrides)
                    command = command._replace(args=newArgs)
                else:
                    LOG_ERROR('cannot override GUI command args by name: arg list was not defined as dict', targetID)
            self._gui.invokeCommand(command)
            return True
        else:
            LOG_ERROR('Command not found', targetID)
            return False


class FunctionalPlayerCommandEffect(FunctionalEffect):

    def triggerEffect(self):
        command = self.getTarget()
        if command is not None:
            player = BigWorld.player()
            attr = getattr(player, command.getName(), None)
            if attr is not None and callable(attr):
                try:
                    attr(*command.args(), **command.kwargs())
                    return True
                except TypeError:
                    LOG_ERROR('Number of arguments mismatch', command.getName(), command.args(), command.kwargs())

            else:
                LOG_ERROR('Player has not method', command.getName())
        else:
            LOG_ERROR('Command not found', self._effect.getTargetID())
        return False


class FunctionalShowDialogEffect(FunctionalEffect):

    def __init__(self, effect):
        super(FunctionalShowDialogEffect, self).__init__(effect)
        self._isRunning = False

    def triggerEffect(self):
        self._gui.release()
        dialog = self.getTarget()
        if dialog is not None:
            content = dialog.getContent()
            if not dialog.isContentFull():
                query = self._ctrlFactory.createContentQuery(dialog.getType())
                query.invoke(content, dialog.getVarRef())
            self._isRunning = self._gui.playEffect(GUI_EFFECT_NAME.SHOW_DIALOG, [content])
            if not self._isRunning:
                LOG_ERROR('Can not play effect "ShowDialog"', dialog.getID(), dialog.getType())
        else:
            LOG_ERROR('Dialog not found', self._effect.getTargetID())
            self._isRunning = False
        return self._isRunning

    def isInstantaneous(self):
        return False

    def isStillRunning(self):
        if self._isRunning and not self._gui.isTutorialDialogDisplayed(self._effect.getTargetID()):
            self._isRunning = False
        return self._isRunning


class FunctionalShowWindowEffect(FunctionalEffect):

    def __init__(self, effect):
        self._isRunning = False
        super(FunctionalShowWindowEffect, self).__init__(effect)

    def triggerEffect(self):
        self._gui.release()
        isRunning = False
        window = self.getTarget()
        if window is not None:
            content = window.getContent()
            if not window.isContentFull():
                query = self._ctrlFactory.createContentQuery(window.getType())
                query.invoke(content, window.getVarRef())
            self._setActions(window)
            isRunning = self._gui.playEffect(GUI_EFFECT_NAME.SHOW_WINDOW, [window.getID(), window.getType(), content])
            if not isRunning:
                LOG_ERROR('Can not play effect "ShowWindow"', window.getID(), window.getType())
        else:
            LOG_ERROR('PopUp not found', self._effect.getTargetID())
        return isRunning

    def _setActions(self, window):
        self._tutorial.getFunctionalScene().setActions(window.getActions())


class FunctionalShowMessageEffect(FunctionalEffect):

    def triggerEffect(self):
        message = self.getTarget()
        if message is not None:
            self._gui.showMessage(message.getText(), lookupType=message.getGuiType())
            return True
        else:
            LOG_ERROR('Message not found', self._effect.getTargetID())
            return False


_var_search = re.compile('(\\$.*?(.+?)\\$)')

class FunctionalSetGuiItemCriteria(FunctionalEffect):

    def triggerEffect(self):
        criteria = self.getTarget()
        if criteria is None:
            LOG_ERROR('Criteria is not found', self._effect.getTargetID())
            return False
        else:
            value = criteria.getValue()
            getVar = self._tutorial.getVars().get
            for marker, varID in re.findall(_var_search, value):
                value = value.replace(marker, str(getVar(varID)))

            return self._playEffect(criteria, value)

    def _playEffect(self, criteria, value):
        LOG_DEBUG('Set gui item criteria', criteria.getTargetID(), value)
        return self._gui.playEffect(GUI_EFFECT_NAME.SET_CRITERIA, (criteria.getTargetID(), value))


class FunctionalSetGuiItemViewCriteria(FunctionalSetGuiItemCriteria):

    def _playEffect(self, criteria, value):
        LOG_DEBUG('Set gui item view criteria', criteria.getComponentIDs(), value)
        return self._gui.playEffect(GUI_EFFECT_NAME.SET_VIEW_CRITERIA, (criteria.getComponentIDs(), value))


class FunctionalSetAction(FunctionalEffect):

    def triggerEffect(self):
        action = self.getTarget()
        if action is None:
            LOG_ERROR('Action is not found', self._effect.getTargetID())
            return False
        else:
            scope = self._funcChapterCtx if self.isGlobal() else self._funcScene
            if scope is None:
                LOG_ERROR('Scope (scene / chapter) is not available', self._effect.getTargetID())
                return False
            scope.setAction(action)
            return self._gui.playEffect(GUI_EFFECT_NAME.SET_TRIGGER, (action.getTargetID(), action.getType()))


class FunctionalRemoveAction(FunctionalEffect):

    def triggerEffect(self):
        action = self.getTarget()
        if action is None:
            LOG_ERROR('Action is not found', self._effect.getTargetID())
            return False
        else:
            scope = self._funcChapterCtx if self.isGlobal() else self._funcScene
            if scope is None:
                LOG_ERROR('Scope (scene / chapter) is not available', self._effect.getTargetID())
                return False
            scope.removeAction(action)
            self._gui.stopEffect(GUI_EFFECT_NAME.SET_TRIGGER, action.getTargetID(), action.getType())
            return True


class FunctionalSetVarAction(FunctionalEffect):

    def triggerEffect(self):
        finder = self.getTarget()
        if finder is None:
            LOG_ERROR('Var finder is not found', self._effect.getTargetID())
            return False
        else:
            finderType = finder.getType()
            if finderType == chapter.VAR_FINDER_TYPE.GAME_ATTRIBUTE:
                getter = self._tutorial.getVars().get
                args = [ getter(varID, default=varID) for varID in finder.getArgs() ]
                self._tutorial.getVars().set(finder.getTargetID(), game_vars.getAttribute(finder.getName(), *args))
                return True
            LOG_ERROR('Type of setter is not supported', finderType)
            return False


class FunctionalChapterContext(TutorialProxyHolder):

    def __init__(self):
        super(FunctionalChapterContext, self).__init__()
        self._mustBeUpdated = True
        self._updating = False
        self._actions = chapter.ActionsHolder()
        self._allowedToFight = True
        self.onBeforeUpdate = Event.Event()
        self.onAfterUpdate = Event.Event()

    def clear(self):
        self._actions.clear()

    def invalidate(self):
        self._mustBeUpdated = True

    def updatePreScene(self):
        if self._mustBeUpdated:
            self._mustBeUpdated = False
            self._updating = True
            self.onBeforeUpdate()
            self._updateGlobalRuntimeEffects(isPostScene=False)

    def updatePostScene(self):
        if self._updating:
            self._updateGlobalRuntimeEffects(isPostScene=True)
            self._updating = False
            self.onAfterUpdate()

    def getAction(self, event):
        return self._actions.getAction(event)

    def setAction(self, action):
        return self._actions.addAction(action)

    def removeAction(self, action):
        return self._actions.removeAction(action)

    def onItemLost(self, itemID):
        pass

    def onStartLongEffect(self):
        pass

    def isAllowedToFight(self):
        return self._allowedToFight

    def setAllowedToFight(self, allowed):
        if allowed != self._allowedToFight:
            self._allowedToFight = allowed
            prebattleControl.updateUI()

    def _updateGlobalRuntimeEffects(self, isPostScene):
        LOG_DEBUG('updating global runtime effects', '(post-scene)' if isPostScene else '(pre-scene)')
        effects = filter(_areAllConditionsOk, self._data.getGlobalEffects(isPostScene))
        if effects:
            self._tutorial.storeEffectsInQueue(effects, isGlobal=True)


class FunctionalClearScene(FunctionalEffect):

    def triggerEffect(self):
        self._gui.clearScene()
        return True


class FunctionalScene(TutorialProxyHolder):

    def __init__(self, scene):
        super(FunctionalScene, self).__init__()
        LOG_DEBUG('New functional scene', scene.getID())
        self._scene = scene
        self._actions = chapter.ActionsHolder()
        self._itemsOnScene = set()
        self._pending = []
        self._mustBeUpdated = True
        self._isUpdatedOnce = False
        self._gui.lock()

    def enter(self):
        itemsOnScene = self._gui.getItemsOnScene()
        LOG_DEBUG('Enter to scene', self._scene.getID(), itemsOnScene)
        for itemID in itemsOnScene:
            self.addItemOnScene(itemID)

    def leave(self):
        LOG_DEBUG('Leave scene', self._scene.getID())
        for itemID in list(self._itemsOnScene):
            self.removeItemFromScene(itemID)

        if self._mustBeUpdated:
            self._gui.release()
            self._mustBeUpdated = False
        self._actions.clear()
        self._itemsOnScene.clear()
        self._pending = []

    def reload(self):
        pass

    def invalidate(self):
        self._mustBeUpdated = True

    def update(self):
        if self._mustBeUpdated:
            self._mustBeUpdated = False
            self._updateScene()

    def addItemOnScene(self, itemID):
        if itemID in self._itemsOnScene:
            return
        else:
            item = self._scene.getGuiItem(itemID)
            if item is None:
                return
            LOG_DEBUG('GUI item has been added to scene.', itemID)
            self._itemsOnScene.add(itemID)
            effects = filter(_areAllConditionsOk, item.getOnSceneEffects())
            if effects:
                if self._isUpdatedOnce:
                    self._tutorial.storeEffectsInQueue(effects, benefit=True)
                else:
                    self._pending.extend(effects)
            return effects

    def removeItemFromScene(self, itemID):
        if itemID not in self._itemsOnScene:
            return
        else:
            self._itemsOnScene.discard(itemID)
            item = self._scene.getGuiItem(itemID)
            if item is None:
                return
            LOG_DEBUG('GUI item has been removed from scene.', itemID)
            effects = filter(_areAllConditionsOk, item.getNotOnSceneEffects())
            if effects:
                self._tutorial.storeEffectsInQueue(effects)
            return

    def getAction(self, event):
        return self._actions.getAction(event)

    def setAction(self, action):
        return self._actions.addAction(action)

    def removeAction(self, action):
        return self._actions.removeAction(action)

    def setActions(self, actions):
        for action in actions:
            self._actions.addAction(action)

    def _updateScene(self):
        LOG_DEBUG('Update scene.')
        effects = filter(_areAllConditionsOk, self._scene.getEffects())
        if self._pending:
            effects.extend(self._pending)
            self._pending = []
        if effects:
            self._tutorial.storeEffectsInQueue(effects)
        self._isUpdatedOnce = True
        self._gui.release()


class GoToSceneEffect(FunctionalEffect):

    def triggerEffect(self):
        sceneID = self.getTargetID()
        if sceneID is None:
            LOG_ERROR('scene is not found', self._effect.getTargetID())
            return False
        else:
            self._gui.goToScene(sceneID)
            return True


class FunctionalPlayAnimationEffect(FunctionalEffect):

    def isInstantaneous(self):
        return not self._effect.needWaitForFinish()

    def isStillRunning(self):
        return False if self.isInstantaneous() else self._gui.isEffectRunning(GUI_EFFECT_NAME.PLAY_ANIMATION, *self._args)

    def triggerEffect(self):
        self._gui.release()
        return self._gui.playEffect(GUI_EFFECT_NAME.PLAY_ANIMATION, self._args)

    def stop(self):
        self._gui.stopEffect(GUI_EFFECT_NAME.PLAY_ANIMATION, *self._args)

    @property
    def _args(self):
        itemID = self._effect.getTargetID()
        animType = self._effect.getAnimType()
        return (itemID, animType)


class FunctionalSetAllowedToFightEffect(FunctionalEffect):

    def triggerEffect(self):
        self._funcChapterCtx.setAllowedToFight(self._effect.getValue())
        return True


class FunctionalSelectVehicleByCDEffect(FunctionalEffect):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args):
        super(FunctionalSelectVehicleByCDEffect, self).__init__(*args)
        self.__waitingForItemsCacheSync = False

    def triggerEffect(self):
        if self.itemsCache.isSynced():
            return self.__doTrigger()
        self.__waitingForItemsCacheSync = True
        self.itemsCache.onSyncCompleted += self.__doTrigger
        return True

    def isInstantaneous(self):
        return False

    def isStillRunning(self):
        return self.__waitingForItemsCacheSync

    def __doTrigger(self, *_):
        if self.__waitingForItemsCacheSync:
            self.__waitingForItemsCacheSync = False
            self.itemsCache.onSyncCompleted -= self.__doTrigger
        varID = self._effect.getTargetID()
        vehicleCD = self._tutorial.getVars().get(varID, default=None)
        if vehicleCD is None:
            LOG_ERROR('invalid vehicle CD')
            return False
        else:
            vehicle = self.itemsCache.items.getItemByCD(vehicleCD)
            if vehicle is None:
                LOG_ERROR('vehicle not found in inventory')
                return False
            g_currentVehicle.selectVehicle(vehicle.invID)
            return True


class FunctionalPlaySoundEffect(FunctionalEffect):
    itemsCache = dependency.descriptor(IItemsCache)

    def triggerEffect(self):
        soundID = self._effect.getTargetID()
        soundEvent = self._effect.getSoundEvent()
        self._sound.play(soundEvent, soundID)
        return True


class FunctionalCloseViewEffect(FunctionalEffect):

    def triggerEffect(self):
        layer, viewAlias = self._effect.getTargetID()
        self._gui.closeView(layer, criteria={POP_UP_CRITERIA.VIEW_ALIAS: viewAlias})
        return True
