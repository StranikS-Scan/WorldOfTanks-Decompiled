# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wot_anniversary/tooltips/progression_box_tooltip.py
import logging
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wot_anniversary.tooltips.progression_box_tooltip_model import ProgressionBoxTooltipModel, State
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.wot_anniversary.bonus_packers import composeBonuses, getWotAnniversaryBonusPacker
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.wot_anniversary import IWotAnniversaryController
_logger = logging.getLogger(__name__)

class ProgressionBoxTooltip(ViewImpl):
    __wotAnniversaryController = dependency.descriptor(IWotAnniversaryController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.wot_anniversary.tooltips.ProgressionBoxTooltip(), model=ProgressionBoxTooltipModel(), args=args, kwargs=kwargs)
        super(ProgressionBoxTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ProgressionBoxTooltip, self).getViewModel()

    def _onLoading(self, stageIdx, *args, **kwargs):
        super(ProgressionBoxTooltip, self)._onLoading(*args, **kwargs)
        config = self.__wotAnniversaryController.config
        progressionTokenCount = self.__wotAnniversaryController.getProgressionTokenCount()
        if not 0 <= stageIdx < len(config.progression):
            _logger.error('Wrong stageIdx = %s. Progression config = %s', stageIdx, config.progression)
            return
        else:
            stageConfig = config.progression[stageIdx]
            previousStageConfig = config.progression[stageIdx - 1] if stageIdx - 1 >= 0 else None
            if progressionTokenCount >= stageConfig.tokenCount:
                state = State.RECEIVED
            elif not previousStageConfig is None:
                state = previousStageConfig.tokenCount <= progressionTokenCount < stageConfig.tokenCount and State.ACTIVE
            else:
                state = State.LOCKED
            with self.viewModel.transaction() as tx:
                tx.setState(state)
                tx.setEnvelopesLeft(stageConfig.tokenCount - progressionTokenCount)
                packBonusModelAndTooltipData(composeBonuses(stageConfig.rewards), tx.getBonuses(), packer=getWotAnniversaryBonusPacker())
            return
