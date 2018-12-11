# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/loyal_service.py
import BigWorld
from gui.shared.gui_items.dossier.achievements.abstract import DeprecatedAchievement
from helpers import i18n

class LoyalServiceAchievement(DeprecatedAchievement):

    def __init__(self, name, block, dossier, value=None):
        super(LoyalServiceAchievement, self).__init__(name, block, dossier, value)
        if dossier is not None:
            self.__registrationDate = BigWorld.wg_getLongDateFormat(dossier.getDossierDescr()['total']['creationTime'])
        else:
            self.__registrationDate = None
        return

    def getUserDescription(self):
        return i18n.makeString('#achievements:{}_descr'.format(self._getActualName()), regDate=self.__registrationDate) if self.__registrationDate else ''
