# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/gf_notifications/crew_reward_notification.py
from __future__ import absolute_import
from gui.impl.gen.view_models.views.lobby.crew.tankman_model import TankmanKind
from gui.impl.lobby.crew.filter import FilterState
from gui.impl.lobby.crew.filter.data_providers import RecruitsDataProvider
from gui.impl.lobby.crew.filter.state import Persistor
from gui.impl.lobby.gf_notifications.notification_base import NotificationBase
from halloween.gui.impl.gen.view_models.views.lobby.notifications.crew_reward_notification_model import CrewRewardNotificationModel
from gui.shared.event_dispatcher import showBarracks
from halloween.skeletons.halloween_twitch_con_controller import IHalloweenTwitchConController
from helpers import dependency
from gui.server_events.recruit_helper import getRecruitInfo
from shared_utils import first

class CrewRewardNotification(NotificationBase):
    _hwTwitchConCtrl = dependency.descriptor(IHalloweenTwitchConController)

    def __init__(self, resId, *args, **kwargs):
        model = CrewRewardNotificationModel()
        super(CrewRewardNotification, self).__init__(resId, model, *args, **kwargs)
        self._filterState = FilterState(initialState={FilterState.GROUPS.TANKMANKIND.value: TankmanKind.RECRUIT.value}, persistor=Persistor(storageKey='barracks', persistentGroups=[FilterState.GROUPS.TANKMANKIND.value], ignoreDefault=True))
        self._recruitsDataProvider = RecruitsDataProvider(self._filterState)

    def _finalize(self):
        self._recruitsDataProvider = None
        super(CrewRewardNotification, self)._finalize()
        return

    @property
    def viewModel(self):
        return super(CrewRewardNotification, self).getViewModel()

    def _subscribe(self):
        super(CrewRewardNotification, self)._subscribe()
        self.viewModel.onRecruit += self._onRecruit

    def _unsubscribe(self):
        self.viewModel.onRecruit -= self._onRecruit
        super(CrewRewardNotification, self)._unsubscribe()

    def _update(self):
        commanderID = self._getPayload().get('commanderID')
        if not commanderID:
            return
        else:
            commander = self._hwTwitchConCtrl.getCommanderByID(commanderID)
            bonus = first(commander.bonuses)
            tokenID = first(bonus.getTokens().keys())
            recruitInfo = getRecruitInfo(tokenID)
            if recruitInfo is None:
                return
            self._recruitsDataProvider.reinit()
            self._recruitsDataProvider.update()
            recruit = next((r for r in self._recruitsDataProvider.items() if r.getRecruitID() == tokenID), None)
            isRecruted = recruit is None
            iconName = recruitInfo.getDynIconName()
            name, surname = recruitInfo.getFullUserNameByNation(nationID=None).split(' ', 1)
            with self.viewModel.transaction() as model:
                model.setPreName(name)
                model.setSurName(surname)
                model.setIcon(iconName)
                model.setIsRecruited(isRecruted)
                model.setIsPopUp(self._isPopUp)
            return

    def _onRecruit(self):
        showBarracks()
