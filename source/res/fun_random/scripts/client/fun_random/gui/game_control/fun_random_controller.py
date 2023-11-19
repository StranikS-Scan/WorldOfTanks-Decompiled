# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/game_control/fun_random_controller.py
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import FUN_RANDOM_LAST_PRESET
from adisp import adisp_async, adisp_process
from constants import Configs
from fun_random_common.fun_constants import FUN_EVENT_ID_KEY, DEFAULT_SETTINGS_KEY
from fun_random.gui.feature.sub_systems.fun_hidden_vehicles import FunHiddenVehicles
from fun_random.gui.feature.sub_systems.fun_notifications import FunNotifications
from fun_random.gui.feature.sub_systems.fun_progressions import FunProgressions
from fun_random.gui.feature.sub_systems.fun_sub_modes_holder import FunSubModesHolder
from fun_random.gui.feature.sub_systems.fun_subscription import FunSubscription
from fun_random.gui.feature.sub_systems.fun_sub_modes_info import FunSubModesInfo
from fun_random.gui.feature.util.fun_helpers import notifyCaller
from fun_random.gui.fun_gui_constants import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME, SELECTOR_BATTLE_TYPES
from fun_random.helpers.server_settings import FunRandomConfig
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import events
from gui.shared.utils.SelectorBattleTypesUtils import setBattleTypeAsUnknown
from helpers import dependency
from skeletons.gui.game_control import IFunRandomController
from skeletons.gui.lobby_context import ILobbyContext
from gui.impl.gen import R
if typing.TYPE_CHECKING:
    from helpers.server_settings import ServerSettings

class FunRandomController(IFunRandomController, IGlobalListener):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(FunRandomController, self).__init__()
        self.__serverSettings = None
        self.__funRandomSettings = None
        self.__subscription = FunSubscription()
        self.__subModesHolder = FunSubModesHolder(self.__subscription)
        self.__subModesInfo = FunSubModesInfo(self.__subModesHolder)
        self.__progressions = FunProgressions(self.__subscription)
        self.__hiddenVehicles = FunHiddenVehicles(self.__subModesHolder)
        self.__notifications = FunNotifications(self.__progressions, self.__subModesHolder)
        return

    def fini(self):
        for subSystemToFini in self.__getSubSystems():
            subSystemToFini.fini()

        super(FunRandomController, self).fini()

    def onAccountBecomePlayer(self):
        self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())
        self.__progressions.startProgressListening()

    def onAccountBecomeNonPlayer(self):
        self.__clearListening()

    def onAvatarBecomePlayer(self):
        if self.__serverSettings is None:
            self.__lobbyContext.onServerSettingsChanged += self.__onServerSettingsChanged
        self.__subModesHolder.setDesiredSubModeID(self.__subModesHolder.getBattleSubModeID())
        return

    def onDisconnected(self):
        self.__clearListening()
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onServerSettingsUpdate
        for subSystemToClear in self.__getSubSystems():
            subSystemToClear.clear()

        self.__serverSettings = self.__funRandomSettings = None
        return

    def onLobbyInited(self, event=None):
        self.__hiddenVehicles.startVehiclesListening()
        self.__notifications.startNotificationPushing()
        self.__subModesHolder.startNotification()
        self.startGlobalListening()

    def onLobbyStarted(self, ctx):
        self.setDesiredSubModeID(ctx.get(FUN_EVENT_ID_KEY, self.__subModesHolder.getDesiredSubModeID()))

    @property
    def notifications(self):
        return self.__notifications

    @property
    def progressions(self):
        return self.__progressions

    @property
    def subscription(self):
        return self.__subscription

    @property
    def subModesHolder(self):
        return self.__subModesHolder

    @property
    def subModesInfo(self):
        return self.__subModesInfo

    def isEnabled(self):
        return self.__funRandomSettings.isEnabled

    def isFunRandomPrbActive(self):
        return False if self.prbEntity is None else bool(self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.FUN_RANDOM)

    def getAssetsPointer(self):
        return self.__funRandomSettings.assetsPointer

    def getIconsResRoot(self):
        assetsPointer = self.__funRandomSettings.assetsPointer
        return R.images.fun_random.gui.maps.icons.feature.asset_packs.modes.dyn(assetsPointer, R.images.fun_random.gui.maps.icons.feature.asset_packs.modes.undefined)

    def getLocalsResRoot(self):
        assetsPointer = self.__funRandomSettings.assetsPointer
        return R.strings.fun_random.modes.dyn(assetsPointer, R.strings.fun_random.modes.undefined)

    def hasDailyQuestsEntry(self):
        desiredSubMode = self.subModesHolder.getDesiredSubMode()
        return self.isFunRandomPrbActive() and desiredSubMode and desiredSubMode.hasDailyQuestsEntry()

    def hasHangarHeaderEntry(self):
        desiredSubMode = self.subModesHolder.getDesiredSubMode()
        return self.isFunRandomPrbActive() and desiredSubMode and desiredSubMode.hasHangarHeaderEntry()

    def getSettings(self):
        return self.__funRandomSettings

    def setDesiredSubModeID(self, subModeID, trustedSource=False):
        self.__subscription.suspend()
        self.__subModesHolder.setDesiredSubModeID(subModeID, trustedSource)
        self.__hiddenVehicles.updateCurrentVehicle(self.__subModesHolder.getDesiredSubMode())
        self.__subscription.resume()

    @adisp_async
    @adisp_process
    def selectFunRandomBattle(self, desiredSubModeID, callback=None):
        extData = {FUN_EVENT_ID_KEY: desiredSubModeID}
        result = yield self.__doSelectPrbAction(PREBATTLE_ACTION_NAME.FUN_RANDOM, extData=extData)
        notifyCaller(callback, result)

    def __getSubSystems(self):
        return (self.__hiddenVehicles,
         self.__notifications,
         self.__progressions,
         self.__subscription,
         self.__subModesInfo,
         self.__subModesHolder)

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onServerSettingsUpdate
        self.__serverSettings = serverSettings
        self.__serverSettings.onServerSettingsChange += self.__onServerSettingsUpdate
        prevFunSettings = self.__funRandomSettings or FunRandomConfig()
        rawNewFunSettings = serverSettings.getSettings().get(Configs.FUN_RANDOM_CONFIG.value, {})
        self.__funRandomSettings = FunRandomConfig(**rawNewFunSettings)
        self.__updateFunRandomSettings(prevFunSettings, self.__funRandomSettings)
        return

    def __onServerSettingsUpdate(self, diff):
        if Configs.FUN_RANDOM_CONFIG.value in diff:
            prevFunSettings = self.__funRandomSettings or FunRandomConfig()
            self.__funRandomSettings = self.__funRandomSettings.replace(diff[Configs.FUN_RANDOM_CONFIG.value].copy())
            self.__updateFunRandomSettings(prevFunSettings, self.__funRandomSettings)

    def __clearListening(self):
        self.__progressions.stopProgressListening()
        self.__notifications.stopNotificationPushing()
        self.__hiddenVehicles.stopVehiclesListening()
        self.__subModesHolder.stopNotification()
        self.stopGlobalListening()

    @adisp_async
    @adisp_process
    def __doSelectPrbAction(self, prbActionName, accountsToInvite=None, extData=None, callback=None):
        if self.prbDispatcher is None:
            notifyCaller(callback, False)
        else:
            prbAction = PrbAction(prbActionName, accountsToInvite=accountsToInvite, extData=extData)
            result = yield self.prbDispatcher.doSelectAction(prbAction)
            notifyCaller(callback, result)
        return

    def __updateFunRandomSettings(self, prevSettings, newSettings):
        self.__subscription.suspend()
        self.__subModesHolder.updateSettings(prevSettings, newSettings)
        self.__progressions.updateSettings(newSettings.metaProgression)
        self.__notifications.updateSettings(newSettings)
        self.__notifications.startNotification()
        self.__subModesHolder.startNotification()
        self.__storeFunRandomPreset()
        self.__subscription.resume()

    def __storeFunRandomPreset(self):
        currPreset = self.__funRandomSettings.settingsKey
        lastPreset = AccountSettings.getSettings(FUN_RANDOM_LAST_PRESET)
        if currPreset != DEFAULT_SETTINGS_KEY and lastPreset != currPreset:
            AccountSettings.setSettings(FUN_RANDOM_LAST_PRESET, currPreset)
            setBattleTypeAsUnknown(SELECTOR_BATTLE_TYPES.FUN_RANDOM)
