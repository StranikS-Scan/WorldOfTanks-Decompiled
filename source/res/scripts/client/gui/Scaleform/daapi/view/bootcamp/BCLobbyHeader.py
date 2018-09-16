# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCLobbyHeader.py
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import LobbyHeader
from gui.Scaleform.Waiting import Waiting
from gui.prb_control.events_dispatcher import g_eventDispatcher
from bootcamp.BootCampEvents import g_bootcampEvents
from bootcamp.Bootcamp import g_bootcamp
from bootcamp.aop.in_garage import PointcutBattleSelectorHintText
_ALLOWED_ENABLED_BUTTONS = [LobbyHeader.BUTTONS.SETTINGS, LobbyHeader.BUTTONS.BATTLE_SELECTOR]

class BCLobbyHeader(LobbyHeader):

    def __init__(self):
        super(BCLobbyHeader, self).__init__()
        self.__battleSelectorHintPointcutIndex = None
        return

    def fightClick(self, _, __):
        g_bootcampEvents.onGarageLessonFinished(0)

    def as_doDisableHeaderButtonS(self, btnId, isEnabled):
        if btnId not in _ALLOWED_ENABLED_BUTTONS:
            isEnabled = False
        super(BCLobbyHeader, self).as_doDisableHeaderButtonS(btnId, isEnabled)

    def _populate(self):
        super(BCLobbyHeader, self)._populate()
        if self.app.battleSelectorHintOverride is not None:
            self.__onOverrideBattleSelectorHint()
        return

    def _getWalletBtnDoText(self, _):
        return None

    def _getPremiumLabelText(self, _, __):
        pass

    def _getPremiumTooltipText(self, _, __):
        pass

    def _onPopulateEnd(self):
        self.as_initOnlineCounterS(False)

    def _dispose(self):
        Waiting.hide('updating')
        super(BCLobbyHeader, self)._dispose()

    def _getWalletBtnData(self, btnType, value, formatter, isHasAction=False, isDiscountEnabled=False, isNew=False):
        if btnType not in _ALLOWED_ENABLED_BUTTONS:
            isHasAction = False
        return super(BCLobbyHeader, self)._getWalletBtnData(btnType, value, formatter, isHasAction, isDiscountEnabled, isNew)

    def _addListeners(self):
        super(BCLobbyHeader, self)._addListeners()
        self.app.onBattleSelectorHintOverride += self.__onOverrideBattleSelectorHint

    def _removeListeners(self):
        super(BCLobbyHeader, self)._removeListeners()
        self.app.onBattleSelectorHintOverride -= self.__onOverrideBattleSelectorHint

    def __onOverrideBattleSelectorHint(self):
        enableOverride = self.app.battleSelectorHintOverride == 'bootcamp'
        isOverrideEnabled = self.__battleSelectorHintPointcutIndex is not None
        if enableOverride != isOverrideEnabled:
            if enableOverride:
                self.__battleSelectorHintPointcutIndex = g_bootcamp.addPointcut(PointcutBattleSelectorHintText)
            else:
                g_bootcamp.removePointcut(self.__battleSelectorHintPointcutIndex)
                self.__battleSelectorHintPointcutIndex = None
            g_eventDispatcher.updateUI()
        return
