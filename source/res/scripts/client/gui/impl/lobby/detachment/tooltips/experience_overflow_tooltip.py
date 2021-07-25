# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/tooltips/experience_overflow_tooltip.py
from frameworks.wulf.view.view import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.experience_overflow_tooltip_model import ExperienceOverflowTooltipModel
from gui.impl.pub import ViewImpl
from helpers.dependency import descriptor
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.shared import IItemsCache

class ExperienceOverflowTooltip(ViewImpl):
    __detachmentCache = descriptor(IDetachmentCache)
    __itemsCache = descriptor(IItemsCache)
    __slots__ = ('_lostXP', '_usedXP')

    def __init__(self, detachmentInvID, bookItemCD):
        settings = ViewSettings(R.views.lobby.detachment.tooltips.ExperienceOverflowTooltip())
        settings.model = ExperienceOverflowTooltipModel()
        super(ExperienceOverflowTooltip, self).__init__(settings)
        detachment = self.__detachmentCache.getDetachment(detachmentInvID)
        bookItem = self.__itemsCache.items.getItemByCD(bookItemCD)
        progression = detachment.progression
        detDescr = detachment.getDescriptor()
        self._usedXP = progression.getLevelStartingXP(progression.maxLevel) - detDescr.experience
        self._lostXP = bookItem.getXP() - self._usedXP

    @property
    def viewModel(self):
        return super(ExperienceOverflowTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ExperienceOverflowTooltip, self)._onLoading()
        with self.viewModel.transaction() as model:
            model.setUsedExp(self._usedXP)
            model.setLostExp(self._lostXP)
