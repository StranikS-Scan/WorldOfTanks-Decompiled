# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ui/black_market.py
import logging
from gui.impl.gen import R
from gui.impl import backport
from helpers import dependency
from web.web_client_api import w2c, W2CSchema, Field
from web.web_client_api.common import ItemPackEntry, ItemPackType
from gui.shared import event_dispatcher as shared_events
from gui.server_events.events_dispatcher import showMissionsMarathon
from skeletons.gui.game_control import ICollectiveGoalEntryPointController, IBlackMarketController
_logger = logging.getLogger(__name__)

class _BlackMarketTabSchema(W2CSchema):
    vehCD = Field(required=True, type=int)


class BlackMarketWebApiMixin(object):
    __blackMarket = dependency.descriptor(IBlackMarketController)
    __collectiveGoalEntryPointController = dependency.descriptor(ICollectiveGoalEntryPointController)

    @w2c(_BlackMarketTabSchema, 'black_market_vehicle_preview')
    def showBlackMarketVehiclePreview(self, cmd):
        if self.__blackMarket.isEnabled():
            shared_events.showVehiclePreviewWithoutBottomPanel(cmd.vehCD, backCallback=self.__getPreviewCallback, backBtnLabel=backport.text(R.strings.black_market.header.backBtn.descrLabel.hangar()), itemsPack=(ItemPackEntry(type=ItemPackType.CREW_100, groupID=1),))
        else:
            _logger.error('Black Market is not active at the moment!')

    def __getPreviewCallback(self):
        marathonPrefix = self.__collectiveGoalEntryPointController.getMarathonPrefix()
        if marathonPrefix:
            showMissionsMarathon(marathonPrefix)
        else:
            _logger.error("Marathon %s isn't found. Check collective goal config", marathonPrefix)
