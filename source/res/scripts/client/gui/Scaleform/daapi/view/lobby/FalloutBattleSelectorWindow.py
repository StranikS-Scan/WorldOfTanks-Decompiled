# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/FalloutBattleSelectorWindow.py
from adisp import process
from gui.Scaleform.daapi.view.meta.FalloutBattleSelectorWindowMeta import FalloutBattleSelectorWindowMeta
from gui.Scaleform.locale.FALLOUT import FALLOUT
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.prb_control.entities.base.ctx import PrbAction, LeavePrbAction
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared.formatters.text_styles import promoSubTitle, main
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from messenger.ext import channel_num_gen
from messenger.ext.channel_num_gen import SPECIAL_CLIENT_WINDOWS
from skeletons.gui.game_control import IFalloutController

class FalloutBattleSelectorWindow(FalloutBattleSelectorWindowMeta, IGlobalListener):
    falloutCtrl = dependency.descriptor(IFalloutController)

    def onSelectCheckBoxAutoSquad(self, isSelected):
        self.falloutCtrl.setAutomatch(isSelected)

    def onWindowMinimize(self):
        self.destroy()

    def onWindowClose(self):
        if not self.prbDispatcher.getFunctionalState().hasLockedState:
            self.__doClose()

    def onDominationBtnClick(self):
        self.__doSelect(PREBATTLE_ACTION_NAME.FALLOUT_CLASSIC)

    def onMultiteamBtnClick(self):
        self.__doSelect(PREBATTLE_ACTION_NAME.FALLOUT_MULTITEAM)

    def onEnqueued(self, queueType, *args):
        self.as_setBtnStatesS(self.__getBtnsStateData(False))
        self._onBtnsDisableStateChanged()

    def onDequeued(self, queueType, *args):
        self.as_setBtnStatesS(self.__getBtnsStateData(True))
        self._onBtnsDisableStateChanged()

    def onPrbEntitySwitched(self):
        self.destroy()

    def onUnitFlagsChanged(self, flags, timeLeft):
        if self.prbEntity.hasLockedState():
            if flags.isInSearch() or flags.isInQueue() or flags.isInArena():
                self.as_setBtnStatesS(self.__getBtnsStateData(False))
        else:
            self.as_setBtnStatesS(self.__getBtnsStateData(True))
        self._onBtnsDisableStateChanged()

    def getClientID(self):
        return channel_num_gen.getClientID4SpecialWindow(SPECIAL_CLIENT_WINDOWS.FALLOUT)

    def _populate(self):
        super(FalloutBattleSelectorWindow, self)._populate()
        self.startGlobalListening()
        self.falloutCtrl.onSettingsChanged += self.__updateFalloutSettings
        self.falloutCtrl.onAutomatchChanged += self.__updateFalloutSettings
        self.__updateFalloutSettings()
        if self.prbDispatcher.getFunctionalState().hasLockedState or not self.falloutCtrl.canChangeBattleType():
            self.as_setBtnStatesS(self.__getBtnsStateData(False))

    def _dispose(self):
        self.stopGlobalListening()
        self.falloutCtrl.onSettingsChanged -= self.__updateFalloutSettings
        self.falloutCtrl.onAutomatchChanged -= self.__updateFalloutSettings
        super(FalloutBattleSelectorWindow, self)._dispose()

    def _getTooltipData(self):
        data = {'autoSquadStr': makeTooltip(TOOLTIPS.FALLOUTBATTLESELECTORWINDOW_INFO_HEADER, TOOLTIPS.FALLOUTBATTLESELECTORWINDOW_INFO_BODY, attention=TOOLTIPS.FALLOUTBATTLESELECTORWINDOW_INFO_ALERT)}
        data['dominationStr'] = TOOLTIPS.BATTLESELECTORWINDOW_TOOLTIP_DOMINATION_SELECTBTN
        data['multiteamStr'] = TOOLTIPS.BATTLESELECTORWINDOW_TOOLTIP_MULTITEAM_SELECTBTN
        if self.prbDispatcher.getFunctionalState().hasLockedState:
            data['dominationStr'] = TOOLTIPS.FALLOUTBATTLESELECTORWINDOW_BTNDISABLED
            data['multiteamStr'] = TOOLTIPS.FALLOUTBATTLESELECTORWINDOW_BTNDISABLED
        elif not self.falloutCtrl.canChangeBattleType():
            data['dominationStr'] = TOOLTIPS.FALLOUTBATTLESELECTORWINDOW_BTNINSQUADDISABLED
            data['multiteamStr'] = TOOLTIPS.FALLOUTBATTLESELECTORWINDOW_BTNINSQUADDISABLED
        return data

    def _onBtnsDisableStateChanged(self):
        self.as_setTooltipsS(self._getTooltipData())

    def __getBtnsStateData(self, isEnabled):
        return {'dominationBtnEnabled': isEnabled,
         'multiteamBtnEnabled': isEnabled,
         'closeBtnEnabled': isEnabled,
         'autoSquadCheckboxEnabled': isEnabled}

    def __updateFalloutSettings(self):
        if not self.falloutCtrl.isEnabled():
            return self.onWindowClose()
        self.as_setInitDataS({'windowTitle': FALLOUT.BATTLESELECTORWINDOW_TITLE,
         'headerTitleStr': promoSubTitle(FALLOUT.BATTLESELECTORWINDOW_HEADERTITLESTR),
         'headerDescStr': main(FALLOUT.BATTLESELECTORWINDOW_HEADERDESC),
         'dominationBattleTitleStr': promoSubTitle(FALLOUT.BATTLESELECTORWINDOW_DOMINATION_TITLE),
         'dominationBattleDescStr': main(FALLOUT.BATTLESELECTORWINDOW_DOMINATION_DESCR),
         'dominationBattleBtnStr': FALLOUT.BATTLESELECTORWINDOW_DOMINATIONBATTLEBTNLBL,
         'multiteamTitleStr': promoSubTitle(FALLOUT.BATTLESELECTORWINDOW_MULTITEAM_TITLE),
         'multiteamDescStr': main(FALLOUT.BATTLESELECTORWINDOW_MULTITEAM_DESCR),
         'multiteamBattleBtnStr': FALLOUT.BATTLESELECTORWINDOW_MULTITEAMBATTLEBTNLBL,
         'bgImg': RES_ICONS.MAPS_ICONS_LOBBY_FALLOUTBATTLESELECTORBG,
         'multiteamAutoSquadEnabled': self.falloutCtrl.isAutomatch(),
         'multiteamAutoSquadLabel': FALLOUT.FALLOUTBATTLESELECTORWINDOW_AUTOSQUAD_LABEL,
         'tooltipData': self._getTooltipData()})
        if self.prbDispatcher.getFunctionalState().hasLockedState or not self.falloutCtrl.canChangeBattleType():
            self.as_setBtnStatesS(self.__getBtnsStateData(False))
        else:
            self.as_setBtnStatesS(self.__getBtnsStateData(True))
        self._onBtnsDisableStateChanged()

    @process
    def __doClose(self):
        yield self.prbDispatcher.doLeaveAction(LeavePrbAction())

    @process
    def __doSelect(self, prebattleActionName):
        yield self.prbDispatcher.doSelectAction(PrbAction(prebattleActionName))
