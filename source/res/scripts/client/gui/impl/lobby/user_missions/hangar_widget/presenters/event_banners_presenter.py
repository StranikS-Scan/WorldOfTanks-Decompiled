# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hangar_widget/presenters/event_banners_presenter.py
import json
from typing import TYPE_CHECKING
import BigWorld
from debug_utils import LOG_ERROR
from gui.impl.gen.view_models.views.lobby.user_missions.widget.event_banner_model import EventBannerModel
from gui.impl.gen.view_models.views.lobby.user_missions.widget.event_banners_list_model import EventBannersListModel
from gui.impl.lobby.user_missions.hangar_widget.event_banners.event_banners_container import EventBannersContainer
from gui.impl.lobby.user_missions.hangar_widget.overlap_ctrl import OverlapCtrlMixin
from gui.impl.lobby.user_missions.hangar_widget.services import IEventsService, ICampaignService
from gui.impl.lobby.user_missions.hangar_widget.tooltip_positioner import TooltipPositionerMixin
from gui.impl.pub.view_component import ViewComponent
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
if TYPE_CHECKING:
    from gui.impl.lobby.user_missions.hangar_widget.event_banners.base_event_banner import BaseEventBanner
_MAX_BANNERS = 5
_SPACE_CREATED_UPDATE_DELAY = 0.7

class EventBannersPresenter(TooltipPositionerMixin, OverlapCtrlMixin, ViewComponent[EventBannersListModel]):
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __eventsService = dependency.descriptor(IEventsService)
    __campaignService = dependency.descriptor(ICampaignService)

    def __init__(self):
        self.__bannersContainer = EventBannersContainer()
        self.__pendingToAppear = set()
        self.__readyForAnimations = self.__hangarSpace.spaceInited
        super(EventBannersPresenter, self).__init__(model=EventBannersListModel)

    @property
    def viewModel(self):
        return super(EventBannersPresenter, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        banner = self.__bannersContainer.getEventBanner(event.getArgument('key'))
        if banner is not None:
            view = banner.createToolTipContent(event)
            if view is not None:
                return view
        return super(EventBannersPresenter, self).createToolTipContent(event=event, contentID=contentID)

    def _getEvents(self):
        return super(EventBannersPresenter, self)._getEvents() + ((self.viewModel.onEventClick, self._onEventClicked),
         (self.viewModel.onAppearAnimationPlayed, self._onAppearAnimationPlayed),
         (self.__bannersContainer.onBannerUpdate, self._onBannerUpdate),
         (self.__eventsService.onEventsListChanged, self._onEventsUpdated),
         (self.__campaignService.onEventsListChanged, self._onEventsUpdated),
         (self.__hangarSpace.onSpaceCreate, self._onSpaceCreate))

    def _onLoading(self, *args, **kwargs):
        self.initOverlapCtrl()
        super(EventBannersPresenter, self)._onLoading(*args, **kwargs)
        self.queueUpdate()

    def _finalize(self):
        self._allBannersOnDisappear()
        super(EventBannersPresenter, self)._finalize()
        self.__bannersContainer = None
        return

    def _onEventsUpdated(self):
        self.queueUpdate()

    def _onEventClicked(self, args):
        banner = self.__bannersContainer.getEventBanner(args.get('key'))
        if banner:
            banner.onClick()

    def _onAppearAnimationPlayed(self, args):
        banners = json.loads(args.get('banners', ''))
        for bannerName in banners:
            banner = self.__bannersContainer.getEventBanner(bannerName)
            if not banner:
                continue
            banner.onAppearAnimationPlayed()

    def _onSpaceCreate(self):
        BigWorld.callback(_SPACE_CREATED_UPDATE_DELAY, self._delayedUpdateAfterSpaceCreated)

    def _delayedUpdateAfterSpaceCreated(self):
        self.__readyForAnimations = True
        if self.__pendingToAppear:
            self.queueUpdate()

    def _rawUpdate(self):
        super(EventBannersPresenter, self)._rawUpdate()
        eventEntries = self.__eventsService.getEntries() + self.__campaignService.getEntries()
        with self.viewModel.transaction() as vm:
            eps = vm.getBanners()
            epNames0 = {ep.getName() for ep in eps}
            eps.clear()
            eps.reserve(len(eventEntries))
            for entry in eventEntries:
                banner = self.__bannersContainer.getEventBanner(entry.id)
                if banner is None:
                    LOG_ERROR('Did not find banner by ID "{}"'.format(entry.id))
                    continue
                eps.addViewModel(self._fillBannerModel(banner))
                banner.onAppear()
                if len(eps) >= _MAX_BANNERS:
                    break

            eps.invalidate()
            epNames1 = {ep.getName() for ep in eps}
            removedEPs = epNames0 - epNames1
            for ep in removedEPs:
                banner = self.__bannersContainer.getEventBanner(ep)
                if banner is not None:
                    banner.onDisappear()

        return

    def _fillBannerModel(self, banner):
        banner.prepare()
        model = EventBannerModel()
        model.setName(banner.NAME)
        model.setIsMode(banner.isMode)
        model.setIntroDescription(banner.introDescription)
        model.setInProgressDescription(banner.inProgressDescription)
        model.setBannerState(banner.bannerState)
        model.setBorderColor(banner.borderColor)
        model.setTimerValue(banner.timerValue)
        model.setEventEndDate(banner.eventEndDate)
        model.setEventStartDate(banner.eventStartDate)
        model.setShowTimerBeforeEventEnd(banner.showTimerBeforeEventEnd)
        if self.__readyForAnimations:
            playAppearAnim = self._pickPendingAnimationIfExist(banner.NAME) or banner.playAppearAnim
            model.setAppearAnimationState(EventBannerModel.APPEAR_READY_TO_PLAY if playAppearAnim else EventBannerModel.APPEAR_NONE)
        elif banner.playAppearAnim:
            self.__pendingToAppear.add(banner.NAME)
            model.setAppearAnimationState(EventBannerModel.APPEAR_PENDING)
        else:
            model.setAppearAnimationState(EventBannerModel.APPEAR_NONE)
        return model

    def _pickPendingAnimationIfExist(self, bannerName):
        if bannerName in self.__pendingToAppear:
            self.__pendingToAppear.remove(bannerName)
            return True
        return False

    def _allBannersOnDisappear(self):
        banners = self.viewModel.getBanners()
        for bp in banners:
            banner = self.__bannersContainer.getEventBanner(str(bp.getName()))
            if banner is not None:
                banner.onDisappear()

        return

    def _onBannerUpdate(self, banner):
        if self.hasDeferModelUpdate:
            self.deferUpdate(self._updateBanner, banner)
        else:
            self._updateBanner(banner)

    def _updateBanner(self, banner):
        with self.viewModel.transaction() as vm:
            banners = vm.getBanners()
            for i, ep in enumerate(banners):
                if ep.getName() == banner.NAME:
                    banners.setViewModel(i, self._fillBannerModel(banner))
                    banners.invalidate()
                    break
