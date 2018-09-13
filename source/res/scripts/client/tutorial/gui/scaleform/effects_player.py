# Embedded file name: scripts/client/tutorial/gui/Scaleform/effects_player.py
from gui.Scaleform.framework import AppRef, ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from tutorial.logger import LOG_ERROR, LOG_DEBUG

class GUIEffect(AppRef):

    def play(self, effectData):
        return False

    def stop(self, effectID = None):
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
            if self.app is None or self.app.containerManager is None:
                return
            container = self.app.containerManager.getContainer(ViewTypes.TOP_WINDOW)
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
            effectIDs = set([effectID])
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


class UpdateContentEffect(GUIEffect, AppRef):

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
                    LOG_DEBUG('View is not on scene')
                    result = True
        return result


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
