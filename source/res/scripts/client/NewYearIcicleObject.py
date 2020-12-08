# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/NewYearIcicleObject.py
import logging
import BigWorld
import AnimationSequence
from gui.Scaleform.managers.cursor_mgr import CursorManager
from skeletons.gui.app_loader import IAppLoader
from vehicle_systems.stricted_loading import makeCallbackWeak
from ClientSelectableObject import ClientSelectableObject
from helpers import dependency
from skeletons.new_year import IIcicleController
from new_year.ny_icicle_controller import IcicleClickStates
_logger = logging.getLogger(__name__)

class _EffectIDs(object):
    NORMAL = 1
    TRUE = 2
    FALSE = 3
    ALL = (NORMAL, TRUE, FALSE)


_CLICK_STATE_TO_EFFECT_ID = {IcicleClickStates.CORRECT: _EffectIDs.TRUE,
 IcicleClickStates.INCORRECT: _EffectIDs.FALSE}

class NewYearIcicleObject(ClientSelectableObject):
    __icicleController = dependency.descriptor(IIcicleController)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self):
        super(NewYearIcicleObject, self).__init__()
        self.__effects = {}

    @property
    def isHighlighted(self):
        return self.__isHighlighted

    def onEnterWorld(self, prereqs):
        super(NewYearIcicleObject, self).onEnterWorld(prereqs)
        effectPaths = (self.effectNormalState, self.effectTrueState, self.effectFalseState)
        if not all((effectPath for effectPath in effectPaths)):
            _logger.error('Missing effect for Icicle Entity [objectID=%s]', self.objectID)
        else:
            effects = tuple((AnimationSequence.Loader(effect, self.spaceID) for effect in effectPaths))
            BigWorld.loadResourceListBG(effects, makeCallbackWeak(self.__onEffectsLoaded, effectPaths))
        self.__icicleController.addIcicleEntity(self)
        self.__isHighlighted = False

    def onLeaveWorld(self):
        self.__icicleController.removeIcicleEntity(self)
        for effectID in _EffectIDs.ALL:
            self.__enableEffect(effectID, enable=False)

        self.__effects.clear()
        super(NewYearIcicleObject, self).onLeaveWorld()

    def onMouseClick(self):
        super(NewYearIcicleObject, self).onMouseClick()
        clickState = self.__icicleController.handleIcicleClick(self.objectID)
        if clickState == IcicleClickStates.NONE:
            return
        elif clickState == IcicleClickStates.COMPLETE:
            self.resetEffects()
            return
        else:
            effectID = _CLICK_STATE_TO_EFFECT_ID.get(clickState)
            if effectID is not None:
                self.__switchEffect(effectID)
            else:
                _logger.error('Wrong ClickState [%s] for IcicleEntity [objectID=%s].', clickState, self.objectID)
            return

    def resetEffects(self):
        ctrl = self.__icicleController
        if ctrl.isCompleted or ctrl.isPuzzleActive or ctrl.puzzleStage:
            effect = None
        else:
            effect = _EffectIDs.NORMAL
        self.__switchEffect(effect)
        return

    def restoreHandCursor(self):
        self.__changeUICursor(CursorManager.HAND)

    def _addEdgeDetect(self):
        self.__isHighlighted = True
        self.__changeUICursor(CursorManager.HAND)

    def _delEdgeDetect(self):
        self.__isHighlighted = False
        self.__changeUICursor(CursorManager.DRAG_OPEN)

    def _getCollisionModelsPrereqs(self):
        if self.collisionModelName:
            collisionModels = ((0, self.collisionModelName),)
            return collisionModels
        return super(NewYearIcicleObject, self)._getCollisionModelsPrereqs()

    def __onEffectsLoaded(self, requestedEffects, resourceList):
        if self.model is None:
            _logger.error('Missing model for IcicleEntity: [modelName=%s].', self.modelName)
            return
        else:
            for effectId, effectPath in zip(_EffectIDs.ALL, requestedEffects):
                if effectPath in resourceList.failedIDs:
                    _logger.error('Failed to load effect: [path=%s].', effectPath)
                    self.__effects.clear()
                    return
                effect = resourceList[effectPath]
                effect.bindTo(AnimationSequence.ModelWrapperContainer(self.model, self.spaceID))
                effect.setEnabled(False)
                self.__effects[effectId] = effect

            self.resetEffects()
            return

    def __switchEffect(self, effectID):
        for eID in _EffectIDs.ALL:
            enable = eID == effectID
            self.__enableEffect(eID, enable=enable)

    def __enableEffect(self, effectID, enable=True):
        effect = self.__effects.get(effectID)
        if effect is None:
            _logger.warning('Missing effect [effectID=%s] for Icicle Entity [objectID=%s]', effectID, self.objectID)
            return
        else:
            effect.setEnabled(enable)
            if enable:
                effect.start()
            else:
                effect.stop()
            return

    def __changeUICursor(self, cursorType):
        app = self.__appLoader.getApp()
        if app is not None and app.cursorMgr is not None:
            app.cursorMgr.setCursorForced(cursorType)
        return
