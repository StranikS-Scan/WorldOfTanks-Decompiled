# Embedded file name: scripts/client/tutorial/control/functional.py
import re
import BigWorld
from tutorial.control import TutorialProxyHolder, game_vars
from tutorial.control.context import GlobalStorage
from tutorial.data import chapter
from tutorial.data.conditions import CONDITION_TYPE
from tutorial.gui import GUI_EFFECT_NAME
from tutorial.logger import LOG_ERROR, LOG_DEBUG

class FunctionalCondition(TutorialProxyHolder):

    def isConditionOk(self, condition):
        return False


class FunctionalFlagCondition(FunctionalCondition):

    def isConditionOk(self, condition):
        result = self._tutorial.getFlags().isActiveFlag(condition.getID())
        if condition.isPositiveState():
            return result
        else:
            return not result


class FunctionalGlobalFlagCondition(FunctionalCondition):

    def isConditionOk(self, condition):
        result = GlobalStorage(condition.getID(), False).value()
        if condition.isPositiveState():
            return result
        else:
            return not result


class FunctionalWindowOnSceneCondition(FunctionalCondition):

    def isConditionOk(self, condition):
        result = self._gui.isTutorialWindowDisplayed(condition.getID())
        if condition.isPositiveState():
            return result
        else:
            return not result


class FunctionalVarDefinedCondition(FunctionalCondition):

    def isConditionOk(self, condition):
        vars = self._tutorial.getVars()
        value = vars.get(condition.getID(), default=None)
        if condition.isPositiveState():
            result = value is not None
        else:
            result = value is None
        return result


class FunctionalVarCompareCondition(FunctionalCondition):

    def isConditionOk(self, condition):
        vars = self._tutorial.getVars()
        value = vars.get(condition.getID(), default=None)
        other = vars.get(condition.getCompareID(), default=None)
        if condition.isPositiveState():
            result = value == other
        else:
            result = value != other
        return result


class FunctionalEffectTriggeredCondition(FunctionalCondition):

    def isConditionOk(self, condition):
        result = self._tutorial.isEffectTriggered(condition.getID())
        if condition.isPositiveState():
            return result
        else:
            return not result


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
            else:
                return not result
        else:
            LOG_ERROR('State of item can not be resolved', condition)
        return False


class FunctionalGameItemRelateStateCondition(FunctionalCondition):

    def isConditionOk(self, condition):
        getter = game_vars.getItemStateGetter(condition.getBaseState())
        if getter:
            tvars = self._tutorial.getVars()
            varID = condition.getID()
            value = tvars.get(varID, default=varID)
            otherID = condition.getOtherID()
            other = tvars.get(otherID, default=otherID)
            try:
                result = getter(value, other)
            except Exception as e:
                LOG_ERROR('Can not resolve condition', varID, e.message)
                return False

            if condition.isPositiveState():
                return result
            else:
                return not result
        else:
            LOG_ERROR('State of item can not be resolved', condition)
        return False


class FunctionalBonusReceivedCondition(FunctionalCondition):

    def isConditionOk(self, condition):
        chapter = self._descriptor.getChapter(condition.getID())
        if chapter is None:
            LOG_ERROR('Chapter is not found', condition.getID())
            return False
        else:
            result = chapter.isBonusReceived(self._bonuses.getCompleted())
            if condition.isPositiveState():
                return result
            return not result
            return


_SUPPORTED_CONDITIONS = {CONDITION_TYPE.FLAG: FunctionalFlagCondition,
 CONDITION_TYPE.GLOBAL_FLAG: FunctionalGlobalFlagCondition,
 CONDITION_TYPE.WINDOW_ON_SCENE: FunctionalWindowOnSceneCondition,
 CONDITION_TYPE.VAR_DEFINED: FunctionalVarDefinedCondition,
 CONDITION_TYPE.VAR_COMPARE: FunctionalVarCompareCondition,
 CONDITION_TYPE.EFFECT_TRIGGERED: FunctionalEffectTriggeredCondition,
 CONDITION_TYPE.GAME_ITEM_SIMPLE_STATE: FunctionalGameItemSimpleStateCondition,
 CONDITION_TYPE.GAME_ITEM_RELATE_STATE: FunctionalGameItemRelateStateCondition,
 CONDITION_TYPE.BONUS_RECEIVED: FunctionalBonusReceivedCondition}

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
                    result = self._isConditionActive(condition)

            return result

    def evaluateWithOR(self):
        if self._conditions is None:
            return True
        else:
            result = False
            for condition in self._conditions:
                if not result:
                    result = self._isConditionActive(condition)

            return result

    def _isConditionActive(self, condition):
        condType = condition.getType()
        functional = condType in _SUPPORTED_CONDITIONS and _SUPPORTED_CONDITIONS[condType]
        if not functional:
            raise AssertionError('Function condition can not be empty')
        else:
            LOG_ERROR('Condition is not found', condType)
            functional = FunctionalCondition()
        return functional().isConditionOk(condition)


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

    def triggerEffect(self):
        raise NotImplementedError, 'method triggerEffect is not implemented'

    def getEffect(self):
        return self._effect

    def getTargetID(self):
        return self._effect.getTargetID()

    def getTarget(self):
        targetID = self.getTargetID()
        raise targetID or AssertionError('TargetID must be defined to find entity')
        return self._data.getHasIDEntity(targetID)

    def isInstantaneous(self):
        return True

    def isStillRunning(self):
        return False

    def stop(self):
        pass

    def isAllConditionsOK(self):
        result = True
        if self._effect is not None:
            return FunctionalConditions(self._effect.getConditions()).allConditionsOk()
        else:
            return result


class FunctionalActivateEffect(FunctionalEffect):

    def triggerEffect(self):
        targetID = self._effect.getTargetID()
        flags = self._tutorial.getFlags()
        if not flags.isActiveFlag(targetID):
            flags.activateFlag(targetID)
            self._tutorial.invalidateFlags()


class FunctionalDeactivateEffect(FunctionalEffect):

    def triggerEffect(self):
        targetID = self._effect.getTargetID()
        flags = self._tutorial.getFlags()
        if flags.isActiveFlag(targetID):
            flags.deactivateFlag(targetID)
            self._tutorial.invalidateFlags()


class FunctionalGlobalActivateEffect(FunctionalEffect):

    def triggerEffect(self):
        GlobalStorage.setValue(self._effect.getTargetID(), True)


class FunctionalGlobalDeactivateEffect(FunctionalEffect):

    def triggerEffect(self):
        GlobalStorage.setValue(self._effect.getTargetID(), False)


class FunctionalRefuseTrainingEffect(FunctionalEffect):

    def triggerEffect(self):
        self._tutorial.refuse()

    def isStillRunning(self):
        return True

    def isInstantaneous(self):
        return False


class FunctionalNextChapterEffect(FunctionalEffect):

    def triggerEffect(self):
        nextChapter = self._effect.getTargetID()
        if nextChapter is None or not len(nextChapter):
            nextChapter = self._descriptor.getInitialChapterID(completed=self._bonuses.getCompleted())
        if self._tutorial._currentChapter != nextChapter:
            self._gui.showWaiting('chapter-loading', isSingle=True)
            self._gui.clear()
            self._tutorial.goToNextChapter(nextChapter)
        return


class FunctionalRunTriggerEffect(FunctionalEffect):

    def __init__(self, effect):
        super(FunctionalRunTriggerEffect, self).__init__(effect)

    def isInstantaneous(self):
        return False

    def isStillRunning(self):
        trigger = self.getTarget()
        if trigger is not None:
            return trigger.isRunning
        else:
            return False

    def triggerEffect(self):
        trigger = self.getTarget()
        if trigger is not None:
            trigger.run()
        else:
            LOG_ERROR('Trigger not found', self._effect.getTargetID())
        return

    def getTarget(self):
        return self._data.getTrigger(self._effect.getTargetID())


class FunctionalRequestBonusEffect(FunctionalEffect):

    def isInstantaneous(self):
        return False

    def isStillRunning(self):
        return self._bonuses.isStillRunning()

    def triggerEffect(self):
        self._bonuses.request(chapterID=self._effect.getTargetID())


class FunctionalGuiItemSetPropertiesEffect(FunctionalEffect):

    def triggerEffect(self):
        effect = self._effect
        self._gui.setItemProps(effect.getTargetID(), effect.getProps(), revert=effect.isRevert())


class FunctionalFinishTrainingEffect(FunctionalEffect):

    def triggerEffect(self):
        self._tutorial.stop(finished=True)

    def isStillRunning(self):
        return True

    def isInstantaneous(self):
        return False


class FunctionalGuiCommandEffect(FunctionalEffect):

    def triggerEffect(self):
        targetID = self._effect.getTargetID()
        command = self._gui.config.getCommand(targetID)
        if command is not None:
            self._gui.invokeCommand(command)
        else:
            LOG_ERROR('Command not found', targetID)
        return


class FunctionalPlayerCommandEffect(FunctionalEffect):

    def triggerEffect(self):
        command = self.getTarget()
        if command is not None:
            player = BigWorld.player()
            attr = getattr(player, command.getName(), None)
            if attr is not None and callable(attr):
                try:
                    attr(*command.args(), **command.kwargs())
                except TypeError:
                    LOG_ERROR('Number of arguments mismatch', command.getName(), command.args(), command.kwargs())

            else:
                LOG_ERROR('Player has not method', command.getName())
        else:
            LOG_ERROR('Command not found', self._effect.getTargetID())
        return


class FunctionalShowDialogEffect(FunctionalEffect):

    def __init__(self, effect):
        self._isRunning = False
        self._isDialogClosed = False
        super(FunctionalShowDialogEffect, self).__init__(effect)

    def triggerEffect(self):
        self._gui.release()
        dialog = self.getTarget()
        if dialog is not None:
            self._isRunning = True
            if self._gui.isGuiDialogDisplayed():
                self._isDialogClosed = True
                return
            content = dialog.getContent()
            if not dialog.isContentFull():
                query = self._tutorial._ctrlFactory.createContentQuery(dialog.getType())
                query.invoke(content, dialog.getVarRef())
            self._isRunning = self._gui.playEffect(GUI_EFFECT_NAME.SHOW_DIALOG, [content])
            if not self._isRunning:
                LOG_ERROR('Can not play effect "ShowDialog"', dialog.getID(), dialog.getType())
        else:
            LOG_ERROR('Dialog not found', self._effect.getTargetID())
        return

    def isInstantaneous(self):
        return False

    def isStillRunning(self):
        if self._isRunning:
            if self._isDialogClosed and not self._gui.isGuiDialogDisplayed():
                self._isDialogClosed = False
                self.triggerEffect()
            if not self._isDialogClosed and not self._gui.isTutorialDialogDisplayed(self._effect.getTargetID()):
                self._isDialogClosed = True
        return self._isRunning

    def stop(self):
        self._isRunning = False
        self._isDialogClosed = False


class FunctionalShowWindowEffect(FunctionalEffect):

    def __init__(self, effect):
        self._isRunning = False
        super(FunctionalShowWindowEffect, self).__init__(effect)

    def triggerEffect(self):
        self._gui.release()
        window = self.getTarget()
        if window is not None:
            content = window.getContent()
            if not window.isContentFull():
                query = self._tutorial._ctrlFactory.createContentQuery(window.getType())
                query.invoke(content, window.getVarRef())
            self._setActions(window)
            isRunning = self._gui.playEffect(GUI_EFFECT_NAME.SHOW_WINDOW, [window.getID(), window.getType(), content])
            if not isRunning:
                LOG_ERROR('Can not play effect "ShowWindow"', window.getID(), window.getType())
        else:
            LOG_ERROR('PopUp not found', self._effect.getTargetID())
        return

    def _setActions(self, window):
        self._tutorial.getFunctionalScene().setActions(window.getActions())


class FunctionalShowMessageEffect(FunctionalEffect):

    def triggerEffect(self):
        message = self.getTarget()
        if message is not None:
            self._gui.showMessage(message.getText(), lookupType=message.getGuiType())
        else:
            LOG_ERROR('Message not found', self._effect.getTargetID())
        return


_var_search = re.compile('(\\$.*?(.+?)\\$)')

class FunctionalSetGuiItemCriteria(FunctionalEffect):

    def triggerEffect(self):
        criteria = self.getTarget()
        if criteria is None:
            LOG_ERROR('Criteria is not found', self._effect.getTargetID())
            return
        else:
            value = criteria.getValue()
            getVar = self._tutorial.getVars().get
            for marker, varID in re.findall(_var_search, value):
                value = value.replace(marker, str(getVar(varID)))

            LOG_DEBUG('Set gui item criteria', criteria.getTargetID(), value)
            self._gui.playEffect(GUI_EFFECT_NAME.SET_CRITERIA, (criteria.getTargetID(), value, not criteria.isCached()))
            return


class FunctionalSetAction(FunctionalEffect):

    def triggerEffect(self):
        action = self.getTarget()
        if action is None:
            LOG_ERROR('Action is not found', self._effect.getTargetID())
            return
        else:
            scene = self._tutorial.getFunctionalScene()
            if scene is None:
                LOG_ERROR('Scene is not defined', self._effect.getTargetID())
                return
            scene.setAction(action)
            self._gui.playEffect(GUI_EFFECT_NAME.SET_TRIGGER, (action.getTargetID(), action.getType()))
            return


class FunctionalRemoveAction(FunctionalEffect):

    def triggerEffect(self):
        action = self.getTarget()
        if action is None:
            LOG_ERROR('Action is not found', self._effect.getTargetID())
            return
        else:
            scene = self._tutorial.getFunctionalScene()
            if scene is None:
                LOG_ERROR('Scene is not defined', self._effect.getTargetID())
                return
            scene.removeAction(action)
            self._gui.stopEffect(GUI_EFFECT_NAME.SET_TRIGGER, action.getTargetID())
            return


class FunctionalSetVarAction(FunctionalEffect):

    def triggerEffect(self):
        finder = self.getTarget()
        if finder is None:
            LOG_ERROR('Var finder is not found', self._effect.getTargetID())
            return
        else:
            finderType = finder.getType()
            if finderType == chapter.VAR_FINDER_TYPE.GAME_ATTRIBUTE:
                getter = self._tutorial.getVars().get
                args = map(lambda varID: getter(varID, default=varID), finder.getArgs())
                self._tutorial.getVars().set(finder.getTargetID(), game_vars.getAttribute(finder.getName(), *args))
            else:
                LOG_ERROR('Type of setter is not supported', finderType)
            return


class FunctionalChapterInfo(TutorialProxyHolder):

    def invalidate(self):
        pass


class FunctionalClearScene(FunctionalEffect):

    def triggerEffect(self):
        self._gui.clearScene()


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
            effects = filter(self.__areAllConditionsOk, item.getOnSceneEffects())
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
            effects = filter(self.__areAllConditionsOk, item.getNotOnSceneEffects())
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
        effects = filter(self.__areAllConditionsOk, self._scene.getEffects())
        if self._pending:
            effects.extend(self._pending)
            self._pending = []
        if effects:
            self._tutorial.storeEffectsInQueue(effects)
        self._isUpdatedOnce = True
        self._gui.release()

    def __areAllConditionsOk(self, item):
        return FunctionalConditions(item.getConditions()).allConditionsOk()


class GoToSceneEffect(FunctionalEffect):

    def triggerEffect(self):
        sceneID = self.getTargetID()
        if sceneID is None:
            LOG_ERROR('scene is not found', self._effect.getTargetID())
            return
        else:
            self._gui.goToScene(sceneID)
            return
