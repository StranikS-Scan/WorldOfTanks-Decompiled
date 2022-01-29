# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lunar_ny/tooltips/envelope_tooltip.py
import logging
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lunar_ny.tooltips.envelope_tooltip_model import EnvelopeTooltipModel, EnvelopeType
from gui.impl.pub import ViewImpl
from helpers import dependency
from lunar_ny import ILunarNYController
_logger = logging.getLogger(__name__)

class EnvelopeTooltip(ViewImpl[EnvelopeTooltipModel]):
    __lunarNYController = dependency.descriptor(ILunarNYController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.lunar_ny.tooltips.EnvelopeTooltip())
        settings.model = EnvelopeTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(EnvelopeTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(EnvelopeTooltip, self)._onLoading(*args, **kwargs)
        envelopeType = kwargs.get('envelopeType')
        isInShop = kwargs.get('isInShop', False)
        if envelopeType is not None:
            envelopeType = EnvelopeType(envelopeType)
            if isInShop:
                count = 1
            else:
                count = self.__lunarNYController.giftSystem.getEnvelopesEntitlementCountByType(envelopeType)
            with self.viewModel.transaction() as model:
                model.setEnvelopeType(envelopeType)
                model.setEnvelopesCount(count)
                model.setHasSentEnvelope(self.__lunarNYController.giftSystem.envelopeInSecretSantaPoll(envelopeType))
                model.setSecretSantaSentLimitTime(self.__lunarNYController.giftSystem.getSecretSantaSentPeriodLimit())
                if envelopeType != EnvelopeType.PREMIUMPAID:
                    model.setRareCharmsProbability(int(self.__lunarNYController.getMinRareCharmProbability()))
        else:
            _logger.error("Cann't find envelopeType in kwargs")
        return
