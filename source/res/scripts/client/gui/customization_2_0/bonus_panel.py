# Embedded file name: scripts/client/gui/customization_2_0/bonus_panel.py
import copy
from Event import Event
from gui.Scaleform.genConsts.CUSTOMIZATION_BONUS_ANIMATION_TYPES import CUSTOMIZATION_BONUS_ANIMATION_TYPES
from gui.shared.formatters import text_styles
from elements.qualifier import getNameByType as _getBonusNameByType
from elements.qualifier import getIcon42x42ByType as _getBonusIcon42x42ByType
from elements.qualifier import QUALIFIER_TYPE_NAMES
from shared import forEachSlotIn
from data_aggregator import CUSTOMIZATION_TYPE
from cart import Cart

class BonusPanel(object):

    def __init__(self, aggregatedData):
        self.__animationStarted = False
        self.__aData = aggregatedData
        self.__bonusData = {}
        self.__initialSlotsData = None
        self.__initialTooltipData = None
        self.__processingPurchase = False
        self.bonusesUpdated = Event()
        Cart.purchaseProcessStarted += self.__onPurchaseProcessStarted
        return

    def fini(self):
        Cart.purchaseProcessStarted -= self.__onPurchaseProcessStarted
        self.__aData = None
        self.__bonusData = None
        self.__initialSlotsData = None
        self.__initialTooltipData = None
        return

    @property
    def bonusData(self):
        return self.__bonusData

    def setInitialSlotsData(self, iSlotsData):
        if not self.__processingPurchase:
            self.__animationStarted = False
        self.__initialSlotsData = iSlotsData
        self.__bonusData = {}
        for qTypeName in QUALIFIER_TYPE_NAMES.iterkeys():
            self.__bonusData[qTypeName] = {'bonusName': text_styles.main(_getBonusNameByType(qTypeName)),
             'bonusIcon': _getBonusIcon42x42ByType(qTypeName),
             'bonusTotalCount': 0,
             CUSTOMIZATION_TYPE.CAMOUFLAGE: [],
             CUSTOMIZATION_TYPE.EMBLEM: [],
             CUSTOMIZATION_TYPE.INSCRIPTION: [],
             'oldBonusTotalCount': 0,
             'bonusAppliedCount': 0,
             'oldBonusAppliedCount': 0,
             'bonusTotalDescriptionCount': 0,
             'bonusAppliedDescriptionCount': 0}

        forEachSlotIn(iSlotsData, iSlotsData, self.__getInitialBonusData)
        self.__saveInitialTooltipData()

    def update(self, updatedSlotsData):
        for qTypeName in QUALIFIER_TYPE_NAMES.iterkeys():
            self.__bonusData[qTypeName]['bonusAppliedCount'] = 0

        self.__restoreInitialTooltipData()
        forEachSlotIn(updatedSlotsData, self.__initialSlotsData, self.__recalculateBonusData)
        self.__setAnimations()
        self.bonusesUpdated(self.__bonusData)

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
        if newSlotItem['itemID'] > 0:
            availableItem = self.__aData.available[cType][newSlotItem['itemID']]
            installedItem = self.__aData.installed[cType][slotIdx]
            singleBonusData = self.__bonusData[availableItem.qualifier.getType()]
            if cType == CUSTOMIZATION_TYPE.CAMOUFLAGE and not singleBonusData['bonusTotalCount'] or cType != CUSTOMIZATION_TYPE.CAMOUFLAGE:
                singleBonusData['bonusTotalCount'] += availableItem.qualifier.getValue()
                if availableItem.qualifier.getDescription():
                    singleBonusData['bonusTotalDescriptionCount'] += 1
            itemData = {'isApplied': False,
             'available': availableItem,
             'installed': installedItem}
            self.__bonusData[availableItem.qualifier.getType()][cType].append(itemData)

    def __recalculateBonusData(self, newSlotItem, oldSlotItem, cType, slotIdx):
        if newSlotItem['itemID'] != oldSlotItem['itemID']:
            if newSlotItem['itemID'] > 0:
                cNewItem = self.__aData.available[cType][newSlotItem['itemID']]
                cInstalledNewItem = self.__aData.installed[cType][slotIdx]
                itemData = {'isApplied': newSlotItem['itemID'] != oldSlotItem['itemID'],
                 'available': cNewItem,
                 'installed': cInstalledNewItem}
                self.__bonusData[cNewItem.qualifier.getType()][cType].append(itemData)
                newQualifierValue = cNewItem.qualifier.getValue()
                if cType == CUSTOMIZATION_TYPE.CAMOUFLAGE:
                    if self.__bonusData[cNewItem.qualifier.getType()]['bonusTotalCount'] != newQualifierValue:
                        self.__bonusData[cNewItem.qualifier.getType()]['bonusAppliedCount'] = newQualifierValue
                elif oldSlotItem['itemID'] > 0:
                    cOldItem = self.__aData.available[cType][oldSlotItem['itemID']]
                    self.__bonusData[cNewItem.qualifier.getType()]['bonusAppliedCount'] += newQualifierValue
                    self.__bonusData[cOldItem.qualifier.getType()]['bonusAppliedCount'] -= cOldItem.qualifier.getValue()
                    if cOldItem.qualifier.getDescription():
                        self.__bonusData[cOldItem.qualifier.getType()]['bonusAppliedDescriptionCount'] -= 1
                else:
                    self.__bonusData[cNewItem.qualifier.getType()]['bonusAppliedCount'] += newQualifierValue
                if cNewItem.qualifier.getDescription():
                    self.__bonusData[cNewItem.qualifier.getType()]['bonusAppliedDescriptionCount'] += 1

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
            if oldBonusTotalCount != bonusTotalCount:
                if self.__animationStarted:
                    animationType = CUSTOMIZATION_BONUS_ANIMATION_TYPES.BUY
                else:
                    animationType = CUSTOMIZATION_BONUS_ANIMATION_TYPES.NONE
                bonusFormatter = text_styles.bonusLocalText
                animationValue = bonusTotalCount
                if appliedBonusValue > 0:
                    additionalValue = text_styles.bonusAppliedText('+{0}%'.format(appliedBonusValue))
                elif appliedBonusValue < 0:
                    additionalValue = text_styles.error('{0}%'.format(appliedBonusValue))
                if self.__bonusData[qTypeName]['bonusTotalDescriptionCount'] != 0:
                    formattedString += '*'
            elif appliedBonusValue == oldBonusAppliedCount:
                animationType = CUSTOMIZATION_BONUS_ANIMATION_TYPES.NONE
                bonusFormatter = text_styles.bonusLocalText
                animationValue = bonusTotalCount
                if appliedBonusValue > 0:
                    additionalValue = text_styles.bonusAppliedText('+{0}%'.format(appliedBonusValue))
                elif appliedBonusValue < 0:
                    additionalValue = text_styles.error('{0}%'.format(appliedBonusValue))
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
