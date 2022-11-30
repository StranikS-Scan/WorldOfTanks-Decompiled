# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/challenge/ny_challenge.py
import logging
from collections import namedtuple
import typing
from gui.impl.lobby.new_year.challenge.ny_challenge_guest import NewYearChallengeGuest
from gui.impl.lobby.new_year.challenge.ny_challenge_headquarters import NewYearChallengeHeadquarters
from gui.impl.lobby.new_year.challenge.ny_challenge_tournament_completed import NewYearChallengeTournamentCompleted
from gui.impl.lobby.new_year.challenge.ny_challenge_tournament import NewYearChallengeTournament
from gui.impl.lobby.new_year.challenge.ny_challenge_guest_d_customization import NyChallengeGuestDCustomization
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_model import NewYearChallengeModel, ChallengeViewStates
from gui.impl.lobby.new_year.ny_selectable_logic_presenter import SelectableLogicPresenter
from gui.impl.lobby.new_year.scene_rotatable_view import SceneRotatableView
from gui.impl.new_year.navigation import NewYearNavigation, ViewAliases
from gui.impl.new_year.new_year_helper import nyCreateToolTipContentDecorator
from helpers import dependency, uniprof
from new_year.ny_constants import NyWidgetTopMenu, NyTabBarChallengeView as TabBarNames, CHALLENGE_TAB_TO_CAMERA_OBJ, CHALLENGE_CAMERA_OBJ_TO_TAB
from skeletons.new_year import ICelebritySceneController
if typing.TYPE_CHECKING:
    from typing import Dict, Optional
    from gui.shared.event_dispatcher import NYTabCtx
    from gui.impl.lobby.new_year.ny_history_presenter import NyHistoryPresenter
_logger = logging.getLogger(__name__)
_SubViewInfo = namedtuple('_SubViewInfo', ('viewCls', 'uiID'))
_VIEW_INFO_BY_ID = {TabBarNames.TOURNAMENT: _SubViewInfo(NewYearChallengeTournament, ChallengeViewStates.TOURNAMENT),
 TabBarNames.TOURNAMENT_COMPLETED: _SubViewInfo(NewYearChallengeTournamentCompleted, ChallengeViewStates.COMPLETED),
 TabBarNames.GUEST_A: _SubViewInfo(NewYearChallengeGuest, ChallengeViewStates.GUESTA),
 TabBarNames.GUEST_M: _SubViewInfo(NewYearChallengeGuest, ChallengeViewStates.GUESTM),
 TabBarNames.GUEST_CAT: _SubViewInfo(NewYearChallengeGuest, ChallengeViewStates.GUESTC),
 TabBarNames.HEADQUARTERS: _SubViewInfo(NewYearChallengeHeadquarters, ChallengeViewStates.HEADQUARTERS),
 TabBarNames.GUEST_D: _SubViewInfo(NyChallengeGuestDCustomization, ChallengeViewStates.GUESTD)}

class NewYearChallenge(SceneRotatableView, SelectableLogicPresenter):
    __slots__ = ('__subViews', '__currentSubViewID', '__isSwitchingAble')
    __celebrityController = dependency.descriptor(ICelebritySceneController)
    _navigationAlias = ViewAliases.CELEBRITY_VIEW

    def __init__(self, viewModel, parentView, *args, **kwargs):
        super(NewYearChallenge, self).__init__(viewModel, parentView, *args, **kwargs)
        self.__subViews = {}
        self.__currentSubViewID = None
        self.__isSwitchingAble = True
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def createPopOverContent(self, event):
        view = self.__getCurrentSubView()
        return view.createPopOverContent(event) if view else super(NewYearChallenge, self).createPopOverContent(event)

    @nyCreateToolTipContentDecorator
    def createToolTipContent(self, event, contentID):
        view = self.__getCurrentSubView()
        return view.createToolTipContent(event, contentID) if view else super(NewYearChallenge, self).createToolTipContent(event, contentID)

    def createToolTip(self, event):
        view = self.__getCurrentSubView()
        return view.createToolTip(event) if view else super(NewYearChallenge, self).createToolTip(event)

    @uniprof.regionDecorator(label='ny_challenge', scope='enter')
    def initialize(self, *args, **kwargs):
        super(NewYearChallenge, self).initialize(*args, **kwargs)
        if self.__currentSubViewID is None:
            selectedTabName = kwargs.get('tabName') or TabBarNames.TOURNAMENT
            self.__switchSubView(selectedTabName)
        else:
            view = self.__getCurrentSubView()
            self.__initializeSubView(view, self.__currentSubViewID)
        return

    @uniprof.regionDecorator(label='ny_challenge', scope='exit')
    def finalize(self):
        super(NewYearChallenge, self).finalize()
        view = self.__getCurrentSubView()
        if view:
            view.finalize()
        self.__currentSubViewID = None
        return

    def clear(self):
        for view in self.__subViews.itervalues():
            view.clear()

        self.__subViews.clear()
        self.__subViews = None
        super(NewYearChallenge, self).clear()
        return

    def _getCallbacks(self):
        return tuple()

    def _getEvents(self):
        events = super(NewYearChallenge, self)._getEvents()
        return events + ((NewYearNavigation.onSidebarSelected, self.__onSideBarSelected), (NewYearNavigation.onUpdateCurrentView, self.__onUpdate), (self.__celebrityController.onQuestsUpdated, self.__onQuestsUpdated))

    def __onSideBarSelected(self, ctx):
        if ctx.menuName != NyWidgetTopMenu.CHALLENGE:
            return
        self.__switchSubView(ctx.tabName, switchCameraObject=True)

    def __switchSubView(self, tabName, switchCameraObject=False):
        if not self.__isSwitchingAble:
            return
        else:
            self.__isSwitchingAble = False
            if tabName == TabBarNames.TOURNAMENT and self.__celebrityController.isChallengeCompleted:
                tabName = TabBarNames.TOURNAMENT_COMPLETED
            if self.__currentSubViewID == tabName:
                return
            newView = self.__getSubView(tabName)
            if newView is None:
                return
            if switchCameraObject:
                camObj = CHALLENGE_TAB_TO_CAMERA_OBJ.get(tabName)
                NewYearNavigation.switchTo(camObj, instantly=False, withFade=False)
            view = self.__getCurrentSubView()
            if view:
                view.finalize()
            self.__initializeSubView(newView, tabName)
            self.__currentSubViewID = tabName
            viewInfo = _VIEW_INFO_BY_ID.get(tabName)
            self.viewModel.setViewState(viewInfo.uiID)
            self.__isSwitchingAble = True
            return

    def __onUpdate(self, *_, **__):
        if self.getNavigationAlias() != NewYearNavigation.getCurrentViewName():
            return
        else:
            newObject = NewYearNavigation.getCurrentObject()
            tabName = CHALLENGE_CAMERA_OBJ_TO_TAB.get(newObject)
            if tabName is None or self.__currentSubViewID == tabName:
                return
            self.__switchSubView(tabName)
            NewYearNavigation.selectSidebarTabOutside(menuName=NyWidgetTopMenu.CHALLENGE, tabName=tabName)
            return

    def __getCurrentSubView(self):
        return self.__subViews.get(self.__currentSubViewID) if self.__currentSubViewID in self.__subViews else None

    def __getSubView(self, tabName):
        return self.__subViews.get(tabName) if tabName in self.__subViews else self.__createSubView(tabName)

    def __createSubView(self, tabName):
        viewInfo = _VIEW_INFO_BY_ID.get(tabName)
        if viewInfo:
            view = viewInfo.viewCls(self.viewModel, self.parentView)
            self.__subViews[tabName] = view
            return view
        else:
            return None

    def __initializeSubView(self, subView, tabName):
        subView.initialize(ctx={'tabName': tabName})

    def __onQuestsUpdated(self):
        if self.__currentSubViewID == TabBarNames.TOURNAMENT and self.__celebrityController.isChallengeCompleted:
            self.__switchSubView(TabBarNames.TOURNAMENT_COMPLETED, switchCameraObject=False)
