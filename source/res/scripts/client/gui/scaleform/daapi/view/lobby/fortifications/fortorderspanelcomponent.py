# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortOrdersPanelComponent.py
from constants import CLAN_MEMBER_FLAGS
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_text
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.framework import AppRef
from gui.Scaleform.daapi.view.meta.OrdersPanelMeta import OrdersPanelMeta
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.ClanCache import g_clanCache
from gui.shared.SoundEffectsId import SoundEffectsId
from helpers import i18n

class FortOrdersPanelComponent(OrdersPanelMeta, FortViewHelper, AppRef):

    def _populate(self):
        super(FortOrdersPanelComponent, self)._populate()
        self.startFortListening()
        self.__orders = []
        self._buildList()

    def _dispose(self):
        self.stopFortListening()
        self.__orders = None
        super(FortOrdersPanelComponent, self)._dispose()
        return

    def _buildList(self):
        result = []
        for buildingID in self.BUILDINGS:
            orderID = self.fortCtrl.getFort().getBuildingOrder(buildingID)
            uid = self.UI_BUILDINGS_BIND[buildingID]
            order = self.fortCtrl.getFort().getOrder(orderID)
            isRecharged = False
            for savedOrder in self.__orders:
                if savedOrder['orderID'] == self.UI_ORDERS_BIND[orderID]:
                    if savedOrder['count'] < order.count:
                        isRecharged = True

            if isRecharged == True:
                if self.app.soundManager is not None:
                    self.app.soundManager.playEffectSound(SoundEffectsId.FORT_ORDER_ISREADY)
            result.append({'enabled': order.hasBuilding,
             'orderID': self.UI_ORDERS_BIND[orderID],
             'orderIcon': order.icon,
             'count': order.count,
             'level': order.level,
             'inProgress': order.inProgress,
             'buildingStr': i18n.makeString(FORTIFICATIONS.buildings_buildingname(uid)),
             'inCooldown': order.inCooldown,
             'cooldownPercent': order.getCooldownAsPercent(),
             'leftTime': order.getUsageLeftTime(),
             'isPermanent': order.isPermanent,
             'isRecharged': isRecharged})

        self.as_setOrdersS(result)
        self.__orders = result
        return

    def getOrderTooltipBody(self, orderID):
        order = self.fortCtrl.getFort().getOrder(self.UI_ORDERS_BIND.index(orderID))
        if order.hasBuilding:
            ordersListStr = i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPOPOVER_CLANPERMISSIONS)
            description = ''
            if order.inCooldown:
                description = self._getCooldownInfo(order)
            elif order.count > 0:
                description = i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPOPOVER_ORDERISREADY)
                if not self._canGiveOrder():
                    description += '\n' + ordersListStr
            else:
                if not order.inProgress:
                    description = i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPOPOVER_CREATEORDER)
                if not self._canGiveOrder():
                    description = i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPOPOVER_USEORDERBTN_NOORDERS)
                    description += '\n' + ordersListStr
            if order.inProgress:
                description = self._getProgressInfo(description, order)
        else:
            buildingStr = i18n.makeString(FORTIFICATIONS.buildings_buildingname(self.UI_BUILDINGS_BIND[order.buildingID]))
            description = i18n.makeString(FORTIFICATIONS.ORDERS_ORDERPOPOVER_ORDERNOTREADY, building=buildingStr)
        return description

    def _canGiveOrder(self):
        return g_clanCache.clanRole in (CLAN_MEMBER_FLAGS.LEADER, CLAN_MEMBER_FLAGS.VICE_LEADER)

    def _getRolesStr(self):
        leader = i18n.makeString(FORTIFICATIONS.FORTIFICATION_CLAN_POSITION_LEADER)
        vice_leader = i18n.makeString(FORTIFICATIONS.FORTIFICATION_CLAN_POSITION_VICE_LEADER)
        return leader + ', ' + vice_leader

    def _getProgressInfo(self, description, order):
        createdTime = order.getProductionLeftTime()
        createdTimeStr = fort_text.getTimeDurationStr(createdTime)
        productionCountStr = ''
        if order.productionCount > 1:
            productionCountStr = ' (x%d)' % order.productionCount
        text = i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPOPOVER_INPROGRESS_TEXT, count=productionCountStr)
        text += '\n' + i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPOPOVER_INPROGRESS_TIMELEFT, timeLeft=createdTimeStr)
        if len(description) > 0:
            description += '\n' + text
        else:
            description = text
        return description

    def _getCooldownInfo(self, order):
        if not order.isPermanent:
            leftTime = order.getUsageLeftTime()
            leftTimeStr = fort_text.getTimeDurationStr(leftTime)
            return i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPOPOVER_PROGRESSBAR_TIMELEFT, timeLeft=leftTimeStr)
        else:
            return i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPOPOVER_INDEFENSIVE)

    def onUpdated(self):
        self._buildList()
