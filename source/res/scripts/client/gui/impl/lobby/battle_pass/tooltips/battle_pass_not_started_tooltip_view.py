# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/tooltips/battle_pass_not_started_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.battle_pass_not_started_tooltip_view_model import BattlePassNotStartedTooltipViewModel
from gui.impl.pub import ViewImpl
from helpers import dependency, time_utils
from skeletons.gui.game_control import IBattlePassController

class BattlePassNotStartedTooltipView(ViewImpl):
    __battlePassController = dependency.descriptor(IBattlePassController)
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.battle_pass.tooltips.BattlePassNotStartedTooltipView())
        settings.model = BattlePassNotStartedTooltipViewModel()
        super(BattlePassNotStartedTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattlePassNotStartedTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BattlePassNotStartedTooltipView, self)._onLoading(*args, **kwargs)
        with self.getViewModel().transaction() as model:
            timeStart = self.__battlePassController.getSeasonStartTime()
            date = ''
            if timeStart > time_utils.getServerUTCTime():
                sday, smonth = self.__getDayMonth(timeStart)
                day = str(sday)
                month = backport.text(R.strings.menu.dateTime.months.num(smonth)())
                date = backport.text(R.strings.battle_pass_2020.tooltips.notStarted.date(), day=day, month=month)
            model.setDate(date)
            model.setSeasonNum(self.__battlePassController.getSeasonNum())

    @staticmethod
    def __getDayMonth(timeStamp):
        timeStruct = time_utils.getTimeStructInUTC(timeStamp)
        return (timeStruct.tm_mday, timeStruct.tm_mon)
