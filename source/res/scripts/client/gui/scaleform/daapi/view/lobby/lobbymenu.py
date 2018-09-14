# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/LobbyMenu.py
import BigWorld
import constants
from adisp import process
from gui import DialogsInterface
from gui.Scaleform.daapi.view.common.settings.new_settings_counter import getCountNewSettings
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID
from gui.Scaleform.daapi.view.meta.LobbyMenuMeta import LobbyMenuMeta
from gui.Scaleform.daapi.view.dialogs.bootcamp_dialogs_meta import ExecutionChooserDialogMeta
from gui.Scaleform.genConsts.MENU_CONSTANTS import MENU_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.BOOTCAMP import BOOTCAMP
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.app_loader import g_appLoader
from gui.shared import event_dispatcher
from gui.shared.formatters import text_styles, icons
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from helpers import i18n, getShortClientVersion, dependency
from skeletons.gui.game_control import IPromoController
from skeletons.gui.game_control import IBootcampController
from skeletons.gui.lobby_context import ILobbyContext
from gui.prb_control import prbDispatcherProperty
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from PlayerEvents import g_playerEvents as events

def _getVersionMessage(promo):
    return {'message': '{0} {1}'.format(text_styles.main(i18n.makeString(MENU.PROMO_PATCH_MESSAGE)), text_styles.stats(getShortClientVersion())),
     'label': i18n.makeString(MENU.PROMO_TOARCHIVE),
     'promoEnabel': promo.isPatchPromoAvailable(),
     'tooltip': TOOLTIPS.LOBBYMENU_VERSIONINFOBUTTON}


class LobbyMenu(LobbyMenuMeta):
    promo = dependency.descriptor(IPromoController)
    bootcamp = dependency.descriptor(IBootcampController)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def versionInfoClick(self):
        self.promo.showVersionsPatchPromo()
        self.destroy()

    def settingsClick(self):
        event_dispatcher.showSettingsWindow(redefinedKeyMode=False)

    def onWindowClose(self):
        self.destroy()

    def cancelClick(self):
        self.destroy()

    def onEscapePress(self):
        self.destroy()

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    @process
    def refuseTraining(self):
        isOk = yield DialogsInterface.showI18nConfirmDialog('refuseTraining')
        if isOk:
            event_dispatcher.stopTutorial()
        self.destroy()

    @process
    def logoffClick(self):
        isOk = yield DialogsInterface.showI18nConfirmDialog('disconnect', focusedID=DIALOG_BUTTON_ID.CLOSE)
        if isOk:
            g_appLoader.goToLoginByRQ()

    @process
    def quitClick(self):
        isOk = yield DialogsInterface.showI18nConfirmDialog('quit', focusedID=DIALOG_BUTTON_ID.CLOSE)
        if isOk:
            g_appLoader.quitFromGame()

    def onCounterNeedUpdate(self):
        self.__updateNewSettingsCount()

    def bootcampClick(self):
        if self.bootcamp.isInBootcamp():
            if not self.bootcamp.needAwarding():
                self.bootcamp.stopBootcamp(False)
            else:
                self.__doBootcamp(isSkip=True)
        elif BigWorld.player().isLongDisconnectedFromCenter:
            DialogsInterface.showI18nInfoDialog('bootcampCenterUnavailable', lambda result: None)
        else:
            self.__doBootcamp(isSkip=False)

    def _populate(self):
        super(LobbyMenu, self)._populate()
        state = MENU_CONSTANTS.STATE_SHOW_ALL
        if self.bootcamp.isInBootcamp():
            state = MENU_CONSTANTS.STATE_HIDE_ALL
        elif constants.IS_CHINA:
            state = MENU_CONSTANTS.STATE_SHOW_SERVER_NAME
        elif not constants.IS_SHOW_SERVER_STATS:
            state = MENU_CONSTANTS.STATE_HIDE_SERVER_STATS_ITEM
        self.as_setMenuStateS(state)
        self.as_setVersionMessageS(_getVersionMessage(self.promo))
        bootcampIcon = RES_ICONS.MAPS_ICONS_BOOTCAMP_MENU_MENUBOOTCAMPICON
        bootcampIconSource = icons.makeImageTag(bootcampIcon, 33, 27, -8, 0)
        if self.bootcamp.isInBootcamp():
            self.as_setBootcampButtonLabelS(BOOTCAMP.REQUEST_BOOTCAMP_FINISH, bootcampIconSource)
        elif self.lobbyContext.getServerSettings().isBootcampEnabled():
            if self.bootcamp.runCount() > 0:
                bootcampLabel = BOOTCAMP.REQUEST_BOOTCAMP_RETURN
            else:
                bootcampLabel = BOOTCAMP.REQUEST_BOOTCAMP_START
            self.as_setBootcampButtonLabelS(bootcampLabel, bootcampIconSource)
        else:
            self.as_showBootcampButtonS(False)
        if events.isPlayerEntityChanging:
            self.as_showBootcampButtonS(False)

    def __updateNewSettingsCount(self):
        userLogin = getattr(BigWorld.player(), 'name', '')
        if userLogin == '':
            return
        newSettingsCnt = getCountNewSettings()
        if newSettingsCnt > 0:
            self.as_setCounterS([{'componentId': 'settingsBtn',
              'count': str(newSettingsCnt)}])
        else:
            self.as_removeCounterS(['settingsBtn'])

    @process
    def __doBootcamp(self, isSkip):
        dialogType, focusedID = (ExecutionChooserDialogMeta.SKIP, DIALOG_BUTTON_ID.CLOSE) if isSkip else (ExecutionChooserDialogMeta.RETRY, DIALOG_BUTTON_ID.SUBMIT)
        dialogKey = 'bootcamp/' + dialogType
        needAwarding = self.bootcamp.needAwarding()
        if not isSkip and needAwarding:
            dialogKey = 'bootcamp/' + ExecutionChooserDialogMeta.START
        result = yield DialogsInterface.showDialog(ExecutionChooserDialogMeta(dialogType, dialogKey, focusedID, not needAwarding and not isSkip))
        if result:
            self.bootcamp.showActionWaitWindow()
            if isSkip:
                self.bootcamp.stopBootcamp(False)
            elif self.prbDispatcher is not None:
                action = PrbAction(PREBATTLE_ACTION_NAME.BOOTCAMP)
                yield self.prbDispatcher.doSelectAction(action)
            self.destroy()
        return
