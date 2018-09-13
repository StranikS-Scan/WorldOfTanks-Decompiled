# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/AimerAchievement.py
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB
from abstract import SeriesAchievement
from abstract.mixins import NoProgressBar
from helpers import i18n

class AimerAchievement(NoProgressBar, SeriesAchievement):

    def __init__(self, dossier, value = None):
        SeriesAchievement.__init__(self, 'aimer', _AB.SINGLE, dossier, value)

    def __getActualName(self):
        return 'maxAimerSeries'

    def getUserName(self):
        return i18n.makeString('#achievements:%s' % self.__getActualName())

    def getUserDescription(self):
        return i18n.makeString('#achievements:%s_descr' % self.__getActualName())

    def getUserCondition(self):
        condKey = '#achievements:%s_condition' % self.__getActualName()
        if i18n.doesTextExist(condKey):
            return i18n.makeString(condKey)
        return ''

    def _getCounterRecordNames(self):
        return ((_AB.TOTAL, 'maxAimerSeries'), (_AB.TOTAL, 'maxAimerSeries'))
