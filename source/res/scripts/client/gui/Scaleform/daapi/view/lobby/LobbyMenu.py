# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/LobbyMenu.py
import BigWorld
import constants
from adisp import process
from async import async, await
from gui import DialogsInterface
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID
from gui.impl.dialogs import dialogs
from account_helpers.counter_settings import getCountNewSettings
from gui.Scaleform.daapi.view.meta.LobbyMenuMeta import LobbyMenuMeta
from gui.Scaleform.genConsts.MENU_CONSTANTS import MENU_CONSTANTS
from gui.Scaleform.locale.BOOTCAMP import BOOTCAMP
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared import event_dispatcher
from gui.shared.formatters import text_styles, icons
from gui.sounds.ambients import LobbySubViewEnv
from helpers import i18n, getShortClientVersion, dependency
from skeletons.gui.game_control import IBootcampController
from skeletons.gameplay import IGameplayLogic
from skeletons.gui.game_control import IPromoController
from skeletons.gui.game_control import IManualController
from skeletons.gui.lobby_context import ILobbyContext
from PlayerEvents import g_playerEvents as events
from gui.prb_control import prbEntityProperty

def _getVersionMessage():
    return ('{0} {1}'.format(text_styles.main(i18n.makeString(MENU.PROMO_PATCH_MESSAGE)), text_styles.stats(getShortClientVersion())),)


class LobbyMenu(LobbyMenuMeta):
    __sound_env__ = LobbySubViewEnv
    promo = dependency.descriptor(IPromoController)
    bootcamp = dependency.descriptor(IBootcampController)
    lobbyContext = dependency.descriptor(ILobbyContext)
    gameplay = dependency.descriptor(IGameplayLogic)
    manualController = dependency.descriptor(IManualController)

    @prbEntityProperty
    def prbEntity(self):
        pass

    def postClick(self):
        self.destroy()
        self.promo.showFieldPost()

    def settingsClick(self):
        event_dispatcher.showSettingsWindow(redefinedKeyMode=False)

    def onWindowClose(self):
        self.destroy()

    def cancelClick(self):
        self.destroy()

    def onEscapePress(self):
        self.destroy()

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
            self.gameplay.goToLoginByDisconnectRQ()

    @async
    def quitClick(self):
        isOk = yield await(dialogs.quitGame(self.getParentWindow()))
        if isOk:
            self.gameplay.quitFromGame()

    def onCounterNeedUpdate(self):
        self.__updateNewSettingsCount()

    def bootcampClick(self):
        self.bootcamp.runBootcamp()

    def manualClick(self):
        if self.manualController.isActivated():
            view = self.manualController.getView()
            if view is not None:
                self.destroy()
            else:
                self.manualController.show()
        return

    def _populate(self):
        super(LobbyMenu, self)._populate()
        self.__addListeners()
        state = MENU_CONSTANTS.STATE_SHOW_ALL
        if self.bootcamp.isInBootcamp():
            state = MENU_CONSTANTS.STATE_HIDE_ALL
        elif constants.IS_CHINA:
            state = MENU_CONSTANTS.STATE_SHOW_SERVER_NAME
        elif not constants.IS_SHOW_SERVER_STATS:
            state = MENU_CONSTANTS.STATE_HIDE_SERVER_STATS_ITEM
        self.as_setMenuStateS(state)
        self.as_setVersionMessageS('{0} {1}'.format(text_styles.main(i18n.makeString(MENU.PROMO_PATCH_MESSAGE)), text_styles.stats(getShortClientVersion())))
        postIconClose = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_POST_CLOSE, 26, 22, -5, 0)
        postIconOpen = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_POST_OPEN, 26, 22, -5, 0)
        self.as_setPostButtonIconsS(postIconClose, postIconOpen)
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
        isBootCampDisabled = BigWorld.player().spaFlags.getFlag(constants.SPA_ATTRS.BOOTCAMP_DISABLED)
        if isBootCampDisabled:
            self.as_showBootcampButtonS(False)
        if events.isPlayerEntityChanging:
            self.as_showBootcampButtonS(False)
        if not self.manualController.isActivated() or self.bootcamp.isInBootcamp() or self.__isInQueue():
            self.as_showManualButtonS(False)
        self.__setPostFieldButtonVisible(self.promo.isActive())

    def _dispose(self):
        self.__removeListeners()
        super(LobbyMenu, self)._dispose()

    def __isInQueue(self):
        return self.prbEntity and self.prbEntity.isInQueue()

    def __updateNewSettingsCount(self):
        userLogin = getattr(BigWorld.player(), 'name', '')
        if userLogin == '':
            return
        toShow, toHide = [], []
        counts = {'settingsBtn': getCountNewSettings(),
         'postBtn': self.promo.getPromoCount()}
        for componentID, count in counts.iteritems():
            if count > 0:
                toShow.append({'componentId': componentID,
                 'count': str(count)})
            toHide.append(componentID)

        if toShow:
            self.as_setCounterS(toShow)
        if toHide:
            self.as_removeCounterS(toHide)

    def __addListeners(self):
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self.promo.onPromoCountChanged += self.__updateNewSettingsCount

    def __removeListeners(self):
        self.promo.onPromoCountChanged -= self.__updateNewSettingsCount
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged

    def __onServerSettingChanged(self, diff):
        if 'isManualEnabled' in diff:
            manualButtonEnabled = diff['isManualEnabled']
            self.as_showManualButtonS(manualButtonEnabled)
        if 'isFieldPostEnabled' in diff:
            self.__setPostFieldButtonVisible(diff['isFieldPostEnabled'])

    def __setPostFieldButtonVisible(self, isVisible):
        self.as_setPostButtonVisibleS(isVisible and not self.__isInQueue())
