# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/NewYearTalismanBaseObject.py
import logging
import BigWorld
import AnimationSequence
from ClientSelectableObject import ClientSelectableObject
from gui.Scaleform.managers.cursor_mgr import CursorManager
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.new_year import ITalismanSceneController, INewYearController
from vehicle_systems.stricted_loading import makeCallbackWeak
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
_logger = logging.getLogger(__name__)
_SHOW_CONGRATS = 'show_congrats'
_HOVER_PARAM = 'hover'

class NewYearTalismanBaseObject(ClientSelectableObject):
    _talismanController = dependency.descriptor(ITalismanSceneController)
    _newYearController = dependency.descriptor(INewYearController)
    _appLoader = dependency.descriptor(IAppLoader)

    def __init__(self):
        super(NewYearTalismanBaseObject, self).__init__()
        self.__hoverEffect = None
        self.__congratsEffect = None
        self._animator = None
        self.targetCaps = []
        self.__modelWrapperContainer = None
        return

    def onEnterWorld(self, prereqs):
        super(NewYearTalismanBaseObject, self).onEnterWorld(prereqs)
        if self.hoverEffect:
            loaderHover = AnimationSequence.Loader(self.hoverEffect, self.spaceID)
            BigWorld.loadResourceListBG((loaderHover,), makeCallbackWeak(self.__onHoverEffectLoaded, self.hoverEffect))
        if self.congratsEffect:
            loaderCongrats = AnimationSequence.Loader(self.congratsEffect, self.spaceID)
            BigWorld.loadResourceListBG((loaderCongrats,), makeCallbackWeak(self.__onCongratsEffectLoaded, self.congratsEffect))
        if self.stateMachine:
            animationLoader = AnimationSequence.Loader(self.stateMachine, self.spaceID)
            BigWorld.loadResourceListBG((animationLoader,), makeCallbackWeak(self.__onAnimatorLoaded, self.stateMachine))
        self.setInteractive(False)

    def onLeaveWorld(self):
        if self.__hoverEffect is not None:
            self.__hoverEffect.stop()
            self.__hoverEffect = None
        if self.__congratsEffect is not None:
            self.__congratsEffect.stop()
            self.__congratsEffect = None
        if self._animator is not None:
            self._animator.stop()
            self._animator.unsubscribe(self.__animatorEvent)
            self._animator = None
        self.__modelWrapperContainer = None
        super(NewYearTalismanBaseObject, self).onLeaveWorld()
        return

    def setAnimatorTrigger(self, triggerName):
        if self._animator is None:
            return
        else:
            self._animator.setTrigger(triggerName)
            if triggerName == _SHOW_CONGRATS:
                self._startCongratsEffect()
            return

    def setInteractive(self, isInteractive):
        self.targetCaps = [] if isInteractive else [0]

    def _onAnimatorEvent(self, eventName):
        pass

    def _startHoverEffect(self):
        if not self._talismanController.mouseEventsAvailable():
            return
        self.__setHoverTrigger(True)
        self.__changeUICursor(CursorManager.HAND)

    def _stopHoverEffect(self):
        self.__setHoverTrigger(False)
        self.__changeUICursor(self._hoverOutCursorType())

    def _startCongratsEffect(self):
        self.__startEffect(self.__congratsEffect)

    def _stopCongratsEffect(self):
        self.__stopEffect(self.__congratsEffect)

    def _addEdgeDetect(self):
        NewYearSoundsManager.playEvent(NewYearSoundEvents.TALISMAN_HOVER_ON)
        self._startHoverEffect()

    def _delEdgeDetect(self):
        NewYearSoundsManager.playEvent(NewYearSoundEvents.TALISMAN_HOVER_OFF)
        self._stopHoverEffect()

    def _getCollisionModelsPrereqs(self):
        if self.collisionModelName:
            collisionModels = ((0, self.collisionModelName),)
            return collisionModels
        return super(NewYearTalismanBaseObject, self)._getCollisionModelsPrereqs()

    def _onAnimatorStarted(self):
        pass

    def _hoverOutCursorType(self):
        return CursorManager.ARROW

    def __changeUICursor(self, cursorType):
        app = self._appLoader.getApp()
        if app is not None and app.cursorMgr is not None:
            app.cursorMgr.setCursorForced(cursorType)
        return

    def __setHoverTrigger(self, paramValue):
        if self.__hoverEffect is not None:
            self.__hoverEffect.setBoolParam(_HOVER_PARAM, paramValue)
        return

    @staticmethod
    def __startEffect(effect):
        if effect is None:
            return
        else:
            effect.setEnabled(True)
            effect.start()
            return

    @staticmethod
    def __stopEffect(effect):
        if effect is None:
            return
        else:
            effect.stop()
            effect.setEnabled(False)
            return

    def __checkResource(self, resourceName, resourceList):
        if self.model is None:
            _logger.error('Could not spawn resource. Model is not loaded: %s', self.modelName)
            return False
        elif resourceName in resourceList.failedIDs:
            _logger.error('Failed to load resource "%s". Effects wont be used', resourceName)
            return False
        else:
            if self.__modelWrapperContainer is None:
                self.__modelWrapperContainer = AnimationSequence.ModelWrapperContainer(self.model, self.spaceID)
            return True

    def __onHoverEffectLoaded(self, resourceName, resourceList):
        if not self.__checkResource(resourceName, resourceList):
            return
        self.__hoverEffect = resourceList[resourceName]
        self.__hoverEffect.bindTo(self.__modelWrapperContainer)
        self.__hoverEffect.start()

    def __onCongratsEffectLoaded(self, resourceName, resourceList):
        if not self.__checkResource(resourceName, resourceList):
            return
        self.__congratsEffect = resourceList[resourceName]
        self.__congratsEffect.bindTo(self.__modelWrapperContainer)

    def __onAnimatorLoaded(self, resourceName, resourceList):
        if not self.__checkResource(resourceName, resourceList):
            return
        self._animator = resourceList[self.stateMachine]
        self._animator.bindTo(self.__modelWrapperContainer)
        self._animator.subscribe(self.__animatorEvent)
        self._animator.start()
        self._onAnimatorStarted()

    def __animatorEvent(self, name, _):
        self._onAnimatorEvent(name)
