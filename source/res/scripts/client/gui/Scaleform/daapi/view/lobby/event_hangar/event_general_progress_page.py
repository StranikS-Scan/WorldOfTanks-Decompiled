# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_hangar/event_general_progress_page.py
from gui import makeHtmlString
from gui.Scaleform.daapi.view.meta.EventGeneralProgressMeta import EventGeneralProgressMeta
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.EVENT import EVENT
from helpers import dependency, int2roman
from gui.Scaleform.daapi import LobbySubView
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
from gui.shared import event_dispatcher
from skeletons.gui.game_event_controller import IGameEventController
from gui.shared.money import Currency, Money
from gui.server_events.awards_formatters import AWARDS_SIZES, getEventAwardFormatter
from gui.Scaleform.daapi.view.lobby.event_hangar.vo_converters import makeAbbilityVO
from gui.shared.gui_items.Vehicle import getTypeSmallIconPath, getLevelIconPath, getContourIconPath
from helpers.i18n import makeString as _ms
from gui.shared.formatters.currency import getBWFormatter
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.gui_items.processors import plugins
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared import events, EVENT_BUS_SCOPE
_MAX_PROGRESS_BAR_VALUE = 100.0
_EMPTY_BONUS_LABEL = 'x1'

class EventGeneralProgressPage(LobbySubView, EventGeneralProgressMeta):
    __background_alpha__ = 0
    gameEventController = dependency.descriptor(IGameEventController)
    itemsCache = dependency.descriptor(IItemsCache)
    service = dependency.descriptor(ICustomizationService)

    def __init__(self, ctx=None, *args, **kwargs):
        super(EventGeneralProgressPage, self).__init__(*args, **kwargs)
        self._general = None
        self._ctx = ctx
        self._availableGeneralIDs = None
        return

    def specialOfferClick(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.EVENT_GENERAL_DIALOG, ctx={'generalId': self._general.getID()}), scope=EVENT_BUS_SCOPE.LOBBY)

    def closeView(self):
        event_dispatcher.showHangar()

    def changeGeneral(self, index):
        generals = self.gameEventController.getGenerals()
        nextGeneralID = index
        self._setGeneral(generals[nextGeneralID])

    def _populate(self):
        super(EventGeneralProgressPage, self)._populate()
        if self._ctx is not None and 'generalId' in self._ctx:
            generalId = self._ctx.get('generalId')
        else:
            generalId = self.gameEventController.getSelectedGeneralID()
        self._availableGeneralIDs = self.gameEventController.getGenerals().keys()
        self._setGeneral(self.gameEventController.getGeneral(generalId))
        return

    def _dispose(self):
        self._setGeneral(None)
        self.service.destroyCtx()
        super(EventGeneralProgressPage, self)._dispose()
        return

    def _setGeneral(self, general):
        if self._general:
            self._general.onItemsUpdated -= self._updateData
            self._general = None
        self._general = general
        if self._general is None:
            return
        else:
            self._general.onItemsUpdated += self._updateData
            self._updateData()
            self.as_selectSectionS(self._availableGeneralIDs.index(general.getID()))
            return

    def _createVehicleVO(self, typeCompDescr):
        vehicle = self.itemsCache.items.getStockVehicle(typeCompDescr, useInventory=True)
        return {'intCD': vehicle.intCD,
         'vehicleName': vehicle.shortUserName,
         'vehicleTypeIcon': getTypeSmallIconPath(vehicle.type),
         'levelIcon': getLevelIconPath(vehicle.level),
         'vehicleIcon': getContourIconPath(vehicle.name)}

    def _updateData(self):
        generalLevels = [ self._makeGeneralVO(self._general, level) for level in xrange(len(self._general.items)) ]
        frontID = self._general.getFrontID()
        generalID = self._general.getID()
        currentProgress = self._general.getCurrentProgress()
        sections = [ {'id': 'faction{}'.format(availableGeneralID)} for availableGeneralID in self._availableGeneralIDs ]
        self.as_setDataS({'about': self._getGeneralAboutData(self._general),
         'levels': generalLevels,
         'sections': sections,
         'bonus': self._getGeneralBonusData(self._general),
         'background': RES_ICONS.getGeneralProgressBackground(generalID),
         'backgroundSmall': RES_ICONS.getGeneralProgressBackgroundSmall(generalID),
         'icon': RES_ICONS.getGeneralLogo(generalID, self._general.getCurrentProgressLevel()),
         'name': EVENT.getGeneralProgressName(generalID),
         'frontName': EVENT.getFrontName(frontID),
         'currentProgress': currentProgress,
         'currentProgressPercent': self._getCurrentProgressPercent(self._general),
         'progressHeader': EVENT.getGeneralProgressLevelsHeader(generalID),
         'level': self._general.getCurrentProgressLevel(),
         'levelIcon': RES_ICONS.getGeneralLevelIcon(self._general.getCurrentProgressLevel()),
         'abilitiesHeader': EVENT.getGeneralProgressAbilitiesHeader(generalID),
         'skills': self._makeSkillsVO(self._general),
         'tooltip': '',
         'specialArgs': [generalID],
         'specialAlias': TOOLTIPS_CONSTANTS.EVENT_GENERAL_PROGRESSION,
         'isSpecial': True})

    def _makeSkillsVO(self, general):
        abilities = [ {'levelsCount': len(levels),
         'name': name} for name, levels in self._getAbilitiesByLevelCount(self._general).iteritems() ]
        abilities.sort(key=lambda ability: ability['levelsCount'], reverse=True)
        return [ self._makeSkillVO(ability['name']) for ability in abilities ]

    def _makeSkillVO(self, abilityName):
        return {'icon': RES_ICONS.getGeneralAbilityIconInHangar(abilityName),
         'label': EVENT.getAbilityName(abilityName),
         'description': EVENT.getAbilityLongDescription(abilityName)}

    def _makeGeneralVO(self, general, level):
        selectedGeneral = self._general
        currency, amount = general.getCurrentCostForLevel(level)
        cost = self._getGeneralCostFormatted(currency, amount)
        canBuy = False
        isCompleted = general.items[level].isCompleted()
        if currency and not isCompleted:
            canBuy = plugins.MoneyValidator(Money(**{currency: amount})).validate().success
        return {'id': general.getID(),
         'label': _ms(EVENT.PROGRESS_LEVEL_NAME, level=int2roman(self.getLevelForUI(level))),
         'maxProgress': general.getTotalProgressForLevel(level),
         'cost': cost,
         'status': _ms(EVENT.PROGRESS_GET_LEVEL, level=int2roman(self.getLevelForUI(level))),
         'reached': isCompleted,
         'buyEnabled': not isCompleted and cost is not None,
         'canBuy': canBuy,
         'isGold': currency == Currency.GOLD,
         'level': level,
         'rank': {'level': level,
                  'tanks': [ self._createVehicleVO(typeCompDescr) for typeCompDescr in selectedGeneral.getVehiclesByLevel(level) ],
                  'items': [ makeAbbilityVO(abilityID, emptyLabel=True, isHangar=True) for abilityID in selectedGeneral.getAbilitiesByLevel(level) ]}}

    def _getAbilitiesByLevelCount(self, general):
        abilities = {}
        for level in xrange(general.getMaxLevel() + 1):
            for abilityID in general.getAbilitiesByLevel(level):
                abilities.setdefault(general.getAbilityBaseName(abilityID), []).append(level)

        return abilities

    def _getGeneralAboutData(self, general):
        return {'sections': self.gameEventController.getGeneralsHistoryInfo().getInfoFor(general.getID()),
         'background': RES_ICONS.MAPS_ICONS_EVENT_PROGRESS_GENERALPROGRESSHISTORYCOMMONBG1,
         'header': EVENT.getGeneralProgressHistoryHeader(general.getID())}

    def _getGeneralBonusData(self, general):
        bonusData = []
        for level in xrange(general.getMaxLevel() + 1):
            item = general.items[level]
            rewards = [ {'icon': bonus.images[AWARDS_SIZES.SMALL],
             'overlayType': bonus.overlayType.get(AWARDS_SIZES.SMALL, '') if bonus.overlayType else '',
             'label': bonus.label or _EMPTY_BONUS_LABEL,
             'tooltip': bonus.tooltip,
             'specialArgs': bonus.specialArgs,
             'specialAlias': bonus.specialAlias,
             'isSpecial': bonus.isSpecial} for bonus in getEventAwardFormatter().format(item.getBonuses()) ]
            bonusData.append({'header': _ms(EVENT.PROGRESS_LEVEL_NAME, level=int2roman(self.getLevelForUI(level))),
             'level': level,
             'rewardTaken': general.getCurrentProgressLevel() >= level,
             'rewards': rewards})

        description = makeHtmlString('html_templates:lobby/textStyle/', 'eventGeneralLevelDescription', {'highlighted': _ms(EVENT.PROGRESS_LEVEL_DESCRIPTION_HIGHLIGHTED),
         'ordinary': _ms(EVENT.PROGRESS_LEVEL_DESCRIPTION_ORDINARY)})
        return {'bonus': bonusData,
         'description': description}

    def _getGeneralCostFormatted(self, currency, amount):
        return None if currency is None or amount is None else getBWFormatter(currency)(amount)

    def _getCurrentProgressPercent(self, general):
        generalMaxLevel = general.getMaxLevel()
        if generalMaxLevel < 1:
            return _MAX_PROGRESS_BAR_VALUE
        generalLevel = general.getCurrentProgressLevel()
        curProgress = general.getCurrentProgress()
        curTotalProgress = general.getTotalProgressForLevel(generalLevel)
        nextTotalProgress = general.getTotalProgressForLevel(min(generalMaxLevel, generalLevel + 1))
        percentagePerLevel = _MAX_PROGRESS_BAR_VALUE / generalMaxLevel
        curLevelPercentage = percentagePerLevel * generalLevel
        difBeetweenLevels = nextTotalProgress - curTotalProgress
        if difBeetweenLevels > 0:
            currentPercentage = percentagePerLevel * (curProgress - curTotalProgress) / difBeetweenLevels
            return min(curLevelPercentage + currentPercentage, _MAX_PROGRESS_BAR_VALUE)
        return _MAX_PROGRESS_BAR_VALUE

    def getLevelForUI(self, level):
        return level + 1
