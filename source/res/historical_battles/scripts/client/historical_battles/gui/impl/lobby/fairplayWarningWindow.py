# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/fairplayWarningWindow.py
from gui.impl.dialogs.dialog_template import DialogTemplateView
from gui.impl.dialogs.dialog_template_button import ConfirmButton
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders as Placeholder
from gui.impl.gen.view_models.views.dialogs.template_settings.default_dialog_template_settings import DisplayFlags
from gui.impl.dialogs.sub_views.icon.icon_set import IconSet
from historical_battles.gui.impl.dialogs.sub_views.content.text_with_warning_content import TextWithWarning
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from gui.impl.dialogs.sub_views.common.simple_text import ImageSubstitution
_DIMMER_ALPHA = 0.7

class FairPlayWarningWindow(DialogTemplateView):

    def __init__(self, reason=''):
        super(FairPlayWarningWindow, self).__init__()
        self.__reason = reason

    def _onLoading(self, *args, **kwargs):
        resWarning = R.strings.hb_lobby.fairPlayWarningWindow.dyn(self.__reason)
        self.setBackgroundImagePath(R.images.historical_battles.gui.maps.icons.backgrounds.vignette())
        self.setBackgroundDimmerAlpha(_DIMMER_ALPHA)
        self.setDisplayFlags(DisplayFlags.RESPONSIVEHEADER.value)
        self.setSubView(Placeholder.TITLE, SimpleTextTitle(resWarning.header()))
        icon = IconSet(R.images.historical_battles.gui.maps.icons.fairplayWindow.hb_fairplay_window())
        self.setSubView(Placeholder.ICON, icon)
        self.setSubView(Placeholder.CONTENT, TextWithWarning(resWarning.body(), resWarning.reason(), ImageSubstitution(R.images.gui.maps.icons.library.alertIcon2(), 'icon', 3, 7, 0, 0)))
        self.addButton(ConfirmButton(resWarning.button()))
        super(FairPlayWarningWindow, self)._onLoading(*args, **kwargs)
