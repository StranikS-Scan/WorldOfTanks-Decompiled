# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/tooltips/detachment_restore_tooltip.py
import typing
from crew2 import settings_globals
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.detachment_restore_tooltip_model import DetachmentRestoreTooltipModel
from gui.impl.auxiliary.detachment_helper import fillRestorePriceModel, getRecoveryTerms
from gui.impl.pub import ViewImpl
from helpers.dependency import descriptor
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.detachment import Detachment

class DetachmentRestoreTooltip(ViewImpl):
    __itemsCache = descriptor(IItemsCache)
    __detachmentCache = descriptor(IDetachmentCache)
    __slots__ = ('_detachment', '_detachmentSettings')

    def __init__(self, detachmentInvID=None):
        settings = ViewSettings(R.views.lobby.detachment.tooltips.DetachmentRestoreTooltip())
        settings.model = DetachmentRestoreTooltipModel()
        super(DetachmentRestoreTooltip, self).__init__(settings)
        self._detachment = self.__detachmentCache.getDetachment(detachmentInvID)
        self._detachmentSettings = settings_globals.g_detachmentSettings

    @property
    def viewModel(self):
        return super(DetachmentRestoreTooltip, self).getViewModel()

    def _onLoading(self):
        super(DetachmentRestoreTooltip, self)._onLoading()
        with self.viewModel.transaction() as model:
            fillRestorePriceModel(model.priceModel, self.__itemsCache.items.stats, self._detachment.invID)
            fullTerm, freeTerm, paidTerm = getRecoveryTerms(self._detachment, self._detachmentSettings)
            model.setFullTerm(fullTerm)
            model.setFreeTerm(freeTerm)
            model.setPaidTerm(paidTerm)
