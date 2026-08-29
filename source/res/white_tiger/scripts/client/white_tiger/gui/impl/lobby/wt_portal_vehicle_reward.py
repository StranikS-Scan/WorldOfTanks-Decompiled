# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/wt_portal_vehicle_reward.py
import Windowing
from cgf_components import sound_helpers
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.Scaleform.Waiting import Waiting
from gui.impl.gen import R
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from gui.server_events.bonuses import CustomizationsBonus
from white_tiger.gui.impl.gen.view_models.views.lobby.portal_rewards.wt_portal_vehicle_reward_model import WtPortalVehicleRewardModel
from white_tiger.gui.impl.lobby.wt_event_sound import playLootBoxPortalExit
from white_tiger.gui.impl.lobby.wt_event_base_portal_awards_view import WtEventBasePortalAwards
from white_tiger.gui.wt_event_models_helper import fillAdditionalAwards
from white_tiger.gui.impl.lobby.wt_event_constants import WhiteTigerLootBoxes

class WtPortalVehicleReward(WtEventBasePortalAwards):

    def __init__(self, boxType, boxCount, awardVehicleData, awards=None, numberOfVideos=1):
        self.__mainRewards = awardVehicleData
        awardsWithoutVehicle, self.__awardVehicles = self.__filterAwards(awards, awardVehicleData[-1][0].intCD)
        settings = ViewSettings(layoutID=R.views.white_tiger.lobby.WtPortalVehicleRewardView(), model=WtPortalVehicleRewardModel())
        super(WtPortalVehicleReward, self).__init__(settings, awardsWithoutVehicle)
        self.__boxCount = boxCount
        self.__boxType = boxType
        self.__vehicleData = None
        self.__numberOfVideos = numberOfVideos
        self.__isLoopPlaying = False
        return

    @property
    def viewModel(self):
        return super(WtPortalVehicleReward, self).getViewModel()

    def _playVideoStart(self):
        _, customData = self.__vehicleData
        event = customData.get('sound_video_start', '')
        sound_helpers.play2d(event)

    def _playVideoStop(self):
        event = 'ev_white_tiger_portal_video_stop'
        sound_helpers.play2d(event)

    def _playLoopStart(self):
        self.__isLoopPlaying = True
        _, customData = self.__vehicleData
        event = customData.get('sound_video_loop_start', '')
        sound_helpers.play2d(event)

    def _playLoopStop(self):
        self.__isLoopPlaying = False
        event = 'ev_white_tiger_portal_reward_loop_stop'
        sound_helpers.play2d(event)

    def _playPause(self):
        event = 'ev_white_tiger_portal_video_pause'
        sound_helpers.play2d(event)

    def _playResume(self):
        event = 'ev_white_tiger_portal_video_resume'
        sound_helpers.play2d(event)

    def _onLoading(self, *args, **kwargs):
        super(WtPortalVehicleReward, self)._onLoading(*args, **kwargs)
        self.viewModel.setIsWindowAccessible(Windowing.isWindowAccessible())
        Windowing.addWindowAccessibilitynHandler(self._onWindowAccessibilityChanged)

    def _onLoaded(self, *args, **kwargs):
        super(WtPortalVehicleReward, self)._onLoaded(*args, **kwargs)
        Waiting.hide('updating')

    def _finalize(self):
        playLootBoxPortalExit()
        self._playLoopStop()
        self.__mainRewards = None
        self.__awardVehicles = []
        self.__vehicleData = None
        Windowing.removeWindowAccessibilityHandler(self._onWindowAccessibilityChanged)
        super(WtPortalVehicleReward, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onIntroVideoPlay, self._onIntroVideoPlay), (self.viewModel.onVehicleVideoComplete, self._onVehicleVideoComplete), (self.viewModel.onVideoInterrupt, self._onVideoInterrupt))

    def _onWindowAccessibilityChanged(self, isWindowAccessible):
        if isWindowAccessible:
            self._playLoopStart()
            self._playResume()
        else:
            self._playPause()
        self.viewModel.setIsWindowAccessible(isWindowAccessible)

    def _onIntroVideoPlay(self):
        self._playVideoStart()

    def _onVehicleVideoComplete(self):
        if self.__numberOfVideos > 0:
            self._playLoopStop()
            self._updateModel()
        else:
            if self.__isLoopPlaying:
                return
            self._playLoopStart()

    def _onVideoInterrupt(self):
        if not self.__isLoopPlaying:
            self._playLoopStart()

    def _onClose(self, args=None):
        if self.__boxType == WhiteTigerLootBoxes.WT_TANK:
            self._goToPortals()
            return
        g_eventBus.handleEvent(events.WtEventPortalsEvent(events.WtEventPortalsEvent.ON_BACK_TO_PORTAL, ctx={'runCounter': self.__boxCount}), scope=EVENT_BUS_SCOPE.LOBBY)
        super(WtPortalVehicleReward, self)._onClose()

    def _updateModel(self):
        super(WtPortalVehicleReward, self)._updateModel()
        with self.viewModel.transaction() as model:
            extra = self._boxesCtrl.getExtraRewards(self._getBoxType(), count=0)
            setFirstLaunch = False
            setFirstLaunchReward = False
            if self._getBoxType() != WhiteTigerLootBoxes.WT_TANK:
                setFirstLaunch = not self._boxesCtrl.isEngineerReroll()
                setFirstLaunchReward = extra.get('gold', 0) if extra else 0
            model.setIsFirstLaunch(setFirstLaunch)
            model.setFirstLaunchReward(setFirstLaunchReward)
            self.__vehicleData = self.__mainRewards[0]
            self.__mainRewards.pop(0)
            if self.__vehicleData:
                _, customData = self.__vehicleData
                if customData:
                    model.setRemainingVideoNumber(self.__numberOfVideos)
                    model.setIntroVideoName(customData.get('video_show', ''))
                    model.setVehicleVideoName(customData.get('video_idle', ''))
            self.__numberOfVideos -= 1
            isLastVideo = self.__numberOfVideos == 0
            filteredAwards = []
            for bonus in self._awards:
                if isinstance(bonus, CustomizationsBonus):
                    item = bonus.getCustomizations()[0]
                    style = bonus.getC11nItem(item)
                    if style.isHiddenInUI():
                        continue
                filteredAwards.append(bonus)

            if isLastVideo:
                self._tooltipItems.clear()
                tooltipItems = self._tooltipItems
                awardList = self.__awardVehicles
                awardList += filteredAwards
                fillAdditionalAwards(model.getRewards(), awardList, tooltipItems)
            model.setIsLastVideo(isLastVideo)

    def _getBoxType(self):
        return self.__boxType

    def _goToPortals(self):
        playLootBoxPortalExit()
        g_eventBus.handleEvent(events.WtEventPortalsEvent(events.WtEventPortalsEvent.ON_PORTAL_AWARD_VIEW_CLOSED), scope=EVENT_BUS_SCOPE.LOBBY)
        self.destroyWindow()

    def __filterAwards(self, awards, ignoredAwardID):
        awardsWithoutMainVehicle = []
        vehicleAwards = []
        for award in awards:
            isIgnore = False
            if award.getName() == 'vehicles':
                for vehicle, _ in award.getVehicles():
                    if vehicle.intCD == ignoredAwardID:
                        vehicleAwards.append(award)
                        isIgnore = True

            if not isIgnore:
                awardsWithoutMainVehicle.append(award)

        return (awardsWithoutMainVehicle, vehicleAwards)


class WtPortalVehicleRewardWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, boxType, boxCount, vehiclesReward, awards=None, parent=None, numberOfVideos=1):
        super(WtPortalVehicleRewardWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WtPortalVehicleReward(boxType=boxType, boxCount=boxCount, awardVehicleData=vehiclesReward, awards=awards, numberOfVideos=numberOfVideos), parent=parent, layer=WindowLayer.OVERLAY)
