# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/awards_formatters.py
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import NewStyleBonusComposer
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.auxiliary.rewards_helper import NEW_STYLE_FORMATTED_BONUSES
from gui.server_events import formatters
from gui.server_events.awards_formatters import AWARDS_SIZES, AwardsPacker, QuestsBonusComposer, getPostBattleAwardsPacker
from gui.server_events.bonuses import BlueprintsBonusSubtypes, formatBlueprint
from gui.battle_pass.battle_pass_bonuses_helper import BonusesHelper
from gui.shared.gui_items.crew_skin import localizedFullName as localizeSkinName
from nations import NAMES
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


class CrewBookFormatter(OldStyleBonusFormatter):

    @classmethod
    def getOrder(cls):
        pass

    def accumulateBonuses(self, bonus):
        result = []
        for book, count in sorted(bonus.getItems()):
            if book is None or not count:
                continue
            result.append(self._formatBook(book, count))

        if result:
            self._result.append(formatters.packSimpleBonusesBlock(result))
        return

    @classmethod
    def _formatBook(cls, book, count):
        return backport.text(R.strings.quests.bonuses.items.name(), name=book.userName, count=count)


class CrewSkinFormatter(OldStyleBonusFormatter):

    @classmethod
    def getOrder(cls):
        pass

    def accumulateBonuses(self, bonus):
        result = []
        for skin, count, _, _ in sorted(bonus.getItems()):
            if skin is None or not count:
                continue
            result.append(self._formatCrewSkin(skin, count))

        if result:
            self._result.append(formatters.packSimpleBonusesBlock(result))
        return

    @classmethod
    def _formatCrewSkin(cls, skin, count):
        return backport.text(R.strings.quests.bonuses.items.name(), name=localizeSkinName(skin), count=count)


class BlueprintsFormatter(OldStyleBonusFormatter):
    _ORDER = [BlueprintsBonusSubtypes.FINAL_FRAGMENT,
     BlueprintsBonusSubtypes.UNIVERSAL_FRAGMENT,
     BlueprintsBonusSubtypes.NATION_FRAGMENT,
     BlueprintsBonusSubtypes.VEHICLE_FRAGMENT,
     BlueprintsBonusSubtypes.RANDOM_FRAGMENT,
     BlueprintsBonusSubtypes.RANDOM_NATIONAL_FRAGMENT]

    def __init__(self):
        super(BlueprintsFormatter, self).__init__()
        self._groupedFragments = {}

    @classmethod
    def getOrder(cls):
        pass

    def accumulateBonuses(self, bonus):
        blueprintType = bonus.getBlueprintName()
        fragments = self._groupedFragments.get(blueprintType, [])
        fragments.append(bonus)
        self._groupedFragments[blueprintType] = fragments

    def extractFormattedBonuses(self, addLineSeparator=False):
        result = []
        for fragmentType in self._ORDER:
            fragments = self._groupedFragments.get(fragmentType)
            if fragments:
                fragmentLabels = []
                for fragment in fragments:
                    fragmentLabels.append(formatBlueprint(fragment, fragment.getCount()))

                result.append(formatters.packLongBonusesBlock(fragmentLabels, linesLimit=len(NAMES)))

        self._groupedFragments = {}
        return result


class BattlePassPointsFormatter(OldStyleBonusFormatter):

    def accumulateBonuses(self, bonus):
        formattedList = bonus.formattedList()
        if formattedList:
            self._result.append(formatters.packSimpleBonusesBlock(formattedList))


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


class TextBonusFormatter(OldStyleBonusFormatter):

    def accumulateBonuses(self, bonus, event=None):
        formattedList = BonusesHelper.getTextStrings(bonus)
        if formattedList:
            self._result.extend(formattedList)

    def extractFormattedBonuses(self, addLineSeparator=False):
        simpleBonusesList = super(TextBonusFormatter, self).extractFormattedBonuses()
        result = []
        if simpleBonusesList:
            result.append(formatters.packSimpleBonusesBlock(simpleBonusesList, endlineSymbol=_END_LINE_SEPARATOR if addLineSeparator else _EMPTY_STRING))
        return result


class BattlePassStyleProgressFormatter(OldStyleBonusFormatter):

    def accumulateBonuses(self, bonus, event=None):
        formattedList = BonusesHelper.getTextStrings(bonus)
        if formattedList:
            self._result.append(formatters.packSimpleBonusesBlock(formattedList))


class NewStyleBonusFormatter(OldStyleBonusFormatter):

    def __init__(self, awardsPacker=None):
        super(NewStyleBonusFormatter, self).__init__()
        self.__formatter = NewStyleBonusComposer(_DISPLAYED_AWARDS_COUNT, awardsPacker or getPostBattleAwardsPacker())

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
     'vehicles': VehiclesFormatter(event),
     'crewBooks': CrewBookFormatter(),
     'blueprints': BlueprintsFormatter(),
     'crewSkins': CrewSkinFormatter(),
     'battlePassPoints': BattlePassPointsFormatter()}


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


def getTextFormattersMap():
    return {'default': TextBonusFormatter(),
     'customizations': CustomizationsFormatter(),
     'styleProgressToken': BattlePassStyleProgressFormatter()}


class BattlePassTextBonusesPacker(AwardsPacker):

    def __init__(self):
        super(BattlePassTextBonusesPacker, self).__init__(getTextFormattersMap())

    def format(self, bonuses, event=None):
        formattedBonuses = []
        for b in bonuses:
            if b.isShowInGUI():
                formatter = self._getBonusFormatter(b.getName())
                if formatter:
                    formatter.accumulateBonuses(b)

        for formatter in sorted(self.getFormatters().itervalues(), key=lambda f: f.getOrder()):
            formattedBonuses.extend(formatter.extractFormattedBonuses())

        return formattedBonuses

    def _getBonusFormatter(self, bonusName):
        formattersMap = self.getFormatters()
        return formattersMap[bonusName] if bonusName in formattersMap else formattersMap.get('default', None)


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
