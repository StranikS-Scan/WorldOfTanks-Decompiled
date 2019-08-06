# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/awards_formatters.py
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import NewStyleBonusComposer
from gui.impl.auxiliary.rewards_helper import NEW_STYLE_FORMATTED_BONUSES
from gui.server_events import formatters
from gui.server_events.awards_formatters import AWARDS_SIZES, AwardsPacker, QuestsBonusComposer, getPostBattleAwardsPacker
SIMPLE_BONUSES_MAX_ITEMS = 5
_DISPLAYED_AWARDS_COUNT = 2
_END_LINE_SEPARATOR = ','
_EMPTY_STRING = ''

class OldStyleBonusFormatter(object):

    def __init__(self):
        self._result = []

    def accumulateBonuses(self, bonus):
        self._result.append(bonus)

    def extractFormattedBonuses(self, addLineSeparator=False):
        result = self._result[:]
        self._result = []
        return result

    @classmethod
    def getOrder(cls):
        pass


class DossierFormatter(OldStyleBonusFormatter):

    @classmethod
    def getOrder(cls):
        pass

    def accumulateBonuses(self, bonus):
        for achieve in bonus.getAchievements():
            self._result.append(formatters.packAchieveElementByItem(achieve))

        for badge in bonus.getBadges():
            self._result.append(formatters.packBadgeElementByItem(badge))


class CustomizationsFormatter(OldStyleBonusFormatter):

    @classmethod
    def getOrder(cls):
        pass

    def accumulateBonuses(self, bonus):
        customizationsList = bonus.getList()
        if customizationsList:
            self._result.append(formatters.packCustomizations(customizationsList))


class VehiclesFormatter(OldStyleBonusFormatter):

    def __init__(self, event):
        super(VehiclesFormatter, self).__init__()
        self.__eventID = str(event.getID())

    @classmethod
    def getOrder(cls):
        pass

    def accumulateBonuses(self, bonus, event=None):
        formattedList = bonus.formattedList()
        if formattedList:
            vehiclesLbl, _ = _joinUpToMax(formattedList)
            self._result.append(formatters.packVehiclesBonusBlock(vehiclesLbl, self.__eventID))


class SimpleBonusFormatter(OldStyleBonusFormatter):

    def accumulateBonuses(self, bonus, event=None):
        formattedList = bonus.formattedList()
        if formattedList:
            self._result.extend(formattedList)

    def extractFormattedBonuses(self, addLineSeparator=False):
        simpleBonusesList = super(SimpleBonusFormatter, self).extractFormattedBonuses()
        result = []
        if simpleBonusesList:
            result.append(formatters.packSimpleBonusesBlock(simpleBonusesList, endlineSymbol=_END_LINE_SEPARATOR if addLineSeparator else _EMPTY_STRING))
        return result


class NewStyleBonusFormatter(OldStyleBonusFormatter):

    def __init__(self):
        super(NewStyleBonusFormatter, self).__init__()
        self.__formatter = NewStyleBonusComposer(_DISPLAYED_AWARDS_COUNT, getPostBattleAwardsPacker())

    def accumulateBonuses(self, bonus, event=None):
        formattedBonuses = self.__formatter.getVisibleFormattedBonuses([], [bonus], 'big')
        if formattedBonuses:
            self._result.extend(formattedBonuses)

    def extractFormattedBonuses(self, addLineSeparator=False):
        simpleBonusesList = super(NewStyleBonusFormatter, self).extractFormattedBonuses()
        result = []
        if simpleBonusesList:
            result.append(formatters.packNewStyleBonusesBlock(simpleBonusesList, endlineSymbol=_END_LINE_SEPARATOR if addLineSeparator else _EMPTY_STRING))
        return result


def getFormattersMap(event):
    return {'dossier': DossierFormatter(),
     'customizations': CustomizationsFormatter(),
     'vehicles': VehiclesFormatter(event)}


class OldStyleAwardsPacker(AwardsPacker):

    def __init__(self, event):
        super(OldStyleAwardsPacker, self).__init__(getFormattersMap(event))
        self.__defaultFormatter = SimpleBonusFormatter()
        self.__newStyleFormatter = NewStyleBonusFormatter()

    def format(self, bonuses, event=None):
        formattedBonuses = []
        isCustomizationBonusExist = False
        for b in bonuses:
            if b.isShowInGUI():
                formatter = self._getBonusFormatter(b.getName())
                if formatter:
                    formatter.accumulateBonuses(b)
                if b.getName() == 'customizations':
                    isCustomizationBonusExist = True

        fmts = [self.__defaultFormatter, self.__newStyleFormatter]
        fmts.extend(sorted(self.getFormatters().itervalues(), key=lambda f: f.getOrder()))
        for formatter in fmts:
            formattedBonuses.extend(formatter.extractFormattedBonuses(isCustomizationBonusExist))

        return formattedBonuses

    def _getBonusFormatter(self, bonusName):
        return self.__newStyleFormatter if bonusName in NEW_STYLE_FORMATTED_BONUSES else self.getFormatters().get(bonusName, self.__defaultFormatter)


class OldStyleBonusesFormatter(QuestsBonusComposer):

    def __init__(self, event):
        super(OldStyleBonusesFormatter, self).__init__(OldStyleAwardsPacker(event))

    def getFormattedBonuses(self, bonuses, size=AWARDS_SIZES.SMALL):
        return self.getPreformattedBonuses(bonuses)


def _joinUpToMax(array, separator=', '):
    if len(array) > SIMPLE_BONUSES_MAX_ITEMS:
        label = separator.join(array[:SIMPLE_BONUSES_MAX_ITEMS]) + '..'
        fullLabel = separator.join(array)
    else:
        label = separator.join(array)
        fullLabel = None
    return (label, fullLabel)
