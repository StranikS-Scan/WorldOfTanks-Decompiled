# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/battle/help_view.py
from frameworks.wulf import ViewSettings, WindowLayer, WindowFlags
from gui.app_loader.settings import APP_NAME_SPACE
from gui.battle_control import avatar_getter
from gui.impl.gen import R
from gui.impl.pub import ViewImpl, WindowImpl
from helpers import dependency
from historical_battles.gui.impl.gen.view_models.views.battle.help_view_model import HelpViewModel
from historical_battles.gui.impl.gen.view_models.views.common.help_hint_model import HelpHintModel
from skeletons.gui.app_loader import IAppLoader

class HelpView(ViewImpl):

    def __init__(self):
        settings = ViewSettings(R.views.historical_battles.battle.HelpView(), model=HelpViewModel())
        super(HelpView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(HelpView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(HelpView, self)._onLoading(*args, **kwargs)
        self.__fillViewModel()

    def __fillViewModel(self):
        from historical_battles.gui.Scaleform.daapi.view.battle.slides import LoadingScreenSlidesCfg
        arena = avatar_getter.getArena()
        hintList = LoadingScreenSlidesCfg.instance().getLoadingScreen(arena.arenaType.geometryName).slides
        with self.viewModel.transaction() as tx:
            tx.setTitle(R.strings.hb_battle.helpScreen.missionTitle.num(arena.guiType)())
            hintVL = tx.getHints()
            hintVL.clear()
            for hintData in hintList:
                battleData = hintData.getBattleData()
                hintModel = HelpHintModel()
                hintModel.setTitle(battleData.get('title', ''))
                hintModel.setDescription(battleData.get('description', ''))
                hintModel.setBackground(battleData.get('background', ''))
                hintVL.addViewModel(hintModel)

            hintVL.invalidate()


class HelpWindow(WindowImpl):
    __slots__ = ()
    appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, parent=None):
        super(HelpWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, content=HelpView(), layer=WindowLayer.OVERLAY, parent=parent)

    @property
    def _battleApp(self):
        return self.appLoader.getApp(APP_NAME_SPACE.SF_BATTLE)

    def _initialize(self):
        super(HelpWindow, self)._initialize()
        self._battleApp.enterGuiControlMode(R.views.historical_battles.battle.HelpView(), cursorVisible=True, enableAiming=False)

    def _finalize(self):
        self._battleApp.leaveGuiControlMode(R.views.historical_battles.battle.HelpView())
        super(HelpWindow, self)._finalize()
