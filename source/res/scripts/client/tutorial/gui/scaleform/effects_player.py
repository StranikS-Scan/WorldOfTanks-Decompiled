# Embedded file name: scripts/client/tutorial/gui/Scaleform/effects_player.py
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.TUTORIAL_TRIGGER_TYPES import TUTORIAL_TRIGGER_TYPES
from tutorial.data.events import GUI_EVENT_TYPE
from tutorial.logger import LOG_ERROR, LOG_DEBUG
from gui.app_loader.decorators import sf_lobby

class GUIEffect(object):

    @sf_lobby
    def app(self):
        return None

    def play(self, effectData):
        return False

    def stop(self, effectID = None):
        pass

    def cancel(self, *criteria):
        pass

    def isStillRunning(self, effectID = None):
        return False

    def _getContainer(self, viewType):
        if self.app is None:
            return
        else:
            manager = self.app.containerManager
            if manager is None:
                return
            return manager.getContainer(viewType)

    def _getTutorialLayout(self):
        if self.app is None:
            return
        else:
            return self.app.tutorialManager


class ShowDialogEffect(GUIEffect):

    def __init__(self, aliasMap):
        self._aliasMap = aliasMap
        self._dialogID = None
        return

    def clear(self):
        self._dialogID = None
        return

    def play(self, effectData):
        effectData = effectData[0]
        result = False
        if 'type' in effectData and 'dialogID' in effectData:
            dialogType = effectData['type']
            dialogID = effectData['dialogID']
            if dialogID == self._dialogID:
                LOG_ERROR('Dialog is displayed', effectData['dialogID'])
                return False
            if dialogType in self._aliasMap:
                alias = self._aliasMap[dialogType]
                self._dialogID = dialogID
                self.app.loadView(alias, dialogID, effectData)
                result = True
            else:
                LOG_ERROR('Alias of dialog not found', effectData, self._aliasMap)
        else:
            LOG_ERROR('Type or id of dialog not found', effectData)
        return result

    def stop(self, effectID = None):
        isForceStop = effectID is None
        if not isForceStop and effectID != self._dialogID:
            LOG_ERROR('Dialog is not opened', effectID)
            return
        else:
            effectID = self._dialogID
            self._dialogID = None
            container = self._getContainer(ViewTypes.TOP_WINDOW)
            if container is not None:
                dialog = container.getView(criteria={POP_UP_CRITERIA.UNIQUE_NAME: effectID})
                if dialog is not None:
                    dialog.destroy()
                elif not isForceStop:
                    LOG_ERROR('Dialog is not opened', effectID)
            return

    def isStillRunning(self, effectID = None):
        if effectID is not None:
            result = self._dialogID == effectID
        else:
            result = self._dialogID is not None
        return result


class ShowWindowEffect(GUIEffect):

    def __init__(self, aliasMap):
        self._aliasMap = aliasMap
        self._windowIDs = set()

    def clear(self):
        self._windowIDs.clear()

    def play(self, effectData):
        windowID, windowType, content = effectData
        result = False
        if windowType in self._aliasMap:
            alias = self._aliasMap[windowType]
            self._windowIDs.add(windowID)
            self.app.loadView(alias, windowID, content)
            result = True
        else:
            LOG_ERROR('Alias of window not found', windowType, self._aliasMap)
        return result

    def stop(self, effectID = None):
        isForceStop = effectID is None
        if not isForceStop:
            if effectID not in self._windowIDs:
                LOG_ERROR('Window is not opened', effectID)
                return
            effectIDs = {effectID}
        else:
            effectIDs = self._windowIDs.copy()
        container = self._getContainer(ViewTypes.WINDOW)
        if container is not None:
            getView = container.getView
            for eID in effectIDs:
                window = getView(criteria={POP_UP_CRITERIA.UNIQUE_NAME: eID})
                if window is not None:
                    window.destroy()
                    self._windowIDs.remove(eID)
                elif not isForceStop:
                    LOG_ERROR('Window is not opened', eID)

        return

    def isStillRunning(self, effectID = None):
        if effectID is not None:
            result = effectID in self._windowIDs
        else:
            result = len(self._windowIDs)
        return result


_GUI_EVENT_TO_TRIGGER_TYPE = {GUI_EVENT_TYPE.CLICK: TUTORIAL_TRIGGER_TYPES.CLICK_TYPE,
 GUI_EVENT_TYPE.CLICK_OUTSIDE: TUTORIAL_TRIGGER_TYPES.CLICK_OUTSIDE_TYPE,
 GUI_EVENT_TYPE.ESC: TUTORIAL_TRIGGER_TYPES.ESCAPE}

class ShowChainHint(GUIEffect):

    def __init__(self):
        super(ShowChainHint, self).__init__()
        self._hintID = None
        self._itemID = None
        return

    def isStillRunning(self, effectID = None):
        if effectID is not None:
            result = self._hintID == effectID
        else:
            result = self._hintID is not None
        return result

    def play(self, effectData):
        hintProps, triggers = effectData
        if self._hintID == hintProps.hintID:
            LOG_DEBUG('Hint already is added', hintProps.hintID)
            return True
        else:
            layout = self._getTutorialLayout()
            if layout is not None:
                self._hintID = hintProps.hintID
                self._itemID = hintProps.itemID
                content = {'uniqueID': hintProps.uniqueID,
                 'hintText': hintProps.text,
                 'hasBox': hintProps.hasBox,
                 'hasArrow': False,
                 'arrowDir': '',
                 'arrowLoop': False}
                arrow = hintProps.arrow
                if arrow is not None:
                    content['hasArrow'] = True
                    content['arrowDir'] = arrow.direction
                    content['arrowLoop'] = arrow.loop
                padding = hintProps.padding
                if padding is not None:
                    content['padding'] = padding._asdict()
                triggers = map(lambda item: _GUI_EVENT_TO_TRIGGER_TYPE[item], triggers)
                layout.showInteractiveHint(hintProps.itemID, content, triggers)
                return True
            return False

    def stop(self, effectID = None):
        if effectID is not None and effectID != self._hintID:
            LOG_DEBUG('Hint is not added', effectID)
            return
        elif self._itemID is None:
            return
        else:
            layout = self._getTutorialLayout()
            if layout is not None:
                layout.closeInteractiveHint(self._itemID)
            self._hintID = None
            self._itemID = None
            return

    def cancel(self, *criteria):
        if not criteria:
            return
        if self._itemID == criteria[0]:
            self.stop()


class ShowOnceOnlyHint(ShowChainHint):

    def stop(self, effectID = None):
        if effectID is not None:
            super(ShowOnceOnlyHint, self).stop(effectID)
        return

    def cancel(self, *criteria):
        if criteria is not None and self._itemID == criteria[0]:
            self.stop(self._hintID)
        return


class UpdateContentEffect(GUIEffect):

    def play(self, effectData):
        effectData = effectData[0]
        result = False
        effectID = None
        viewType = None
        if 'dialogID' in effectData:
            effectID = effectData['dialogID']
            viewType = ViewTypes.TOP_WINDOW
        if effectID is not None:
            container = self._getContainer(viewType)
            if container is not None:
                view = container.getView(criteria={POP_UP_CRITERIA.UNIQUE_NAME: effectID})
                if view is not None:
                    if hasattr(view, 'as_updateContentS'):
                        view.as_updateContentS(effectData)
                        result = True
                    else:
                        LOG_ERROR('View is invalid', view)
                else:
                    LOG_DEBUG('View is not on scene', effectID)
                    result = True
        return result


class SetCriteriaEffect(GUIEffect):

    def play(self, effectData):
        itemID, value, noCached = effectData
        layout = self._getTutorialLayout()
        if layout is not None:
            layout.setCriteria(itemID, value, noCached)
        return


_ACTION_TO_TRIGGER_TYPE = {GUI_EVENT_TYPE.CLICK: TUTORIAL_TRIGGER_TYPES.CLICK_TYPE,
 GUI_EVENT_TYPE.CLICK_OUTSIDE: TUTORIAL_TRIGGER_TYPES.CLICK_OUTSIDE_TYPE}

class SetTriggerEffect(GUIEffect):

    def __init__(self):
        super(SetTriggerEffect, self).__init__()
        self._itemsIDs = set()

    def play(self, effectData):
        itemID, actionType = effectData
        if actionType not in _ACTION_TO_TRIGGER_TYPE:
            LOG_ERROR('Can not found type of trigger', itemID, actionType)
            return
        else:
            layout = self._getTutorialLayout()
            if layout is not None:
                self._itemsIDs.add(itemID)
                layout.setTriggers(itemID, (_ACTION_TO_TRIGGER_TYPE[actionType],))
            return

    def stop(self, effectID = None):
        if effectID is None:
            itemIDs = self._itemsIDs.copy()
            self._itemsIDs.clear()
        else:
            itemIDs = {effectID}
            if effectID not in self._itemsIDs:
                LOG_ERROR('Trigger is not set for item', effectID)
                return
            self._itemsIDs.discard(effectID)
        layout = self._getTutorialLayout()
        if layout is not None:
            for itemID in itemIDs:
                layout.clearTriggers(itemID)

        return


class EffectsPlayer(object):

    def __init__(self, effects):
        super(EffectsPlayer, self).__init__()
        self._effects = effects

    def clear(self):
        self._effects.clear()

    def play(self, effectName, effectData):
        result = False
        if effectName in self._effects:
            result = self._effects[effectName].play(effectData)
        else:
            LOG_ERROR('GUI effect not found', effectName)
        return result

    def stop(self, effectName, effectID):
        if effectName in self._effects:
            self._effects[effectName].stop(effectID=effectID)
        else:
            LOG_ERROR('GUI effect not found', effectName)

    def cancel(self, effectName, *criteria):
        if effectName in self._effects:
            self._effects[effectName].cancel(*criteria)
        else:
            LOG_ERROR('GUI effect not found', effectName)

    def stopAll(self):
        for effect in self._effects.itervalues():
            effect.stop()

    def isStillRunning(self, effectName, effectID = None):
        result = False
        if effectName in self._effects:
            result = self._effects[effectName].isStillRunning(effectID=effectID)
        else:
            LOG_ERROR('GUI effect not found', effectName)
        return result
