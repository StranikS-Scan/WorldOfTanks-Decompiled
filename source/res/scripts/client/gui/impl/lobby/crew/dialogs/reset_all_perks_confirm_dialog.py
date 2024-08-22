# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/reset_all_perks_confirm_dialog.py
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.dialogs.sub_views.content.simple_text_content import SimpleTextContent
from gui.impl.dialogs.sub_views.icon.icon_set import IconSet
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders as Placeholder
from gui.impl.lobby.crew.dialogs.recruit_window.base_crew_dialog_template_with_blur_view import BaseCrewDialogTemplateWithBlurView
from uilogging.crew_nps.loggers import CrewNpsDialogLogger
from uilogging.crew_nps.logging_constants import CrewNpsDialogKeys, CrewNpsViewKeys

class ResetAllPerksConfirmDialog(BaseCrewDialogTemplateWithBlurView):

    def __init__(self, **kwargs):
        kwargs.setdefault('parentViewKey', CrewNpsViewKeys.BARRACKS)
        kwargs.setdefault('loggingKey', CrewNpsDialogKeys.RESET_ALL_CONFIRM)
        kwargs.setdefault('loggerClass', CrewNpsDialogLogger)
        super(ResetAllPerksConfirmDialog, self).__init__(**kwargs)

    def _onLoading(self, *args, **kwargs):
        rDialogTemplates = R.strings.dialogs.resetAllPerks
        rDialogs = R.images.gui.maps.uiKit.dialogs
        self.setSubView(Placeholder.TITLE, SimpleTextTitle(rDialogTemplates.title()))
        self.setSubView(Placeholder.ICON, IconSet(rDialogs.icons.alert(), [rDialogs.highlights.yellow_1()]))
        self.setSubView(Placeholder.CONTENT, SimpleTextContent(rDialogTemplates.warning()))
        self.addButton(ConfirmButton(rDialogTemplates.submit()))
        self.addButton(CancelButton(rDialogTemplates.cancel()))
        super(ResetAllPerksConfirmDialog, self)._onLoading(*args, **kwargs)
