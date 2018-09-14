# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization/bonus_panel.py
import copy
from gui.Scaleform.genConsts.CUSTOMIZATION_BONUS_ANIMATION_TYPES import CUSTOMIZATION_BONUS_ANIMATION_TYPES
from gui.shared.formatters import text_styles
from helpers.i18n import makeString as _ms
from gui.customization.shared import forEachSlotIn, elementsDiffer, QUALIFIER_TYPE_NAMES, CUSTOMIZATION_TYPE, getBonusIcon42x42

class BonusPanel(object):

    def __init__(self, events):
        self.__animationStarted = False
        self.__events = events
        self.__bonusData = {}
        self.__installedElements = None
        self.__initialSlotsData = None
        self.__initialTooltipData = None
        self.__processingPurchase = False
        return

    def init(self):
        self.__events.onMultiplePurchaseStarted += self.__onPurchaseProcessStarted
        self.__events.onInstalledElementsUpdated += self.__saveInstalledElements
        self.__events.onInitialSlotsSet += self.__setInitialSlotsData
        self.__events.onSlotsSet += self.__update

    def fini(self):
        self.__events.onSlotsSet -= self.__update
        self.__events.onInitialSlotsSet -= self.__setInitialSlotsData
        self.__events.onInstalledElementsUpdated -= self.__saveInstalledElements
        self.__events.onMultiplePurchaseStarted -= self.__onPurchaseProcessStarted
        self.__bonusData.clear()
        self.__installedElements = None
        self.__initialSlotsData = None
        self.__initialTooltipData = None
        self.__processingPurchase = False
        return

    @property
    def bonusData(self):
        return self.__bonusData

    def __setInitialSlotsData(self, iSlotsData):
        if not self.__processingPurchase:
            self.__animationStarted = False
        self.__initialSlotsData = iSlotsData
        oldBonusData = self.__bonusData
        self.__bonusData = {}
        for qTypeName in QUALIFIER_TYPE_NAMES.iterkeys():
            self.__bonusData[qTypeName] = {'bonusName': text_styles.main(_ms('#vehicle_customization:bonusName/{0}'.format(qTypeName))),
             'bonusIcon': getBonusIcon42x42(qTypeName),
             'bonusTotalCount': 0,
             CUSTOMIZATION_TYPE.CAMOUFLAGE: [],
             CUSTOMIZATION_TYPE.EMBLEM: [],
             CUSTOMIZATION_TYPE.INSCRIPTION: [],
             'oldBonusTotalCount': 0,
             'bonusAppliedCount': 0,
             'oldBonusAppliedCount': 0,
             'bonusTotalDescriptionCount': 0,
             'bonusAppliedDescriptionCount': 0}
            if oldBonusData:
                self.__bonusData[qTypeName]['oldBonusTotalCount'] = oldBonusData[qTypeName]['bonusTotalCount']

        forEachSlotIn(iSlotsData, iSlotsData, self.__getInitialBonusData)
        self.__saveInitialTooltipData()

    def __update(self, updatedSlotsData):
        for qTypeName in QUALIFIER_TYPE_NAMES.iterkeys():
            self.__bonusData[qTypeName]['bonusAppliedCount'] = 0

        self.__restoreInitialTooltipData()
        forEachSlotIn(updatedSlotsData, self.__initialSlotsData, self.__recalculateBonusData)
        self.__setAnimations()
        self.__events.onBonusesUpdated(self.__bonusData)

    def __saveInstalledElements(self, newVehicleSelected, installed):
        self.__installedElements = installed

    def __saveDisplayedElements(self, displayedElements, displayedGroups):
        self.__displayedElements = displayedElements

    def __onPurchaseProcessStarted(self):
        self.__processingPurchase = True

    def __saveInitialTooltipData(self):
        self.__initialTooltipData = {}
        for qTypeName in QUALIFIER_TYPE_NAMES.iterkeys():
            self.__initialTooltipData[qTypeName] = {CUSTOMIZATION_TYPE.CAMOUFLAGE: copy.deepcopy(self.__bonusData[qTypeName][CUSTOMIZATION_TYPE.CAMOUFLAGE]),
             CUSTOMIZATION_TYPE.EMBLEM: copy.deepcopy(self.__bonusData[qTypeName][CUSTOMIZATION_TYPE.EMBLEM]),
             CUSTOMIZATION_TYPE.INSCRIPTION: copy.deepcopy(self.__bonusData[qTypeName][CUSTOMIZATION_TYPE.INSCRIPTION])}

    def __restoreInitialTooltipData(self):
        if self.__initialTooltipData is not None:
            for qTypeName in QUALIFIER_TYPE_NAMES.iterkeys():
                self.__bonusData[qTypeName][CUSTOMIZATION_TYPE.CAMOUFLAGE] = copy.deepcopy(self.__initialTooltipData[qTypeName][CUSTOMIZATION_TYPE.CAMOUFLAGE])
                self.__bonusData[qTypeName][CUSTOMIZATION_TYPE.EMBLEM] = copy.deepcopy(self.__initialTooltipData[qTypeName][CUSTOMIZATION_TYPE.EMBLEM])
                self.__bonusData[qTypeName][CUSTOMIZATION_TYPE.INSCRIPTION] = copy.deepcopy(self.__initialTooltipData[qTypeName][CUSTOMIZATION_TYPE.INSCRIPTION])

        return

    def __getInitialBonusData(self, newSlotItem, oldSlotItem, cType, slotIdx):
        newElement = newSlotItem['element']
        if newElement is not None:
            singleBonusData = self.__bonusData[newElement.qualifier.getType()]
            if cType == CUSTOMIZATION_TYPE.CAMOUFLAGE and not singleBonusData['bonusTotalCount'] or cType != CUSTOMIZATION_TYPE.CAMOUFLAGE:
                singleBonusData['bonusTotalCount'] += newElement.qualifier.getValue()
                if newElement.qualifier.getDescription():
                    singleBonusData['bonusTotalDescriptionCount'] += 1
            itemData = {'isApplied': False,
             'available': newElement,
             'installed': self.__installedElements[cType][slotIdx]}
            self.__bonusData[newElement.qualifier.getType()][cType].append(itemData)
        return

    def __recalculateBonusData(self, newSlotData, oldSlotData, cType, slotIdx):
        newElement = newSlotData['element']
        oldElement = oldSlotData['element']
        if elementsDiffer(newElement, oldElement):
            if newElement is not None:
                newValue = newElement.qualifier.getValue()
                newType = newElement.qualifier.getType()
                itemData = {'isApplied': not newSlotData['isInDossier'],
                 'available': newElement,
                 'installed': self.__installedElements[cType][slotIdx]}
                self.__bonusData[newType][cType].append(itemData)
                if cType == CUSTOMIZATION_TYPE.CAMOUFLAGE:
                    if self.__bonusData[newType]['bonusTotalCount'] != newValue:
                        self.__bonusData[newType]['bonusAppliedCount'] = newValue
                elif oldElement is not None:
                    oldValue = oldElement.qualifier.getValue()
                    oldType = oldElement.qualifier.getType()
                    self.__bonusData[newType]['bonusAppliedCount'] += newValue
                    self.__bonusData[oldType]['bonusAppliedCount'] -= oldValue
                    if oldElement.qualifier.getDescription():
                        self.__bonusData[oldType]['bonusAppliedDescriptionCount'] -= 1
                else:
                    self.__bonusData[newType]['bonusAppliedCount'] += newValue
                if newElement.qualifier.getDescription():
                    self.__bonusData[newType]['bonusAppliedDescriptionCount'] += 1
        return

    def __setAnimations(self):
        for qTypeName in QUALIFIER_TYPE_NAMES.iterkeys():
            oldBonusAppliedCount = self.__bonusData[qTypeName]['oldBonusAppliedCount']
            appliedBonusValue = self.__bonusData[qTypeName]['bonusAppliedCount']
            oldBonusTotalCount = self.__bonusData[qTypeName]['oldBonusTotalCount']
            bonusTotalCount = self.__bonusData[qTypeName]['bonusTotalCount']
            formattedString = '+{0}%'
            bonusFormatter = text_styles.bonusAppliedText
            color = CUSTOMIZATION_BONUS_ANIMATION_TYPES.COLOR_GREEN
            additionalValue = ''
            descriptionFlag = ''
            if oldBonusTotalCount != bonusTotalCount:
                if self.__animationStarted:
                    animationType = CUSTOMIZATION_BONUS_ANIMATION_TYPES.BUY
                else:
                    animationType = CUSTOMIZATION_BONUS_ANIMATION_TYPES.NONE
                bonusFormatter = text_styles.bonusLocalText
                animationValue = bonusTotalCount
                if self.__bonusData[qTypeName]['bonusAppliedDescriptionCount'] != 0:
                    descriptionFlag = '*'
                if appliedBonusValue > 0:
                    additionalValue = text_styles.bonusAppliedText('+{0}%{1}'.format(appliedBonusValue, descriptionFlag))
                elif appliedBonusValue < 0:
                    additionalValue = text_styles.error('{0}%{1}'.format(appliedBonusValue, descriptionFlag))
                if self.__bonusData[qTypeName]['bonusTotalDescriptionCount'] != 0:
                    formattedString += '*'
            elif appliedBonusValue == oldBonusAppliedCount:
                animationType = CUSTOMIZATION_BONUS_ANIMATION_TYPES.NONE
                bonusFormatter = text_styles.bonusLocalText
                animationValue = bonusTotalCount
                if self.__bonusData[qTypeName]['bonusAppliedDescriptionCount'] != 0:
                    descriptionFlag = '*'
                if appliedBonusValue > 0:
                    additionalValue = text_styles.bonusAppliedText('+{0}%{1}'.format(appliedBonusValue, descriptionFlag))
                elif appliedBonusValue < 0:
                    additionalValue = text_styles.error('{0}%{1}'.format(appliedBonusValue, descriptionFlag))
                if self.__bonusData[qTypeName]['bonusTotalDescriptionCount'] != 0:
                    formattedString += '*'
            elif appliedBonusValue == 0:
                if oldBonusAppliedCount < 0:
                    formattedString = '{0}%'
                    bonusFormatter = text_styles.error
                    color = CUSTOMIZATION_BONUS_ANIMATION_TYPES.COLOR_RED
                animationType = CUSTOMIZATION_BONUS_ANIMATION_TYPES.RESET
                animationValue = oldBonusAppliedCount
                if self.__bonusData[qTypeName]['bonusAppliedDescriptionCount'] != 0:
                    formattedString += '*'
            else:
                if appliedBonusValue < 0:
                    formattedString = '{0}%'
                    bonusFormatter = text_styles.error
                    color = CUSTOMIZATION_BONUS_ANIMATION_TYPES.COLOR_RED
                animationType = CUSTOMIZATION_BONUS_ANIMATION_TYPES.SET
                animationValue = appliedBonusValue
                if self.__bonusData[qTypeName]['bonusAppliedDescriptionCount'] != 0:
                    formattedString += '*'
            self.__bonusData[qTypeName]['oldBonusAppliedCount'] = appliedBonusValue
            self.__bonusData[qTypeName]['oldBonusTotalCount'] = bonusTotalCount
            self.__bonusData[qTypeName]['animationPanel'] = {'animationType': animationType,
             'install': False,
             'color': color,
             'value1': bonusFormatter(formattedString.format(animationValue)),
             'value2': additionalValue}

        self.__animationStarted = True
        self.__processingPurchase = False
