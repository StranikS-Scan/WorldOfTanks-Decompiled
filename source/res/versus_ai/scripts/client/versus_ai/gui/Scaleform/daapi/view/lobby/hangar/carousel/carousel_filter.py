# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: versus_ai/scripts/client/versus_ai/gui/Scaleform/daapi/view/lobby/hangar/carousel/carousel_filter.py
from account_helpers.AccountSettings import VERSUS_AI_CAROUSEL_FILTER_1, VERSUS_AI_CAROUSEL_FILTER_2, VERSUS_AI_CAROUSEL_FILTER_CLIENT_1, BATTLEPASS_CAROUSEL_FILTER_1, BATTLEPASS_CAROUSEL_FILTER_CLIENT_1
from gui.Scaleform.daapi.view.lobby.hangar.carousels.battle_pass.carousel_filter import BattlePassCarouselFilter, BattlePassCriteriesGroup
from gui.shared.utils.requesters import REQ_CRITERIA
from versus_ai.gui.prb_control.entities.pre_queue.actions_validator import VersusAIVehicleValidator

class VersusAICarouselFilter(BattlePassCarouselFilter):

    def __init__(self):
        super(VersusAICarouselFilter, self).__init__()
        self._serverSections = (VERSUS_AI_CAROUSEL_FILTER_1, VERSUS_AI_CAROUSEL_FILTER_2, BATTLEPASS_CAROUSEL_FILTER_1)
        self._clientSections = (VERSUS_AI_CAROUSEL_FILTER_CLIENT_1, BATTLEPASS_CAROUSEL_FILTER_CLIENT_1)
        self._criteriesGroups = (VersusAICriteriesGroup(),)


class VersusAICriteriesGroup(BattlePassCriteriesGroup):

    def update(self, filters):
        super(VersusAICriteriesGroup, self).update(filters)
        self._criteria |= REQ_CRITERIA.CUSTOM(self._versusAICriteria)

    @classmethod
    def _versusAICriteria(cls, vehicle):
        return VersusAIVehicleValidator.validateForVersusAI(vehicle) is None
