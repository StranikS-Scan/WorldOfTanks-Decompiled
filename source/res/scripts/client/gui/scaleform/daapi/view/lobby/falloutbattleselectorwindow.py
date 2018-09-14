# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/FalloutBattleSelectorWindow.py
from adisp import process
from constants import FALLOUT_BATTLE_TYPE, QUEUE_TYPE
from gui.game_control import getFalloutCtrl
from gui.prb_control.context import prb_ctx
from gui.prb_control.prb_helpers import GlobalListener
from gui.shared import events, EVENT_BUS_SCOPE
from gui.Scaleform.daapi.view.meta.FalloutBattleSelectorWindowMeta import FalloutBattleSelectorWindowMeta
from gui.Scaleform.locale.FALLOUT import FALLOUT
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.formatters.text_styles import promoSubTitle, main

class FalloutBattleSelectorWindow(FalloutBattleSelectorWindowMeta, GlobalListener):

    def __init__(self, ctx = None):
        super(FalloutBattleSelectorWindow, self).__init__(ctx)

    def _populate(self):
        super(FalloutBattleSelectorWindow, self)._populate()
        self.addListener(events.HideWindowEvent.HIDE_BATTLE_SESSION_WINDOW, self.__handleFalloutWindowHide, scope=EVENT_BUS_SCOPE.LOBBY)
        self.startGlobalListening()
        self.__falloutCtrl = getFalloutCtrl()
        self.__falloutCtrl.onSettingsChanged += self.__updateFalloutSettings
        self.as_setInitDataS({'windowTitle': FALLOUT.BATTLESELECTORWINDOW_TITLE,
         'headerTitleStr': promoSubTitle(FALLOUT.BATTLESELECTORWINDOW_HEADERTITLESTR),
         'headerDescStr': main(FALLOUT.BATTLESELECTORWINDOW_HEADERDESC),
         'dominationBattleTitleStr': promoSubTitle(FALLOUT.BATTLESELECTORWINDOW_DOMINATION_TITLE),
         'dominationBattleDescStr': main(FALLOUT.BATTLESELECTORWINDOW_DOMINATION_DESCR),
         'dominationBattleBtnStr': FALLOUT.BATTLESELECTORWINDOW_DOMINATIONBATTLEBTNLBL,
         'multiteamTitleStr': promoSubTitle(FALLOUT.BATTLESELECTORWINDOW_MULTITEAM_TITLE),
         'multiteamDescStr': main(FALLOUT.BATTLESELECTORWINDOW_MULTITEAM_DESCR),
         'multiteamBattleBtnStr': FALLOUT.BATTLESELECTORWINDOW_MULTITEAMBATTLEBTNLBL,
         'bgImg': RES_ICONS.MAPS_ICONS_LOBBY_FALLOUTBATTLESELECTORBG})
        if self.prbDispatcher.getFunctionalState().hasLockedState:
            self.as_setBtnStatesS({'dominationBtnEnabled': False,
             'multiteamBtnEnabled': False,
             'closeBtnEnabled': False})

    def _dispose(self):
        self.stopGlobalListening()
        self.removeListener(events.HideWindowEvent.HIDE_BATTLE_SESSION_WINDOW, self.__handleFalloutWindowHide, scope=EVENT_BUS_SCOPE.LOBBY)
        if self.__falloutCtrl:
            self.__falloutCtrl.onSettingsChanged -= self.__updateFalloutSettings
        self.__falloutCtrl = None
        super(FalloutBattleSelectorWindow, self)._dispose()
        return

    def onWindowMinimize(self):
        self.destroy()

    def onWindowClose(self):
        self.__leaveFallout()

    def onDominationBtnClick(self):
        getFalloutCtrl().setBattleType(FALLOUT_BATTLE_TYPE.CLASSIC)
        self.onWindowMinimize()

    def onMultiteamBtnClick(self):
        getFalloutCtrl().setBattleType(FALLOUT_BATTLE_TYPE.MULTITEAM)
        self.onWindowMinimize()

    def onEnqueued(self):
        self.as_setBtnStatesS({'dominationBtnEnabled': False,
         'multiteamBtnEnabled': False,
         'closeBtnEnabled': False})

    def onDequeued(self):
        self.as_setBtnStatesS({'dominationBtnEnabled': True,
         'multiteamBtnEnabled': True,
         'closeBtnEnabled': True})

    def onUnitFlagsChanged(self, flags, timeLeft):
        if self.unitFunctional.hasLockedState():
            if flags.isInSearch() or flags.isInQueue() or flags.isInArena():
                self.as_setBtnStatesS({'dominationBtnEnabled': False,
                 'multiteamBtnEnabled': False,
                 'closeBtnEnabled': False})
        else:
            self.as_setBtnStatesS({'dominationBtnEnabled': True,
             'multiteamBtnEnabled': True,
             'closeBtnEnabled': True})

    def __handleFalloutWindowHide(self, _):
        self.destroy()

    def __updateFalloutSettings(self, *args):
        if not self.__falloutCtrl.isEnabled():
            self.onWindowClose()

    @process
    def __leaveFallout(self):
        yield self.prbDispatcher.join(prb_ctx.JoinModeCtx(QUEUE_TYPE.RANDOMS))
