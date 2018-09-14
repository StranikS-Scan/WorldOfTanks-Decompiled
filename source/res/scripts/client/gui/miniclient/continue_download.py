# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/miniclient/continue_download.py
import BigWorld
from gui import GUI_SETTINGS
from gui.DialogsInterface import showDialog
from gui.Scaleform.daapi.view.dialogs import SimpleDialogMeta, I18nConfirmDialogButtons, DIALOG_BUTTON_ID
from helpers import aop
from helpers.i18n import makeString as _ms

class _PrepareLibrariesListAspect(aop.Aspect):

    def atReturn(self, cd):
        original_return_value = list(cd.returned)
        original_return_value.append('miniClient.swf')
        cd.change()
        return original_return_value


class PrepareLibrariesListPointcut(aop.Pointcut):

    def __init__(self):
        aop.Pointcut.__init__(self, 'gui.Scaleform.lobby_entry', 'LobbyEntry', '_getRequiredLibraries', aspects=(_PrepareLibrariesListAspect,))


class _OnHyperlinkClickAspect(aop.Aspect):

    def atCall(self, cd):
        cd.avoid()
        _show_continue_client_download_dialog()


class _OnBrowserHyperlinkClickAspect(aop.Aspect):

    def atCall(self, cd):
        if cd.args[0] == _getContinueDownloadUrl():
            cd.avoid()
            _show_continue_client_download_dialog()
            return True


class _OnFailLoadingFrameAspect(aop.Aspect):

    def atCall(self, cd):
        cd.avoid()
        if cd.args[1] and cd.args[4] == _getContinueDownloadUrl():
            cd.self.onLoadEnd(True)


class OnHyperlinkClickPointcut(aop.Pointcut):

    def __init__(self):
        aop.Pointcut.__init__(self, 'gui.Scaleform.daapi.view.meta.MiniClientComponentMeta', 'MiniClientComponentMeta', 'onHyperlinkClick', aspects=(_OnHyperlinkClickAspect,))


class OnSquadHyperlinkClickPointcut(aop.Pointcut):

    def __init__(self):
        aop.Pointcut.__init__(self, 'gui.Scaleform.daapi.view.lobby.prb_windows.SquadPromoWindow', 'SquadPromoWindow', 'onHyperlinkClick', aspects=(_OnHyperlinkClickAspect,))


class OnBrowserHyperlinkClickPointcut(aop.Pointcut):

    def __init__(self):
        aop.Pointcut.__init__(self, 'WebBrowser', 'EventListener', 'onFilterNavigation', aspects=(_OnBrowserHyperlinkClickAspect,))


class OnFailLoadingFramePointcut(aop.Pointcut):

    def __init__(self):
        aop.Pointcut.__init__(self, 'WebBrowser', 'EventListener', 'onFailLoadingFrame', aspects=(_OnFailLoadingFrameAspect,))


class OnChrismasAwardgHyperLinkPointcut(aop.Pointcut):

    def __init__(self):
        aop.Pointcut.__init__(self, 'gui.awards.special_achievement_awards', 'ChristmasAward', 'handleWarningHyperlinkClick', aspects=(_OnHyperlinkClickAspect,))


def _show_continue_client_download_dialog():
    showDialog(SimpleDialogMeta(title=_ms('#miniclient:continue_download_dialog/title'), message=_ms('#miniclient:continue_download_dialog/message'), buttons=I18nConfirmDialogButtons(focusedIndex=DIALOG_BUTTON_ID.SUBMIT, i18nKey='questsConfirmDialog')), lambda proceed: BigWorld.wg_quitAndStartLauncher() if proceed else None)


def _getContinueDownloadUrl():
    return GUI_SETTINGS.miniclient['webBridgeRootURL'] + '/wot_client_url/'
