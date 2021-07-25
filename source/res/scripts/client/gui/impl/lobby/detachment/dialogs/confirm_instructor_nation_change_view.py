# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/dialogs/confirm_instructor_nation_change_view.py
from frameworks.wulf import ViewSettings
from items.components.detachment_constants import NO_DETACHMENT_ID
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.dialogs.confirm_instructor_nation_change_view_model import ConfirmInstructorNationChangeViewModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from skeletons.gui.detachment import IDetachmentCache
from helpers.dependency import descriptor

class ConfirmInstructorNationChangeView(FullScreenDialogView):
    __detachmentCache = descriptor(IDetachmentCache)
    __slots__ = ('__detachmentInvID', '__nation')

    def __init__(self, ctx):
        settings = ViewSettings(R.views.lobby.detachment.dialogs.ConfirmInstructorNationChangeView())
        settings.model = ConfirmInstructorNationChangeViewModel()
        self.__detachmentInvID = ctx.get('detInvID', NO_DETACHMENT_ID)
        self.__nation = ctx['nation']
        super(ConfirmInstructorNationChangeView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ConfirmInstructorNationChangeView, self).getViewModel()

    def _setBaseParams(self, model):
        with model.transaction() as viewModel:
            detachment = self.__detachmentCache.getDetachment(self.__detachmentInvID)
            viewModel.setTitleBody(R.strings.detachment.nationChangeDialog.title())
            viewModel.setTankmanName(detachment.cmdrFullName)
            viewModel.setNation(detachment.nationName)
            viewModel.setNewNation(self.__nation)
            viewModel.setAcceptButtonText(R.strings.detachment.common.submit())
            viewModel.setCancelButtonText(R.strings.detachment.common.cancel())
        super(ConfirmInstructorNationChangeView, self)._setBaseParams(model)
