# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/extra_intro_view.py
from account_helpers.settings_core.settings_constants import BattlePassStorageKeys
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import getVehicleCDForStyle
from gui.battle_pass.battle_pass_helpers import getStyleForChapter
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.extra_intro_view_model import ExtraIntroViewModel
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showBattlePass
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBattlePassController
from tutorial.control.game_vars import getVehicleByIntCD

class ExtraIntroView(ViewImpl):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __battlePassController = dependency.descriptor(IBattlePassController)

    def __init__(self, chapterID=0):
        settings = ViewSettings(R.views.lobby.battle_pass.ExtraIntroView())
        settings.flags = ViewFlags.VIEW
        settings.model = ExtraIntroViewModel()
        self.__chapterID = chapterID
        super(ExtraIntroView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ExtraIntroView, self).getViewModel()

    def activate(self):
        self._subscribe()
        self.__fillModel()

    def deactivate(self):
        self._unsubscribe()

    def onExtraChapterExpired(self):
        showBattlePass(R.aliases.battle_pass.ChapterChoice())

    def _onLoading(self, *args, **kwargs):
        super(ExtraIntroView, self)._onLoading(*args, **kwargs)
        self.__fillModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onSubmit), (self.__battlePassController.onBattlePassSettingsChange, self.__onBattlePassSettingsChanged), (self.__battlePassController.onSeasonStateChanged, self.__onBattlePassSettingsChanged))

    def __onSubmit(self):
        self.__settingsCore.serverSettings.saveInBPStorage({BattlePassStorageKeys.EXTRA_CHAPTER_INTRO_SHOWN: True})
        if self.__chapterID in self.__battlePassController.getMainChapterIDs():
            showBattlePass(R.aliases.battle_pass.Progression(), self.__chapterID)
        else:
            showBattlePass(R.aliases.battle_pass.ChapterChoice())

    def __onBattlePassSettingsChanged(self, *_):
        if self.__battlePassController.isPaused():
            showBattlePass()
        elif not self.__battlePassController.isChapterExists(self.__chapterID):
            showBattlePass(R.aliases.battle_pass.ChapterChoice())

    def __fillModel(self):
        style = getStyleForChapter(self.__chapterID)
        vehicleCD = getVehicleCDForStyle(style)
        vehicle = getVehicleByIntCD(vehicleCD)
        with self.viewModel.transaction() as tx:
            tx.setStyleName(style.userName)
            fillVehicleInfo(tx.vehicleInfo, vehicle)
