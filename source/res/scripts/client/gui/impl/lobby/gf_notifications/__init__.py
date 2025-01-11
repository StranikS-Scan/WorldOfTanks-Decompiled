# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/gf_notifications/__init__.py
from debug_utils import LOG_ERROR
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.gen import R
from gui.impl.lobby.gf_notifications.ny.ny_piggy_bank import NyPiggyBankSingleReward, NyPiggyBankMultipleRewards
from gui.shared.system_factory import registerGamefaceNotifications, collectGamefaceNotifications
from ny.ny_attached_3d_rewards import NyAttached3DRewards
from ny.ny_challenge_rewards import NyChallengeRewards
from ny.ny_dog_mission_completed import NyDogMissionCompleted
from ny.ny_dog_reminder import NyDogReminder
from ny.ny_new_reward_kit import NyNewRewardKit
from ny.ny_quest_rewards import NyQuestReward
from ny.ny_resources_reminder import NyResourcesReminder
from ny.ny_sack_rare_loot import NySackRareLoot
from ny.receiving_awards import ReceivingAwards
registerGamefaceNotifications({'NyDogReminder': (R.views.lobby.new_year.notifications.NyDogReminder(), NyDogReminder),
 'NyDogMissionCompleted': (R.views.lobby.new_year.notifications.NyDogMissionCompleted(), NyDogMissionCompleted),
 'NySackRareLoot': (R.views.lobby.new_year.notifications.NySackRareLoot(), NySackRareLoot),
 'NyResourcesReminder': (R.views.lobby.new_year.notifications.NyResourcesReminder(), NyResourcesReminder),
 'ReceivingAwards': (R.views.lobby.new_year.notifications.NyReceivingAwards(), ReceivingAwards),
 'ChallengeRewards': (R.views.lobby.new_year.notifications.NyChallengeRewards(), NyChallengeRewards),
 'AssignmentsRewards': (R.views.lobby.new_year.notifications.NyAssignmentsRewards(), NyQuestReward),
 'NyNewRewardKit': (R.views.lobby.new_year.notifications.NyNewRewardKit(), NyNewRewardKit),
 'PiggyBankSingleReward': (R.views.lobby.new_year.notifications.NyPiggyBankSingleReward(), NyPiggyBankSingleReward),
 'PiggyBankMultipleRewards': (R.views.lobby.new_year.notifications.NyPiggyBankMultipleRewards(), NyPiggyBankMultipleRewards),
 'NyAttached3DRewards': (R.views.lobby.new_year.notifications.NyAttached3DRewards(), NyAttached3DRewards)})

class GFNotificationInject(InjectComponentAdaptor):

    def __init__(self, gfViewName, isPopUp, linkageData, *args, **kwargs):
        self.__gfViewName = gfViewName
        self.__isPopUp = isPopUp
        self.__linkageData = linkageData
        super(GFNotificationInject, self).__init__()

    def _makeInjectView(self):
        resId, presenter = PresentersFactory.get(self.__gfViewName)
        return presenter(resId, self.__isPopUp, self.__linkageData)


class PresentersFactory(object):

    @staticmethod
    def get(viewName):
        resId, clazz = collectGamefaceNotifications().get(viewName, None)
        if clazz is not None:
            return (resId, clazz)
        else:
            LOG_ERROR("Cant fined presenter for '%s'" % viewName)
            return
