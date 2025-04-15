# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/impl/battle/battle_page/fall_tanks_postmortem_info_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from fall_tanks.gui.battle_control.mixins import FallTanksBattleMixin
from fall_tanks.gui.impl.gen.view_models.views.battle.battle_page.fall_tanks_postmortem_info_view_model import FallTanksPostmortemInfoViewModel

class FallTanksPostmortemInfoView(ViewImpl, FallTanksBattleMixin):

    def __init__(self):
        viewSettings = ViewSettings(R.views.fall_tanks.battle.FallTanksPostmortemInfoView(), ViewFlags.VIEW, FallTanksPostmortemInfoViewModel())
        super(FallTanksPostmortemInfoView, self).__init__(viewSettings)

    @property
    def viewModel(self):
        return super(FallTanksPostmortemInfoView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(FallTanksPostmortemInfoView, self)._initialize()
        self.startFallTanksAttachedListening(self.__invalidate)

    def _finalize(self):
        self.stopFallTanksAttachedListening(self.__invalidate)
        super(FallTanksPostmortemInfoView, self)._finalize()

    def __invalidate(self, attachedInfo):
        self.viewModel.setIsFinished(attachedInfo.isFinished)
