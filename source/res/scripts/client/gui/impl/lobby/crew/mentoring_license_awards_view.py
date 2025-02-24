# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/mentoring_license_awards_view.py
import SoundGroups
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from account_helpers.settings_core.settings_constants import GuiSettingsBehavior
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.common.awards_view_model import AwardsViewModel
from gui.impl.gen.view_models.views.lobby.common.reward_item_model import RewardItemModel
from gui.impl.lobby.crew.base_crew_view import BaseCrewSubView
from gui.impl.lobby.crew.crew_sounds import SOUNDS
from gui.impl.lobby.crew.tooltips.mentoring_license_tooltip import MentoringLicenseTooltip
from gui.impl.pub import WindowImpl
from gui.shared.account_settings_helper import AccountSettingsHelper
from gui.shared.event_dispatcher import showQuickTraining
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from skeletons.gui.shared import IItemsCache
from skeletons.gui.system_messages import ISystemMessages

class MentoringLicenseAwardsView(BaseCrewSubView):
    itemsCache = dependency.descriptor(IItemsCache)
    __systemMessages = dependency.descriptor(ISystemMessages)
    __slots__ = ('numItems',)

    def __init__(self, layoutID=R.views.lobby.common.AwardsView(), *args, **kwargs):
        settings = ViewSettings(layoutID, flags=ViewFlags.VIEW, model=AwardsViewModel(), args=args, kwargs=kwargs)
        self.numItems = kwargs.get('numItems', 9)
        super(MentoringLicenseAwardsView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(MentoringLicenseAwardsView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(MentoringLicenseAwardsView, self)._onLoading(*args, **kwargs)
        locales = R.strings.mentoring_license.MentoringLicenseAwards
        with self.viewModel.transaction() as tx:
            tx.setBackground(R.images.gui.maps.icons.windows.background())
            tx.setTitle(locales.title())
            tx.setUnderTitle(locales.underTitle())
            if self._primaryButtonVisible:
                tx.setRedirectButtonTitle(locales.button.primary())
            tx.setDefaultButtonTitle(locales.button.secondary())
            mainRewards = tx.mainRewards
            reward = RewardItemModel()
            reward.setName('goodies')
            reward.setType('goodies')
            reward.setIcon('mentoring_license')
            reward.setValue(str(self.numItems))
            reward.setLabel(backport.text(locales.title()))
            reward.setTooltipContentId(str(R.views.lobby.crew.tooltips.MentoringLicenseTooltip()))
            reward.setOverlayType('')
            mainRewards.addViewModel(reward)

    def _onLoaded(self, *args, **kwargs):
        super(MentoringLicenseAwardsView, self)._onLoaded(*args, **kwargs)
        SoundGroups.g_instance.playSound2D(SOUNDS.MENTORING_LICENSE_AWARD)

    def _getEvents(self):
        return ((self.viewModel.onClose, self._onClose), (self.viewModel.onRedirect, self._onRedirect), (g_playerEvents.onDisconnected, self.__onDisconnected))

    def _onClose(self, *_):
        AccountSettingsHelper.welcomeScreenShown(GuiSettingsBehavior.CREW_MENTORING_LICENSE_AWARDS_SHOWN)
        self.__pushSystemMessage()
        self.destroyWindow()

    def _onRedirect(self, *_):
        AccountSettingsHelper.welcomeScreenShown(GuiSettingsBehavior.CREW_MENTORING_LICENSE_AWARDS_SHOWN)
        showQuickTraining(vehicleInvID=g_currentVehicle.invID)
        self.__pushSystemMessage(priority=NotificationPriorityLevel.LOW)
        self.destroyWindow()

    def createToolTipContent(self, event, contentID):
        return MentoringLicenseTooltip(self.numItems) if contentID == R.views.lobby.crew.tooltips.MentoringLicenseTooltip() else super(MentoringLicenseAwardsView, self).createToolTipContent(event=event, contentID=contentID)

    @property
    def _primaryButtonVisible(self):
        currVehicle = g_currentVehicle.item
        if currVehicle is None:
            return False
        elif not currVehicle.hasCrew:
            return False
        else:
            return False if currVehicle.isInBattle else True

    def __onDisconnected(self):
        self.destroyWindow()

    def __pushSystemMessage(self, priority=None):
        msgType = SCH_CLIENT_MSG_TYPE.MENTORING_LICENSE
        self.__systemMessages.proto.serviceChannel.pushClientMessage(message={'priority': priority}, msgType=msgType)


class MentoringLicenseAwardsWindow(WindowImpl):

    def __init__(self, **kwargs):
        super(MentoringLicenseAwardsWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.TOP_WINDOW, content=MentoringLicenseAwardsView(**kwargs))
