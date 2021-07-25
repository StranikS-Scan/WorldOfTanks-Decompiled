# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/dialogs/confirm_unpacking_dialog_view.py
import nations
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.auxiliary.instructors_helper import canInsertInstructorToSlot, getInstructorPageBackground
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.perk_base_model import PerkBaseModel
from gui.impl.gen.view_models.views.lobby.detachment.dialogs.confirm_unpacking_dialog_view_model import ConfirmUnpackingDialogViewModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.perk_tooltip_model import PerkTooltipModel
from gui.impl.lobby.detachment.tooltips.perk_tooltip import PerkTooltip
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.shared.gui_items.perk import PerkGUI
from helpers.dependency import descriptor
from skeletons.gui.detachment import IDetachmentCache
MIN_COUNT_PERKS = 1

class ConfirmUnpackingDialogView(FullScreenDialogView):
    __detachmentCache = descriptor(IDetachmentCache)
    __slots__ = ('_instructor', '_detachment', '_slotID', '_perksIDs', '_nationID')

    def __init__(self, ctx):
        settings = ViewSettings(R.views.lobby.detachment.dialogs.ConfirmUnpackingDialogView())
        settings.model = ConfirmUnpackingDialogViewModel()
        super(ConfirmUnpackingDialogView, self).__init__(settings)
        self._instructor = self.__detachmentCache.getInstructor(ctx.get('instrInvID'))
        self._detachment = self.__detachmentCache.getDetachment(ctx.get('detInvID'))
        self._slotID = ctx.get('slotID')
        self._perksIDs = ctx.get('perksIDs', [])
        self._nationID = ctx.get('nationID', nations.NONE_INDEX)

    @property
    def viewModel(self):
        return super(ConfirmUnpackingDialogView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if event.contentID == R.views.lobby.detachment.tooltips.PerkTooltip():
            perkId = event.getArgument('id')
            return PerkTooltip(perkId, tooltipType=PerkTooltipModel.INSTRUCTOR_PERK_TOOLTIP)

    def _setBaseParams(self, model):
        fromBarracks = not self._detachment
        isEnoughEmptySlots = True
        if self._detachment and self._instructor:
            isEnoughEmptySlots = canInsertInstructorToSlot(self._detachment.invID, self._instructor.invID, self._slotID, checkNations=False)
        canApply = not fromBarracks and isEnoughEmptySlots
        with model.transaction() as viewModel:
            if canApply:
                viewModel.setAcceptButtonText(R.strings.dialogs.detachment.confirmUnpacking.apply())
            else:
                viewModel.setAcceptButtonText(R.strings.dialogs.detachment.confirmUnpacking.recruit())
            viewModel.setCancelButtonText(R.strings.dialogs.common.cancel())
            model.setBackground(getInstructorPageBackground(self._instructor.pageBackground))
            viewModel.setNotEnoughSlots(isEnoughEmptySlots)
            viewModel.setCanApply(canApply)
            viewModel.setIcon(self._instructor.getPortraitName())
            viewModel.setNation(nations.MAP.get(self._nationID, ''))
            celebrityName = self._instructor.getCelebrityTokenName()
            if celebrityName:
                viewModel.setName(celebrityName)
            self.__fillPerks(viewModel)
        super(ConfirmUnpackingDialogView, self)._setBaseParams(model)

    def __fillPerks(self, model):
        perks = model.getPerks()
        perks.clear()
        perksCount = len(self._perksIDs)
        if perksCount > MIN_COUNT_PERKS:
            for perkID in self._perksIDs[:perksCount - 1]:
                perkModel = self.__fillPerk(perkID, PerkBaseModel())
                perks.addViewModel(perkModel)

            self.__fillPerk(self._perksIDs[perksCount - 1], model.additionalPerk)
        elif perksCount == MIN_COUNT_PERKS:
            perkModel = self.__fillPerk(self._perksIDs[MIN_COUNT_PERKS - 1], PerkBaseModel())
            perks.addViewModel(perkModel)
        perks.invalidate()

    def __fillPerk(self, perkID, perkModel):
        perk = PerkGUI(perkID)
        perkModel.setId(perkID)
        perkModel.setIcon(backport.image(R.images.gui.maps.icons.perks.normal.c_64x64.fill.dyn(perk.icon)()))
        perkModel.setName(perk.name)
        return perkModel
