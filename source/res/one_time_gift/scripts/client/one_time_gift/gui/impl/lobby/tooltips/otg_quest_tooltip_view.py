# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/impl/lobby/tooltips/otg_quest_tooltip_view.py
import logging
import typing
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.server_events.event_items import PersonalQuest
from helpers import dependency
from shared_utils import first
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from one_time_gift.gui.impl.gen.view_models.views.lobby.otg_quest_tooltip_view_model import OtgQuestTooltipViewModel
if typing.TYPE_CHECKING:
    from gui.server_events.event_items import Quest
_logger = logging.getLogger(__name__)

class OTGQuestTooltipView(ViewImpl):
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, requiredToken):
        settings = ViewSettings(R.views.one_time_gift.mono.lobby.one_time_gift_quest_tooltip())
        settings.model = OtgQuestTooltipViewModel()
        settings.kwargs = {'requiredToken': requiredToken}
        super(OTGQuestTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(OTGQuestTooltipView, self).getViewModel()

    def _onLoading(self, requiredToken, *args, **kwargs):
        super(OTGQuestTooltipView, self)._onLoading(*args, **kwargs)

        def filterFunc(quest):
            return isinstance(quest, PersonalQuest) and quest.getRequiredToken() == requiredToken

        quest = first(self.__eventsCache.getQuests(filterFunc).values())
        if quest is None:
            _logger.warning('OneTimeGift quests not found on account')
            return
        else:
            tokenExpiryTime = self.__itemsCache.items.tokens.getTokenExpiryTime(requiredToken)
            questFinishTime = quest.getFinishTime()
            self.viewModel.setExpireTime(min(tokenExpiryTime, questFinishTime))
            return
