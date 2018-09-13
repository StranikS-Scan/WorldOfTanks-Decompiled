# Embedded file name: scripts/client/tutorial/control/functional.py
import BigWorld
from tutorial.control import TutorialProxyHolder, game_vars
from tutorial.control.context import GlobalStorage
from tutorial.data import chapter
from tutorial.gui import GUI_EFFECT_NAME
from tutorial.logger import LOG_ERROR, LOG_DEBUG

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
            flags = self._tutorial.getFlags()
            for condition in self._conditions:
                if result:
                    result = self._isConditionActive(result, condition, flags)

            return result

    def evaluateWithOR(self):
        if self._conditions is None:
            return True
        else:
            result = False
            flags = self._tutorial.getFlags()
            for condition in self._conditions:
                if not result:
                    result = self._isConditionActive(result, condition, flags)

            return result

    def _isConditionActive(self, result, condition, flags):
        condType = condition.getType()
        baseType = chapter.Condition
        if condType == baseType.FLAG_CONDITION:
            result = condition.isActiveState() == flags.isActiveFlag(condition.getID())
        elif condType == baseType.GLOBAL_FLAG_CONDITION:
            result = condition.isActiveState() == GlobalStorage(condition.getID(), False).value()
        elif condType == baseType.VEHICLE_CONDITION:
            result = condition.isValueEqual(game_vars.vehicle(condition.getID()))
        elif condType == baseType.WINDOW_ON_SCENE_CONDITION:
            result = condition.isActiveState() == self._gui.isTutorialWindowDisplayed(condition.getID())
        return result


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

    def getTarget(self):
        return self._tutorial._data.getHasIDEntity(self._effect.getTargetID())

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
            nextChapter = self._tutorial._descriptor.getInitialChapterID(bonusCompleted=self._tutorial._bonuses.getCompleted())
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
        return self._tutorial._data.getTrigger(self._effect.getTargetID())


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


class FunctionalDefineGuiItem(FunctionalEffect):

    def triggerEffect(self):
        effect = self._effect
        parentReference = self._gui.config.getItem(effect.getParentReference())
        extraReference = self._gui.config.getItem(effect.getExtraReference())
        targetId = effect.getTargetID()
        ERROR = '%s was not found in gui-items list'
        if parentReference is not None:
            if extraReference is not None:
                extraPath = '{0:>s}.{1:>s}'.format(parentReference.get('path'), extraReference.get('path'))
                self._gui.config.addItem(targetId, extraPath, True)
            else:
                LOG_ERROR(ERROR % effect.getExtraReference())
        else:
            LOG_ERROR(ERROR % effect.getParentReference())
        return


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
            self._tutorial.getFunctionalScene().setActions(window.getActions())
            isRunning = self._gui.playEffect(GUI_EFFECT_NAME.SHOW_WINDOW, [window.getID(), window.getType(), content])
            if not isRunning:
                LOG_ERROR('Can not play effect "ShowWindow"', window.getID(), window.getType())
        else:
            LOG_ERROR('PopUp not found', self._effect.getTargetID())
        return


class FunctionalShowMessageEffect(FunctionalEffect):

    def triggerEffect(self):
        message = self.getTarget()
        if message is not None:
            self._gui.showMessage(message.getText(), lookupType=message.getGuiType())
        else:
            LOG_ERROR('Message not found', self._effect.getTargetID())
        return


class FunctionalChapterInfo(TutorialProxyHolder):

    def invalidate(self):
        pass


class FunctionalScene(TutorialProxyHolder):

    def __init__(self, scene):
        super(FunctionalScene, self).__init__()
        LOG_DEBUG('New functional scene', scene.getID())
        self.__scene = scene
        self.__actions = {}
        self.__dynamicItems = {}
        self.__dynamicItemsOnScene = []
        self._sceneToBeUpdated = True
        self._gui.lock()

    def enter(self):
        pass

    def leave(self):
        if self._sceneToBeUpdated:
            self._gui.release()
            self._sceneToBeUpdated = False

    def reload(self):
        pass

    def update(self):
        if self._sceneToBeUpdated:
            self._sceneToBeUpdated = False
            self._updateScene()
        for itemID, item in self.__dynamicItems.iteritems():
            criteria = item.getFindCriteria()
            if criteria is not None:
                criteria[2] = self._tutorial.getVars().get(criteria[2])
            result = self._gui.findItem(itemID, criteria)
            wasOnScene = itemID in self.__dynamicItemsOnScene
            effects = []
            if result is not None and not wasOnScene:
                LOG_DEBUG('Gui item is on scene', itemID)
                self.__dynamicItemsOnScene.append(itemID)
                props = item.getProps()
                if len(props):
                    self._gui.setItemProps(item.getTargetID(), props)
                effects = item.getOnSceneEffects()
            elif result is None and wasOnScene:
                LOG_DEBUG('Gui item is not on scene', itemID)
                effects = item.getNotOnSceneEffects()
                self.__dynamicItemsOnScene.remove(itemID)
            if len(effects):
                self._tutorial.storeEffectsInQueue(effects)

        return

    def _updateScene(self, playEffects = True):
        LOG_DEBUG('Update scene.')
        items = filter(self.__isPermanentGuiItem, self.__scene.getGuiItems())
        for item in items:
            self._gui.setItemProps(item.getTargetID(), item.getProps(), revert=True)

        items = filter(self.__isDynamicGuiItem, self.__scene.getGuiItems())
        self.__dynamicItems = dict(map(lambda item: (item.getTargetID(), item), items))
        if playEffects:
            effects = filter(self.__areAllConditionsOk, self.__scene.getEffects())
            if len(effects):
                self._tutorial.storeEffectsInQueue(effects)
        self._gui.release()

    def getAction(self, targetID):
        return self.__actions.get(targetID)

    def setAction(self, targetID, action):
        self.__actions[targetID] = action

    def clearAction(self, targetID):
        self.__actions.pop(targetID, None)
        return

    def setActions(self, actions):
        for action in actions:
            self.__actions[action.getTargetID()] = action

    def __areAllConditionsOk(self, item):
        return FunctionalConditions(item.getConditions()).allConditionsOk()

    def __isPermanentGuiItem(self, item):
        return item.getLifeCycle() == chapter.GuiItemRef.LIFE_CYCLE_PERMANENT and FunctionalConditions(item.getConditions()).allConditionsOk()

    def __isDynamicGuiItem(self, item):
        return item.getLifeCycle() == chapter.GuiItemRef.LIFE_CYCLE_DYNAMIC and FunctionalConditions(item.getConditions()).allConditionsOk()
