# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/widgets/ny_main_widget.py
import typing
import Event
from CurrentVehicle import g_currentVehicle
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_main_widget_model import NewYearMainWidgetModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_economic_bonus_model import NyEconomicBonusModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_widget_friend_info_model import NyWidgetFriendInfoModel, UserStatus
from gui.impl.gen.view_models.views.lobby.new_year.ny_constants import TutorialStates
from gui.impl.lobby.new_year.tooltips.ny_friends_tooltip import NyFriendsTooltip
from gui.impl.lobby.new_year.tooltips.ny_main_widget_tooltip import NyMainWidgetTooltip
from gui.impl.lobby.new_year.tooltips.ny_widget_bonus_tooltip import NyWidgetBonusTooltip
from gui.impl.new_year.navigation import NewYearNavigation, ViewAliases
from gui.impl.new_year.new_year_helper import IS_ROMAN_NUMBERS_ALLOWED
from gui.impl.new_year.sound_rtpc_controller import SoundRTPCController
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from helpers import dependency, getLanguageCode, isMemoryRiskySystem
from messenger.proto.events import g_messengerEvents
from new_year import parseHangarNameMask
from new_year.ny_bonuses import isBonusApplicable, EconomicBonusHelper, getXpBonusNameByID, getXpBonusIDbyName, toPrettyCumulativeBonusValue
from new_year.ny_constants import CustomizationObjects, SyncDataKeys, AdditionalCameraObject
from new_year.ny_level_helper import NewYearAtmospherePresenter
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController, ICelebrityController, IFriendServiceController
from uilogging.ny.loggers import NyMainWidgetLogger
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.new_year.components.ny_widget_level_progress_model import NyWidgetLevelProgressModel
    from messenger.proto.xmpp.entities import XMPPUserEntity

class NyMainWidgetInject(InjectComponentAdaptor):

    def _makeInjectView(self):
        return NyMainWidget()


class WidgetLevelProgressHelper(object):
    __nyController = dependency.descriptor(INewYearController)
    __friendsService = dependency.descriptor(IFriendServiceController)

    def __init__(self, model):
        super(WidgetLevelProgressHelper, self).__init__()
        self.__model = model
        self.__level = None
        self.onLevelChanged = Event.Event()
        return

    def initialize(self):
        self.__subscribe()
        self.__initWidgetModel()
        self.__updateWidgetLevel()

    def update(self):
        self.__updateHangarName()
        self.__updateWidgetLevel()

    @property
    def viewModel(self):
        return self.__model

    def clear(self):
        self.__unsubscribe()
        self.__model = None
        self.onLevelChanged.clear()
        return

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.new_year.tooltips.NyMainWidgetTooltip():
            return NyMainWidgetTooltip()
        else:
            return NyFriendsTooltip(kind=event.getArgument('type'), payload=event.getArgument('payload')) if contentID == R.views.lobby.new_year.tooltips.NyFriendsTooltips() else None

    def __getEvents(self):
        return ((self.__nyController.onDataUpdated, self.__onDataUpdated),
         (self.viewModel.onAnimationEnd, self.__onAnimationEnd),
         (NewYearNavigation.onObjectStateChanged, self.__onObjectStateChanged),
         (self.__friendsService.onFriendHangarEnter, self.__onFriendHangarUpdate),
         (self.__friendsService.onFriendHangarExit, self.__onFriendHangarUpdate))

    def __initWidgetModel(self):
        maxLevel = NewYearAtmospherePresenter.getMaxLevel()
        self.__updateHangarName()
        with self.viewModel.transaction() as model:
            model.setMaxLevel(maxLevel)
            model.setIsRomanNumbersAllowed(IS_ROMAN_NUMBERS_ALLOWED)
            model.setUserLanguage(str(getLanguageCode()).upper())

    def __updateHangarName(self):
        titleId, descriptionId = parseHangarNameMask(self.__nyController.getHangarNameMask())
        with self.viewModel.transaction() as model:
            model.hangarName.setTitle(titleId)
            model.hangarName.setDescription(descriptionId)

    def __updateWidgetLevel(self):
        level = NewYearAtmospherePresenter.getLevel()
        currentPoints, maxPoints = NewYearAtmospherePresenter.getLevelProgress()
        isLevelChanged = level != self.__level
        if isLevelChanged:
            self.__level = level
            self.onLevelChanged()
        with self.viewModel.transaction() as model:
            if isLevelChanged:
                model.setLevel(level)
                model.setMaxPoints(maxPoints)
            model.setCurrentPoints(currentPoints)

    def __onFriendHangarUpdate(self, *_):
        self.__reset()

    def __reset(self):
        self.__initWidgetModel()
        self.__updateWidgetLevel()

    def __subscribe(self):
        for event, handler in self.__getEvents():
            event += handler

    def __unsubscribe(self):
        for event, handler in reversed(self.__getEvents()):
            event -= handler

    def __onDataUpdated(self, keys, _):
        if SyncDataKeys.POINTS in keys:
            self.__updateWidgetLevel()
        if SyncDataKeys.HANGAR_NAME_MASK in keys:
            self.__updateHangarName()

    def __onAnimationEnd(self):
        self.__nyController.setWidgetLevelUpAnimationEnd()

    def __onObjectStateChanged(self):
        self.__updateHangarName()
        self.__updateWidgetLevel()


class WidgetFriendStatusHelper(object):
    __friendsService = dependency.descriptor(IFriendServiceController)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, model):
        super(WidgetFriendStatusHelper, self).__init__()
        self.__model = model

    def initialize(self):
        self.__subscribe()
        self.__updateWidgetModel()

    @property
    def viewModel(self):
        return self.__model

    def clear(self):
        self.__unsubscribe()
        self.__model = None
        return

    def __getEvents(self):
        return ((self.__friendsService.onFriendHangarEnter, self.__onFriendHangarUpdate), (self.__friendsService.onFriendHangarExit, self.__onFriendHangarUpdate), (g_messengerEvents.users.onUserStatusUpdated, self.__updateFriendOnlineStatus))

    def __updateWidgetModel(self):
        isInService = self.__friendsService.friendHangarSpaId is not None
        with self.viewModel.transaction() as model:
            model.setIsShow(isInService)
            if isInService:
                spaId = self.__friendsService.friendHangarSpaId
                status = UserStatus.ONLINE if self.__friendsService.isFriendOnline(spaId) else UserStatus.OFFLINE
                model.setId(spaId)
                model.setNickname(self.__friendsService.getFriendName(spaId) or '')
                model.setServerName(self.__lobbyContext.getRegionCode(spaId) or '')
                model.setUserStatus(status)
        return

    def __onFriendHangarUpdate(self, *_):
        self.__updateWidgetModel()

    def __subscribe(self):
        for event, handler in self.__getEvents():
            event += handler

    def __unsubscribe(self):
        for event, handler in reversed(self.__getEvents()):
            event -= handler

    def __updateFriendOnlineStatus(self, user):
        with self.viewModel.transaction() as model:
            if model.getId() == user.getID():
                model.setUserStatus(UserStatus.ONLINE if user.isOnline() else UserStatus.OFFLINE)


class NyMainWidget(ViewImpl):
    __nyController = dependency.descriptor(INewYearController)
    __celebrityController = dependency.descriptor(ICelebrityController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __guiLoader = dependency.descriptor(IGuiLoader)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __uiLogger = NyMainWidgetLogger()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.new_year.widgets.WidgetAtmosphere())
        settings.flags = ViewFlags.COMPONENT
        settings.model = NewYearMainWidgetModel()
        super(NyMainWidget, self).__init__(settings)
        self.__soundRTPCController = None
        self.__widgetHelper = None
        return

    @property
    def viewModel(self):
        return super(NyMainWidget, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.new_year.tooltips.NyWidgetBonusTooltip():
            return NyWidgetBonusTooltip()
        if self.__widgetHelper:
            content = self.__widgetHelper.createToolTipContent(event, contentID)
            if content:
                return content
        return super(NyMainWidget, self).createToolTipContent(event, contentID)

    @property
    def isLobbyMode(self):
        return NewYearNavigation.getCurrentObject() is None

    def _subscribe(self):
        currentObject = NewYearNavigation.getCurrentObject()
        self.__soundRTPCController = SoundRTPCController()
        self.__soundRTPCController.init(currentObject)
        self.__soundRTPCController.setLevelAtmosphere(NewYearAtmospherePresenter.getLevel())
        self.__widgetHelper = WidgetLevelProgressHelper(self.viewModel.widgetLevelProgress)
        self.__widgetHelper.onLevelChanged += self.__onLevelChanged
        super(NyMainWidget, self)._subscribe()

    def _getEvents(self):
        return ((self.__nyController.onDataUpdated, self.__onDataUpdated),
         (self.__celebrityController.onCelebCompletedTokensUpdated, self.__onCelebCompletedTokensUpdated),
         (self.viewModel.onGoToGladeView, self.__onGoToGladeView),
         (self.viewModel.onGoToChallenge, self.__onGoToChallenge),
         (self.viewModel.onChangeBonus, self.__onChangeBonus),
         (NewYearNavigation.onSwitchView, self.__onSwitchView),
         (NewYearNavigation.onObjectStateChanged, self.__onObjectStateChanged),
         (g_currentVehicle.onChanged, self.__onCurrentVehicleChanged))

    def _finalize(self):
        if self.__soundRTPCController is not None:
            self.__soundRTPCController.fini()
            self.__soundRTPCController = None
        self.__widgetHelper.onLevelChanged -= self.__onLevelChanged
        self.__widgetHelper.clear()
        self.__widgetHelper = None
        super(NyMainWidget, self)._finalize()
        return

    def _onLoaded(self, *args, **kwargs):
        super(NyMainWidget, self)._onLoaded(*args, **kwargs)
        with self.viewModel.transaction() as model:
            self.__updateData(model)
            self.__updateActiveState(model)
            self.__updateSelectedBonus(model)
            self.__updateBonusError(model=model)
            self.__updateEconomicBonus(model)
        self.__widgetHelper.initialize()
        self.viewModel.setIsExtendedAnim(not isMemoryRiskySystem())
        self.viewModel.setIsInited(True)

    def __onGoToGladeView(self, *_):
        self.__uiLogger.logClick(self.isLobbyMode)
        if not self.__tryToShowTutotial():
            from ClientSelectableCameraObject import ClientSelectableCameraObject
            ClientSelectableCameraObject.deselectAll()
            NewYearNavigation.switchTo(CustomizationObjects.FIR, True, withFade=True)

    def __onGoToChallenge(self):
        self.__uiLogger.logClick(self.isLobbyMode)
        if not self.__tryToShowTutotial():
            NewYearNavigation.switchTo(AdditionalCameraObject.CELEBRITY, viewAlias=ViewAliases.CELEBRITY_VIEW)

    def __tryToShowTutotial(self):
        if self.__settingsCore.serverSettings.getNewYearStorage().get(NewYearStorageKeys.TUTORIAL_STATE, TutorialStates.INTRO) < TutorialStates.FINISHED:
            NewYearNavigation.switchTo(AdditionalCameraObject.UNDER_SPACE, True, withFade=True)
            return True
        return False

    def __onDataUpdated(self, keys, _):
        if SyncDataKeys.XP_BONUS_CHOICE in keys:
            with self.viewModel.transaction() as model:
                self.__updateSelectedBonus(model)

    def __onCurrentVehicleChanged(self):
        self.__updateBonusError()

    @replaceNoneKwargsModel
    def __updateBonusError(self, model=None):
        bonusError = isBonusApplicable(g_currentVehicle.item, NewYearAtmospherePresenter.getLevel())
        model.setBonusError(bonusError)

    def __updateSelectedBonus(self, model):
        selectedBonusID = self.__itemsCache.items.festivity.getChosenXPBonus()
        model.setSelectedBonus(getXpBonusNameByID(selectedBonusID))

    def __onCelebCompletedTokensUpdated(self):
        with self.viewModel.transaction() as model:
            self.__updateEconomicBonus(model)

    def __updateEconomicBonus(self, model):
        bonuses = EconomicBonusHelper.getBonusesDataInventory()
        economicBonuses = model.getEconomicBonuses()
        economicBonuses.clear()
        for bonusID, value in bonuses.iteritems():
            bonus = NyEconomicBonusModel()
            bonus.setBonusName(bonusID)
            bonus.setBonusValue(toPrettyCumulativeBonusValue(value))
            economicBonuses.addViewModel(bonus)

        economicBonuses.invalidate()

    def __onLevelChanged(self):
        self.__soundRTPCController.setLevelAtmosphere(NewYearAtmospherePresenter.getReachedLevel())
        self.__tryToDestroyWidgetTooltip()
        self.__updateBonusError()

    def __updateData(self, model):
        model.setIsLobbyMode(self.isLobbyMode)
        model.setIsEnabled(NewYearNavigation.getCurrentObject() != CustomizationObjects.FIR)

    def __onChangeBonus(self, args):
        bonusType = str(args['bonusType'])
        selectedBonusID = getXpBonusIDbyName(bonusType)
        if selectedBonusID is not None:
            self.__nyController.chooseXPBonus(selectedBonusID)
        return

    @staticmethod
    def __updateActiveState(model):
        currentView = NewYearNavigation.getCurrentViewName()
        model.setIsVisible(currentView != ViewAliases.INFO_VIEW)
        model.setIsEnabled(currentView != ViewAliases.GLADE_VIEW or NewYearNavigation.getCurrentObject() != CustomizationObjects.FIR)

    def __onObjectStateChanged(self):
        currentObject = NewYearNavigation.getCurrentObject()
        with self.viewModel.transaction() as model:
            self.__updateData(model)
            self.__updateActiveState(model)
        self.__soundRTPCController.setCurrentLocation(currentObject)

    def __onSwitchView(self, _):
        with self.viewModel.transaction() as tx:
            self.__updateActiveState(tx)
        if not self.viewModel.getIsVisible():
            self.__tryToDestroyWidgetTooltip()

    def __tryToDestroyWidgetTooltip(self):
        tooltipIDs = (R.views.lobby.new_year.tooltips.NyMainWidgetTooltip(), R.views.lobby.new_year.tooltips.NyWidgetBonusTooltip())
        for tooltipID in tooltipIDs:
            tooltipView = self.__guiLoader.windowsManager.getViewByLayoutID(tooltipID)
            if tooltipView:
                tooltipView.destroyWindow()
