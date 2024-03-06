# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/custom_tankmen_voiceover_view.py
from frameworks.wulf import WindowFlags
from gui.battle_pass.sounds import BattlePassSounds
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.custom_tankmen_voiceover_view_model import CustomTankmenVoiceoverViewModel
from gui.impl.lobby.battle_pass.tankmen_voiceover_view import TankmenVoiceoverView
from gui.impl.pub.lobby_window import LobbyWindow
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController

class CustomTankmenVoiceoverView(TankmenVoiceoverView):
    __slots__ = ()
    __battlePass = dependency.descriptor(IBattlePassController)

    def __init__(self, ctx):
        super(CustomTankmenVoiceoverView, self).__init__(R.views.lobby.battle_pass.CustomTankmenVoiceoverView(), CustomTankmenVoiceoverViewModel, ctx=ctx)

    @property
    def viewModel(self):
        return super(CustomTankmenVoiceoverView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(CustomTankmenVoiceoverView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setSeasonNum(self.__battlePass.getSeasonNum())

    def _getStopSound(self):
        return BattlePassSounds.REGULAR_VOICEOVER_STOP


class CustomTankmenVoiceoverWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, parent=None, ctx=None):
        super(CustomTankmenVoiceoverWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=CustomTankmenVoiceoverView(ctx=ctx), parent=parent)
