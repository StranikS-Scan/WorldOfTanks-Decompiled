# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/LobbyMenu.py
from adisp import process
from helpers import i18n
from gui import DialogsInterface, game_control
from gui.app_loader import g_appLoader
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID
from gui.Scaleform.daapi.view.meta.LobbyMenuMeta import LobbyMenuMeta

class LobbyMenu(LobbyMenuMeta):

    def versionInfoClick(self):
        game_control.g_instance.promo.showPatchPromo()
        self.destroy()

    def settingsClick(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.SETTINGS_WINDOW, ctx={'redefinedKeyMode': False}), EVENT_BUS_SCOPE.LOBBY)

    def onWindowClose(self):
        self.destroy()

    def cancelClick(self):
        self.destroy()

    @process
    def refuseTraining(self):
        isOk = yield DialogsInterface.showI18nConfirmDialog('refuseTraining')
        if isOk:
            g_eventBus.handleEvent(events.TutorialEvent(events.TutorialEvent.STOP_TRAINING), scope=EVENT_BUS_SCOPE.GLOBAL)
        self.destroy()

    @process
    def logoffClick(self):
        isOk = yield DialogsInterface.showI18nConfirmDialog('disconnect', focusedID=DIALOG_BUTTON_ID.CLOSE)
        if isOk:
            self.destroy()
            g_appLoader.goToLoginByRQ()

    @process
    def quitClick(self):
        isOk = yield DialogsInterface.showI18nConfirmDialog('quit', focusedID=DIALOG_BUTTON_ID.CLOSE)
        if isOk:
            self.destroy()
            g_appLoader.quitFromGame()

    def _populate(self):
        super(LobbyMenu, self)._populate()
        message = self.__getPatchPromoMessage()
        self.as_setVersionMessageS(message, message is not None)
        return

    def __getPatchPromoMessage(self):
        if game_control.g_instance.promo.isPatchPromoAvailable():
            return (i18n.makeString(MENU.PROMO_PATCH_MESSAGE),)
        else:
            return None
