# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/prb_control/formatters/invites.py
from fun_random_common.fun_constants import UNKNOWN_EVENT_ID
from fun_random.gui.feature.util.fun_mixins import FunAssetPacksMixin, FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasSpecifiedSubMode
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.formatters.invites import PrbInviteHtmlTextFormatter
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from shared_utils import first
from skeletons.gui.shared import IItemsCache

class FunPrbInviteHtmlTextFormatter(PrbInviteHtmlTextFormatter, FunAssetPacksMixin, FunSubModesWatcher):
    __itemsCache = dependency.descriptor(IItemsCache)

    def canAcceptInvite(self, invite):
        canAccept = super(FunPrbInviteHtmlTextFormatter, self).canAcceptInvite(invite)
        return canAccept and self.__hasAnyVehicle()

    def getIconPath(self, invite, pathMaker=None):
        return backport.image(self.getModeIconsResRoot().library.invite_notification())

    def updateTooltips(self, invite, canAccept, message):
        if not canAccept and 'buttonsLayout' in message and not self.__hasAnyVehicle():
            tooltip = makeTooltip(body=backport.text(R.strings.fun_random.invite.tooltip.noVehicles()))
            message['buttonsLayout'][0]['tooltip'] = tooltip
        return message

    def _getTitle(self, invite, kwargs=None):
        subModeID = first(invite.getExtraData('unitInviteExtras', []), UNKNOWN_EVENT_ID)
        detailedModeName = self.__getDetailedModeName(subModeID) or self.getModeUserName()
        return backport.text(R.strings.fun_random.invite.text.detailedTitle(), detailedModeName=detailedModeName)

    def __hasAnyVehicle(self):
        return bool(self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY))

    @hasSpecifiedSubMode(defReturn='')
    def __getDetailedModeName(self, subModeID):
        subModeName = backport.text(self.getSubMode(subModeID).getLocalsResRoot().userName())
        return self.getModeDetailedUserName(subModeName=subModeName)
