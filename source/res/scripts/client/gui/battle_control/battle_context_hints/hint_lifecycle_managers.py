# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/battle_context_hints/hint_lifecycle_managers.py
import logging
import typing
from helpers.CallbackDelayer import CallbackDelayer
from gui.battle_control.avatar_getter import getSoundNotifications
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


class KitHintLifecycleMgr(BaseHintLifecycleMgr):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, *args, **kwargs):
        super(KitHintLifecycleMgr, self).__init__(*args, **kwargs)
        self._component = None
        return

    def _doShowHint(self):
        _logger.debug('[BATTLE_CONTEXT_INTS] KitHintLifecycleMgr._doShowHint()')
        equipmentTag = self._context['equipmentTag']
        equipCtrl = self.__sessionProvider.shared.equipments
        if equipCtrl is None:
            if self._hintFinishedCallback is not None:
                self._hintFinishedCallback(self._hintId)
            return
        else:
            equipIntCD = None
            for intCD, item in equipCtrl.iterEquipmentsByTag(equipmentTag, lambda eq: eq.isAvailableToUse):
                equipIntCD = intCD
                if item.getDescriptor().name.startswith('large'):
                    break

            if equipIntCD is None:
                if self._hintFinishedCallback is not None:
                    self._hintFinishedCallback(self._hintId)
                return
            self._component.showContextHint(equipIntCD, equipmentTag)
            self._delayer.delayCallback(self._duration, self._hideHint)
            return

    def _doHideHint(self, applied=False):
        _logger.debug('[BATTLE_CONTEXT_INTS] KitHintLifecycleMgr._doHideHint(applied=%s)', applied)
        self._component.hideContextHint(applied)

    def applied(self):
        self._hideHint(True)
