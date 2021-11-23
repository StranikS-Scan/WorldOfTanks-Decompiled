# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/shop/telecom_rentals.py
import logging
import BigWorld
from account_helpers.telecom_rentals import TelecomRentals
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.Vehicle import getUserName
from items.vehicles import getVehicleType
from web.web_client_api import W2CSchema, w2c, Field
_logger = logging.getLogger(__name__)

class _TelecomRentalsRentVehicleInfoSchema(W2CSchema):
    vehCD = Field(required=True, type=int)


class TelecomRentalsWebApiMixin(object):

    @w2c(W2CSchema, 'get_telecom_rentals_info')
    def getTelecomRentalsInfo(self, cmd):
        helper = BigWorld.player().telecomRentals
        return {'active': helper.isActive(),
         'rent_token_total': helper.getTotalRentCount(),
         'rent_token_count': 0 if helper.isBlocked() else helper.getAvailableRentCount(),
         'expiration_date': helper.getRosterExpirationTime()}

    @w2c(_TelecomRentalsRentVehicleInfoSchema, 'telecom_rent_delayed')
    def telecomRentDelayed(self, cmd):
        if cmd.vehCD:
            BigWorld.player().telecomRentals.setRentPending(cmd.vehCD)
            vehName = getUserName(getVehicleType(cmd.vehCD))
            SystemMessages.pushMessage('', messageData={'header': backport.text(R.strings.messenger.serviceChannelMessages.wotPlus.tankRental.isPending.title()),
             'text': backport.text(R.strings.messenger.serviceChannelMessages.wotPlus.tankRental.isPending.text(), vehicle=vehName)}, type=SystemMessages.SM_TYPE.MessageHeader)
