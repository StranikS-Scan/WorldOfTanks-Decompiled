# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/battle_context_hints/hint_lifecycle_managers.py
import logging
import typing
from gui.Scaleform.genConsts.CONTEXT_HINT_PARAMS import CONTEXT_HINT_PARAMS
from gui.Scaleform.genConsts.CONTEXT_HINT_STATE import CONTEXT_HINT_STATE
from helpers.CallbackDelayer import CallbackDelayer
from gui.battle_control.avatar_getter import getSoundNotifications
from gui.battle_control.battle_context_hints.common import ContextHintsSoundEvents, getBestPiercingShellCD
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from typing import Optional, Type
    from gui.impl.battle.battle_page.battle_context_hints.hint_inject_component import HintInjectComponent
    from gui.impl.battle.battle_page.battle_context_hints.battle_context_hint_view import BattleContextHintsView
    from gui.impl.battle.battle_page.battle_context_hints.battle_context_hints_presenters import BattleContextHintsViewPresenter
    from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel
    from uilogging.battle_context_hints.loggers import BattleContextHintsLogger
_logger = logging.getLogger(__name__)

class HintLifecycleMgr(object):

    def __init__(self, *args, **kwargs):
        self.onFinished = None
        return

    def start(self, hintId, hintSoundEvent, context, logger, component, hintViewClass, hintPresenterClass, delay, duration, hintFinishedCallback):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def applied(self):
        raise NotImplementedError

    def isShowing(self):
        raise NotImplementedError


class BaseHintLifecycleMgr(HintLifecycleMgr):

    def __init__(self, *args, **kwargs):
        super(BaseHintLifecycleMgr, self).__init__(*args, **kwargs)
        self._delayer = CallbackDelayer()
        self._hintId = None
        self._hintSoundEvent = None
        self._context = None
        self._logger = None
        self._component = None
        self._hintViewClass = None
        self._hintPresenterClass = None
        self._delay = None
        self._duration = None
        self._hintFinishedCallback = None
        self._isShowing = False
        return

    def start(self, hintId, hintSoundEvent, context, logger, component, hintViewClass, hintPresenterClass, delay, duration, hintFinishedCallback):
        self._hintId = hintId
        self._hintSoundEvent = hintSoundEvent
        self._context = context
        self._logger = logger
        self._component = component
        self._hintViewClass = hintViewClass
        self._hintPresenterClass = hintPresenterClass
        self._delay = delay
        self._duration = duration
        self._hintFinishedCallback = hintFinishedCallback
        self._delayer.delayCallback(self._delay, self._showHint)

    def stop(self):
        self._delayer.destroy()
        self._hideHint()

    def _showHint(self):
        if self._isShowing:
            return
        self._doShowHint()
        self._playHintSound()
        self._logger.logHintShowed()
        self._isShowing = True

    def _hideHint(self, applied=False):
        if not self._isShowing:
            return
        else:
            self._doHideHint(applied)
            self._isShowing = False
            if self._hintFinishedCallback is not None:
                self._hintFinishedCallback(self._hintId)
            return

    def _playHintSound(self):
        if not self._hintSoundEvent:
            return
        soundNotifications = getSoundNotifications()
        if soundNotifications and hasattr(soundNotifications, 'play'):
            soundNotifications.play(self._hintSoundEvent)

    def isShowing(self):
        return self._isShowing

    def _doShowHint(self):
        raise NotImplementedError

    def _doHideHint(self, applied=False):
        raise NotImplementedError


class InfoHintLifecycleMgr(BaseHintLifecycleMgr):

    def _doShowHint(self):
        _logger.debug('[BATTLE_CONTEXT_INTS] InfoHintLifecycleMgr._doShowHint()')
        self._component.setInjectView(self._hintViewClass)
        self._component.getInjectView().showHint(self._hintPresenterClass(self._duration, self._hintId) if self._hintPresenterClass is not None else None, self._hideHint)
        self._component.showHint()
        return

    def _doHideHint(self, applied=False):
        _logger.debug('[BATTLE_CONTEXT_INTS] InfoHintLifecycleMgr._doHideHint()')
        self._component.getInjectView().hideHint()
        self._component.hideHint()

    def applied(self):
        pass


class ConsumablesPanelHintLifecycleMgr(BaseHintLifecycleMgr):

    def __init__(self, *args, **kwargs):
        super(ConsumablesPanelHintLifecycleMgr, self).__init__(*args, **kwargs)
        self._component = None
        return

    def _doShowHint(self):
        _logger.debug('[BATTLE_CONTEXT_INTS] %s._doShowHint()', self.__class__.__name__)
        intCD = self._resolveTargetIntCD()
        if intCD is None:
            if self._hintFinishedCallback is not None:
                self._hintFinishedCallback(self._hintId)
            return
        else:
            self._component.showContextHint(intCD, self._getHintText())
            self._onHintShown(intCD)
            self._scheduleHideHint()
            return

    def _doHideHint(self, applied=False):
        _logger.debug('[BATTLE_CONTEXT_INTS] %s._doHideHint(applied=%s)', self.__class__.__name__, applied)
        self._onHintHidden(applied)
        self._component.hideContextHint(applied)

    def applied(self):
        self._hideHint(True)

    def _scheduleHideHint(self):
        self._delayer.delayCallback(self._duration, self._hideHint)

    def _resolveTargetIntCD(self):
        raise NotImplementedError

    def _getHintText(self):
        raise NotImplementedError

    def _onHintShown(self, intCD):
        pass

    def _onHintHidden(self, applied=False):
        pass


class KitHintLifecycleMgr(ConsumablesPanelHintLifecycleMgr):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _resolveTargetIntCD(self):
        equipmentTag = self._context['equipmentTag']
        equipCtrl = self.__sessionProvider.shared.equipments
        if equipCtrl is None:
            return
        else:
            equipIntCD = None
            for intCD, item in equipCtrl.iterEquipmentsByTag(equipmentTag, lambda eq: eq.isAvailableToUse):
                equipIntCD = intCD
                if item.getDescriptor().name.startswith('large'):
                    break

            return equipIntCD

    def _getHintText(self):
        return backport.text(R.strings.battle_hints.contextHint.consumablesPanel.medkit()) if self._context['equipmentTag'] == 'medkit' else backport.text(R.strings.battle_hints.contextHint.consumablesPanel.repairkit())


class AmmoTypeSwitchHintLifecycleMgr(ConsumablesPanelHintLifecycleMgr):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, *args, **kwargs):
        super(AmmoTypeSwitchHintLifecycleMgr, self).__init__(*args, **kwargs)
        self.__ammoCtrl = None
        self.__targetIntCD = None
        self.__selectedStateShown = False
        return

    def _onHintShown(self, intCD):
        self.__selectedStateShown = False
        self.__targetIntCD = intCD
        self.__subscribeToNextShellChanged()
        self.__tryShowSelectedState()

    def _onHintHidden(self, applied=False):
        self.__unsubscribeFromNextShellChanged()
        self.__targetIntCD = None
        self.__selectedStateShown = False
        return

    def applied(self):
        if self.isShowing():
            soundNotifications = getSoundNotifications()
            if soundNotifications and hasattr(soundNotifications, 'play'):
                soundNotifications.play(ContextHintsSoundEvents.AMMO_TYPE_SWITCH_APPLIED)
        super(AmmoTypeSwitchHintLifecycleMgr, self).applied()

    def __subscribeToNextShellChanged(self):
        self.__ammoCtrl = self.__sessionProvider.shared.ammo
        if self.__ammoCtrl is not None:
            self.__ammoCtrl.onNextShellChanged += self.__onNextShellChanged
        return

    def __unsubscribeFromNextShellChanged(self):
        if self.__ammoCtrl is not None:
            self.__ammoCtrl.onNextShellChanged -= self.__onNextShellChanged
            self.__ammoCtrl = None
        return

    def __onNextShellChanged(self, intCD):
        if self.__selectedStateShown or intCD != self.__targetIntCD:
            return
        self.__selectedStateShown = True
        self._delayer.stopCallback(self._hideHint)
        self._delayer.delayCallback(CONTEXT_HINT_PARAMS.INTERFERING_TWEEN_DURATION / 1000.0 + 0.01, self.__setSelectedState, intCD)
        self.__unsubscribeFromNextShellChanged()

    def __setSelectedState(self, intCD):
        self._component.setContextHintState(intCD, self._getConfirmHintText(), CONTEXT_HINT_STATE.SELECTED)
        self._scheduleHideHint()

    def __tryShowSelectedState(self):
        if self.__ammoCtrl is not None and self.__ammoCtrl.getNextShellCD() == self.__targetIntCD:
            self.__onNextShellChanged(self.__targetIntCD)
        return

    def _resolveTargetIntCD(self):
        return getBestPiercingShellCD(self.__sessionProvider.shared.ammo)

    def _scheduleHideHint(self):
        self._delayer.delayCallback(self._duration / 2.0, self._hideHint)

    def _getHintText(self):
        return backport.text(R.strings.battle_hints.contextHint.consumablesPanel.ammoReloadPrepare())

    @staticmethod
    def _getConfirmHintText():
        return backport.text(R.strings.battle_hints.contextHint.consumablesPanel.ammoReloadConfirm())
