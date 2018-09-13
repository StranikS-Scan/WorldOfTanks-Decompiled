# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/MedalKnispelAchievement.py
from abstract import ClassProgressAchievement
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB

class MedalKnispelAchievement(ClassProgressAchievement):

    def __init__(self, dossier, value = None):
        super(MedalKnispelAchievement, self).__init__('medalKnispel', _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('damageLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'medalKnispel')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getRandomStats().getDamageDealt() + dossier.getRandomStats().getDamageReceived() + dossier.getTeam7x7Stats().getDamageDealt() + dossier.getTeam7x7Stats().getDamageReceived() + dossier.getFortBattlesStats().getDamageDealt() + dossier.getFortBattlesStats().getDamageReceived() + dossier.getFortSortiesStats().getDamageDealt() + dossier.getFortSortiesStats().getDamageReceived()
