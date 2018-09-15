# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ny/ny_chests_view.py
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.lobby.ny.ny_common import getRewardsRibbonData
from gui.Scaleform.daapi.view.meta.NYChestsViewMeta import NYChestsViewMeta
from gui.Scaleform.locale.NY import NY
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.shared.utils.HangarSpace import g_hangarSpace
from helpers import dependency
from helpers import i18n
from new_year.new_year_sounds import NYSoundEvents
from skeletons.new_year import INewYearUIManager, INewYearController
from gui.Scaleform.daapi.view.lobby.ny.ny_helper_view import NYHelperView

class NYChestsView(NYHelperView, NYChestsViewMeta):
    nyUIManager = dependency.descriptor(INewYearUIManager)
    newYearController = dependency.descriptor(INewYearController)
    __background_alpha__ = 0.0

    def __init__(self, ctx=None):
        super(NYChestsView, self).__init__(ctx)
        self.__isBtnEnabled = True
        self.__onLoadCallback = ctx.get('callback', None) if ctx is not None else None
        return

    def onOpenBtnClick(self):
        self.nyUIManager.buttonClickOpenNextChest()

    def onPlaySound(self, soundType):
        NYSoundEvents.playSound(soundType)

    def onCloseWindow(self):
        self.nyUIManager.buttonClickCloseChest()

    def __onChestDone(self):
        self._switchBack()

    def _populate(self):
        super(NYChestsView, self)._populate()
        self.as_setInitDataS({'closeBtnLabel': NY.CHESTVIEW_CLOSEBTNLABEL,
         'header': NY.CHESTVIEW_GETAWARD})
        self.__updateChestsInfo()
        self.nyUIManager.onChestGiftsLoaded += self.__onChestGiftLoaded
        self.nyUIManager.onChestGiftsDone += self.__onChestGiftsDone
        self.nyUIManager.onChestDone += self.__onChestDone
        self.newYearController.onStateChanged += self.__onNyStateChanged
        g_hangarSpace.onSpaceDestroy += self.__onSpaceDestroyed
        if self.__onLoadCallback:
            self.__onLoadCallback()

    def _dispose(self):
        self.nyUIManager.chestViewDone()
        self.newYearController.onStateChanged -= self.__onNyStateChanged
        self.nyUIManager.onChestGiftsLoaded -= self.__onChestGiftLoaded
        self.nyUIManager.onChestGiftsDone -= self.__onChestGiftsDone
        self.nyUIManager.onChestDone -= self.__onChestDone
        g_hangarSpace.onSpaceDestroy -= self.__onSpaceDestroyed
        super(NYChestsView, self)._dispose()

    def __onNyStateChanged(self, _):
        if not self.newYearController.isAvailable():
            self.destroy()

    def __onSpaceDestroyed(self):
        self._switchBack()

    def __onChestGiftLoaded(self, bonuses):
        self.as_setRewardDataS(getRewardsRibbonData(bonuses))
        self.as_showRewardRibbonS()
        self.__updateChestsInfo()

    def __onChestGiftsDone(self):
        self.as_hideRewardRibbonS()
        self.__updateChestsInfo()

    def __updateChestsInfo(self, *args):
        chestAmount = self.newYearController.chestStorage.count
        if chestAmount > 0:
            txt = i18n.makeString(NY.CHESTVIEW_STATUSLABEL, count=str(chestAmount))
        else:
            txt = i18n.makeString(NY.CHESTVIEW_STATUSLABEL_NOITEMS)
        self.as_setOpenBtnLabelS(txt)
