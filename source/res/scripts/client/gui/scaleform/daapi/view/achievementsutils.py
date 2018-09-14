# Embedded file name: scripts/client/gui/Scaleform/daapi/view/AchievementsUtils.py
from dossiers2.ui.achievements import ACHIEVEMENT_SECTION, ACHIEVEMENT_TYPE
from dossiers2.custom.config import RECORD_CONFIGS
from gui.shared.gui_items.dossier.achievements.abstract import isRareAchievement
from gui.Scaleform.genConsts.ACHIEVEMENTS_ALIASES import ACHIEVEMENTS_ALIASES

class AchievementsUtils(object):

    def __init__(self):
        super(AchievementsUtils, self).__init__()

    @staticmethod
    def packAchievementList(target, dossierType, dossierCompactDescriptor, isDossierForCurrentUser, defaultShowProgress = True, defaultSeriesCounter = None):
        return [ AchievementsUtils.packAchievement(a, dossierType, dossierCompactDescriptor, isDossierForCurrentUser, defaultShowProgress, defaultSeriesCounter) for a in target ]

    @staticmethod
    def packAchievement(achievement, dossierType, dossierCompDescr, isDossierForCurrentUser, defaultShowProgress = True, defaultSeriesCounter = None):
        atype = achievement.getType()
        total = achievement.getLevelUpTotalValue() or 0
        lvlUpValue = achievement.getLevelUpValue() or 0
        current = total - lvlUpValue
        progress = None
        section = achievement.getSection()
        if atype == ACHIEVEMENT_TYPE.REPEATABLE:
            if section == ACHIEVEMENT_SECTION.SPECIAL or section == ACHIEVEMENT_SECTION.BATTLE:
                if total > 0:
                    progress = (0, current, total)
        elif atype == ACHIEVEMENT_TYPE.SERIES:
            if section == ACHIEVEMENT_SECTION.SPECIAL:
                minRecordValue = -1
                if atype == ACHIEVEMENT_TYPE.SERIES and section == ACHIEVEMENT_SECTION.SPECIAL:
                    minRecordValue = RECORD_CONFIGS.get(achievement.getName())
                MIN_PROGRESS_PERCENT = 0.9
                divisionVal = 0
                if total != 0:
                    divisionVal = current / total
                if divisionVal >= MIN_PROGRESS_PERCENT or current != 0 and lvlUpValue < minRecordValue:
                    progress = (0, current, total)
        elif atype == ACHIEVEMENT_TYPE.CUSTOM:
            if section == ACHIEVEMENT_SECTION.SPECIAL:
                if current != total:
                    progress = (0, current, total)
            else:
                progress = (0, current, total)
        elif atype == ACHIEVEMENT_TYPE.CLASS:
            if current != total:
                progress = (0, current, total)
        elif atype == ACHIEVEMENT_TYPE.SINGLE:
            if current != total and not achievement.getValue():
                progress = (0, current, total)
        isRare = isRareAchievement(achievement)
        if isRare:
            rareIconID = achievement.requestImageID()
        else:
            rareIconID = None
        if not defaultShowProgress or not isDossierForCurrentUser:
            progress = None
        commonData = AchievementsUtils.getCommonAchievementData(achievement, dossierType, dossierCompDescr, 1 if achievement.isInDossier() else 0.2)
        commonData.update({'isRare': isRare,
         'rareIconId': rareIconID,
         'counterType': AchievementsUtils.getCounterType(achievement, defaultSeriesCounter),
         'progress': progress,
         'isDossierForCurrentUser': isDossierForCurrentUser})
        return commonData

    @staticmethod
    def getCommonAchievementData(achievement, dossierType, dossierCompDescr, iconAlpha = 1):
        icons = achievement.getIcons()
        return {'name': achievement.getName(),
         'block': achievement.getBlock(),
         'type': achievement.getType(),
         'section': achievement.getSection(),
         'value': achievement.getValue(),
         'localizedValue': achievement.getI18nValue(),
         'isInDossier': achievement.isInDossier(),
         'icon': {'big': icons['180x180'],
                  'small': icons['67x71']},
         'dossierType': dossierType,
         'dossierCompDescr': dossierCompDescr,
         'iconAlpha': iconAlpha}

    @staticmethod
    def getCounterType(achievement, defaultSeriesCounter = None):
        counterType = None
        section = achievement.getSection()
        atype = achievement.getType()
        in_dossier = achievement.isInDossier()
        if atype == ACHIEVEMENT_TYPE.REPEATABLE:
            if section == ACHIEVEMENT_SECTION.SPECIAL or section == ACHIEVEMENT_SECTION.BATTLE:
                if in_dossier:
                    counterType = ACHIEVEMENTS_ALIASES.RED_COUNTER
            elif section == ACHIEVEMENT_SECTION.ACTION:
                if achievement.hasCounter():
                    counterType = ACHIEVEMENTS_ALIASES.RED_COUNTER
            elif in_dossier:
                counterType = ACHIEVEMENTS_ALIASES.RED_COUNTER
        elif atype == ACHIEVEMENT_TYPE.SERIES:
            if in_dossier:
                counterType = defaultSeriesCounter if defaultSeriesCounter is not None else ACHIEVEMENTS_ALIASES.YELLOW_COUNTER
        elif atype == ACHIEVEMENT_TYPE.CUSTOM:
            if section == ACHIEVEMENT_SECTION.SPECIAL:
                counterType = None
        elif atype == ACHIEVEMENT_TYPE.CLASS:
            counterType = ACHIEVEMENTS_ALIASES.BEIGE_COUNTER
        return counterType
