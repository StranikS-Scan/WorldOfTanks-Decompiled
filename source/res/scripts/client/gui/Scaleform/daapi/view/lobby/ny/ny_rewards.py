# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ny/ny_rewards.py
from adisp import process
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui import GUI_NATIONS, DialogsInterface
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta, HtmlMessageDialogMeta, DIALOG_BUTTON_ID
from gui.Scaleform.daapi.view.lobby.cyberSport.VehicleSelectorPopup import VehicleSelectorPopup
from gui.Scaleform.daapi.view.lobby.ny.ny_helper_view import NYHelperView
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleBasicVO
from gui.Scaleform.daapi.view.lobby.recruitWindow.QuestsRecruitWindow import QuestsRecruitWindow
from gui.Scaleform.daapi.view.meta.NYScreenRewardsMeta import NYScreenRewardsMeta
from gui.Scaleform.genConsts.NY_CONSTANTS import NY_CONSTANTS
from gui.Scaleform.genConsts.VEHICLE_SELECTOR_CONSTANTS import VEHICLE_SELECTOR_CONSTANTS
from gui.Scaleform.locale.NY import NY
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.server_events.awards_formatters import QuestsBonusComposer
from gui.server_events.bonuses import VehiclesBonus
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME as _VCN
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from helpers.i18n import makeString as _ms
from items import tankmen
from nations import INDICES
from new_year.new_year_sounds import NYSoundEvents
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
_CONST_INIT_DATA = {'title': NY.REWARDSSCREEN_TITLE,
 'rewards': None}
_BONUS_FORMATTER = QuestsBonusComposer()

class NYRewards(NYHelperView, NYScreenRewardsMeta):
    _eventsCache = dependency.descriptor(IEventsCache)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None):
        super(NYRewards, self).__init__(ctx)
        ctx = ctx or {}
        self.__backAlias = ctx['previewAlias'] if 'previewAlias' in ctx else VIEW_ALIAS.LOBBY_NY_SCREEN
        self.__nyMaxLevel = None
        self.__nyLevel = None
        return

    def onClose(self):
        if self.__backAlias == VIEW_ALIAS.LOBBY_NY_SCREEN:
            self._switchToNYMain(previewAlias=VIEW_ALIAS.LOBBY_NY_REWARDS)
        else:
            self.fireEvent(events.LoadViewEvent(self.__backAlias), scope=EVENT_BUS_SCOPE.LOBBY)

    def onRecruitClick(self, level):
        vdIdByLvl = self.__getTmanDiscountIDByLvl(level)
        if vdIdByLvl is not None:
            from gui.shared import g_eventBus
            g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.NY_RECRUIT_WINDOW, ctx={'questID': vdIdByLvl}), EVENT_BUS_SCOPE.LOBBY)
        else:
            LOG_ERROR('Varidaic tankman ID for disired level "level" has not been found!'.format(level))
        return

    def onDiscountApplyClick(self, level, vehicleLevel, discount):
        level = int(level)
        LOG_DEBUG('onDiscountApplyClick', vehicleLevel, discount)
        discount = '{}%'.format(discount)
        infoText = _ms(NY.APPLYDISCOUNT_INFOTEXT, discount=discount, level=vehicleLevel)
        vehDiscounts = self._newYearController.vehDiscountsStorage.getClientDiscountsCache()[level - 1]
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.NY_APPLY_DISCOUNT_FILTER, ctx={'isMultiSelect': False,
         'infoText': infoText,
         'titleText': NY.APPLYDISCOUNT_TITLE,
         'selectButton': NY.APPLYDISCOUNT_BUTTONS_SELECT,
         'cancelButton': NY.APPLYDISCOUNT_BUTTONS_CANCEL,
         'compatibleOnlyLabel': NY.APPLYDISCOUNT_COMPATIBLECHECKBOX_LABEL,
         'variadicDiscountID': self.__getVariadicDiscountIdByLvl(level),
         'discountData': dict(((descr.target.targetValue, (dID, descr.resource.value)) for dID, descr in vehDiscounts.iteritems())),
         'section': 'ny_vehicle_discount_activation',
         'vehicleTypes': (_VCN.LIGHT_TANK, _VCN.MEDIUM_TANK, _VCN.HEAVY_TANK),
         'filterVisibility': VEHICLE_SELECTOR_CONSTANTS.VISIBLE_NATION | VEHICLE_SELECTOR_CONSTANTS.VISIBLE_VEHICLE_TYPE | VEHICLE_SELECTOR_CONSTANTS.VISIBLE_COMPATIBLE_ONLY}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _populate(self):
        super(NYRewards, self)._populate()
        self.__nyLevel, self.__nyMaxLevel, _, _ = self._newYearController.getProgress()
        self.__updateData()
        NYSoundEvents.playSound(NYSoundEvents.ON_OPEN_REWARDS)
        NYSoundEvents.setState(NYSoundEvents.STATE_ON_REWARDS)
        self._newYearController.onProgressChanged += self.__onNYProgressChanged
        self._newYearController.vehDiscountsStorage.onUpdated += self.__onStoragesUpdated
        self._newYearController.tankmanDiscountsStorage.onUpdated += self.__onStoragesUpdated

    def _dispose(self):
        NYSoundEvents.playSound(NYSoundEvents.ON_CLOSE_REWARDS)
        self._newYearController.onProgressChanged -= self.__onNYProgressChanged
        self._newYearController.vehDiscountsStorage.onUpdated -= self.__onStoragesUpdated
        self._newYearController.tankmanDiscountsStorage.onUpdated -= self.__onStoragesUpdated
        super(NYRewards, self)._dispose()

    def __onStoragesUpdated(self):
        self.__updateData()

    def __onNYProgressChanged(self, progress):
        if self.__nyMaxLevel != progress.maxLevel or self.__nyLevel != progress.level:
            self.__nyMaxLevel = progress.maxLevel
            self.__nyLevel = progress.level
            self.__updateData()

    def __updateData(self):
        _CONST_INIT_DATA['rewards'] = self.__getRewardsVO()
        self.as_initS(_CONST_INIT_DATA)

    def __getTankWoman(self, level, isChestOpened):
        idByLevel = self.__getTmanDiscountIDByLvl(level)
        if idByLevel is None:
            return
        else:
            if self._newYearController.tankmanDiscountsStorage.getDiscounts().get(idByLevel, 0) > 0 or not isChestOpened:
                tankWoman = {'isRecruited': False,
                 'icon': RES_ICONS.MAPS_ICONS_NY_REWARDS_ICON_GIRL_107X80,
                 'id': None}
            elif level > self.__nyMaxLevel:
                tankWoman = {'isRecruited': False,
                 'icon': RES_ICONS.MAPS_ICONS_NY_REWARDS_ICON_GIRL_107X80,
                 'id': None}
            else:
                tMan = self._newYearController.tankmanDiscountsStorage.getRecruitedTankmen(level)
                if tMan:
                    tankWoman = {'isRecruited': True,
                     'icon': '../maps/icons/tankmen/icons/big/{}'.format(tMan.icon),
                     'id': tMan.invID}
                else:
                    tankWoman = {'isRecruited': True,
                     'icon': RES_ICONS.MAPS_ICONS_NY_REWARDS_ICON_GIRL_107X80,
                     'id': None}
            tankWoman.update({'available': isChestOpened})
            return tankWoman

    def __getRewardsVO(self):
        rewards = []
        chests_decrs = sorted(self._newYearController.chestStorage.getDescriptors().itervalues(), key=lambda v: v.level)
        hidden_quests = self._eventsCache.getHiddenQuests()
        for chestDescr in chests_decrs:
            quest_id = chestDescr.id
            hasChests = self._newYearController.chestStorage.hasItem(chestDescr.id)
            nyQuest = hidden_quests.get(quest_id, None)
            if nyQuest is None:
                LOG_ERROR('Quest "{}" has not been found!'.format(quest_id))
                return []
            lvl = chestDescr.level
            bonuses = nyQuest.getBonuses()
            state = self.__getStateByLevel(lvl)
            isLevelMax = lvl == self.__nyMaxLevel
            vehicleName = ''
            tankIcon = ''
            vehicleUnknown = False
            tooltipBody = ''
            tooltipHeader = ''
            vehicleLevel = _ms(TOOLTIPS.level(lvl))
            vehDiscountStatus = NY_CONSTANTS.NY_VEHICLE_DISCOUNT_NOT_AVAILABLE
            vehDiscount = self._newYearController.vehDiscountsStorage.extractDiscountValueByLevel(lvl)
            if lvl == 1:
                vehDiscountStatus = NY_CONSTANTS.NY_VEHICLE_DISCOUNT_AVAILABLE if hasChests else NY_CONSTANTS.NY_VEHICLE_DISCOUNT_APPLIED
                for idx, bonus in enumerate(bonuses):
                    if isinstance(bonus, VehiclesBonus):
                        vehicle = bonus.getVehicles()[0][0]
                        vehicleName = vehicle.shortUserName
                        vehicleLevel = _ms(TOOLTIPS.level(vehicle.level))
                        tankIcon = vehicle.icon
                        tooltipHeader = _ms(NY.REWARDSSCREEN_TOOLTIP_GIFT_VEHICLE_HEADER)
                        tooltipBody = _ms(NY.REWARDSSCREEN_TOOLTIP_GIFT_VEHICLE_BODY, name=vehicleName, level=vehicleLevel)
                        bonuses.pop(idx)
                        break

            else:
                if vehDiscount is not None:
                    hasVehicleDiscounts = self._newYearController.vehDiscountsStorage.getDiscounts().get(self.__getVariadicDiscountIdByLvl(lvl), 0) > 0
                    levelAchieved = state != NY_CONSTANTS.REWARDS_LEVEL_NEXT
                    if levelAchieved:
                        vehDiscountStatus = self.__getVehicleDiscountStatus(hasChests, hasVehicleDiscounts)
                    tankDiscountApplied = levelAchieved and not hasVehicleDiscounts and not hasChests
                    if tankDiscountApplied:
                        discountVehicle = self.__getPersonalDiscountVehicle(self._newYearController.vehDiscountsStorage.getClientDiscountsCache()[lvl - 1])
                        if discountVehicle is not None:
                            vehicleName = discountVehicle.shortUserName
                            tankIcon = discountVehicle.icon
                        else:
                            discountVehicle = self._newYearController.vehDiscountsStorage.getBoughtVehicle(lvl - 1)
                            if discountVehicle:
                                vehicleName = discountVehicle.shortUserName
                                tankIcon = discountVehicle.icon
                            else:
                                tankIcon = RES_ICONS.MAPS_ICONS_NY_REWARDS_NY_REWARD_UNKNOWN_TANK
                                vehicleUnknown = True
                    else:
                        tankIcon = RES_ICONS.MAPS_ICONS_NY_REWARDS_NY_REWARD_UNKNOWN_TANK
                else:
                    tankDiscountApplied = True
                    vehDiscountStatus = NY_CONSTANTS.NY_VEHICLE_DISCOUNT_APPLIED
                if tankDiscountApplied:
                    if vehicleUnknown:
                        tooltipBody = _ms(NY.REWARDSSCREEN_TOOLTIP_VEHICLEUNKNOWN_APPLIED_BODY, discount=vehDiscount)
                    else:
                        tooltipBody = _ms(NY.REWARDSSCREEN_TOOLTIP_VEHICLE_APPLIED_BODY, discount=vehDiscount, name=vehicleName)
                else:
                    tooltipBody = _ms(NY.REWARDSSCREEN_TOOLTIP_VEHICLE_BODY, discount=vehDiscount, level=vehicleLevel)
                tooltipHeader = _ms(NY.REWARDSSCREEN_TOOLTIP_VEHICLE_HEADER, level=vehicleLevel)
            data = {'state': state,
             'level': lvl,
             'levelStr': NY.atmosphere_level(lvl),
             'isLevelMax': isLevelMax,
             'vehicleLevel': vehicleLevel,
             'vehicleName': vehicleName,
             'discount': vehDiscount,
             'tankIcon': tankIcon,
             'vehDiscountStatus': vehDiscountStatus,
             'tankWoman': self.__getTankWoman(lvl, not hasChests),
             'bonuses': _BONUS_FORMATTER.getFormattedBonuses(bonuses),
             'tooltip': makeTooltip(tooltipHeader, tooltipBody)}
            rewards.append(data)

        return rewards

    def __getStateByLevel(self, level):
        if level == self.__nyLevel:
            return NY_CONSTANTS.REWARDS_LEVEL_CURRENT
        return NY_CONSTANTS.REWARDS_LEVEL_RECEIVED if level <= self.__nyMaxLevel else NY_CONSTANTS.REWARDS_LEVEL_NEXT

    def __getVehicleDiscountStatus(self, hasChests, hasVehicleDiscounts):
        if hasChests:
            return NY_CONSTANTS.NY_VEHICLE_DISCOUNT_AVAILABLE
        return NY_CONSTANTS.NY_VEHICLE_DISCOUNT_RECEIVED if hasVehicleDiscounts else NY_CONSTANTS.NY_VEHICLE_DISCOUNT_APPLIED

    def __getVariadicDiscountIdByLvl(self, level):
        return self._newYearController.vehDiscountsStorage.extractDiscountIDByLvl(level)

    def __getPersonalDiscountVehicle(self, availableDiscounts):
        accountDiscounts = self._itemsCache.items.shop.personalVehicleDiscounts
        for dId, dData in availableDiscounts.iteritems():
            if dId in accountDiscounts:
                return self._itemsCache.items.getItemByCD(typeCompDescr=dData.target.targetValue)

        return None

    def __getTmanDiscountIDByLvl(self, level):
        descrs = self._newYearController.tankmanDiscountsStorage.getDescriptors()
        for d in descrs.itervalues():
            if d.level == level:
                return d.id

        return None


class NYApplyDiscountOnVehiclePopup(VehicleSelectorPopup):
    _newYearController = dependency.descriptor(INewYearController)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None):
        super(NYApplyDiscountOnVehiclePopup, self).__init__(ctx)
        self.__discountData = ctx.get('discountData', {})
        self.__variadicDiscountID = ctx.get('variadicDiscountID')
        self.__allVehicles = self._itemsCache.items.getVehicles(REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD(self.__discountData.keys()))
        self.__allVehicles = self.__allVehicles.filter(~REQ_CRITERIA.INVENTORY)

    def initFilters(self):
        filters = self._initFilter(nation=-1, vehicleType='none', isMain=False, level=-1, compatibleOnly=False)
        self._updateFilter(filters['nation'], filters['vehicleType'], filters['isMain'], filters['level'], filters['compatibleOnly'])
        self.as_setFiltersDataS(filters)
        return filters

    def updateData(self):
        super(NYApplyDiscountOnVehiclePopup, self).updateData()
        if self.getFilters().get('compatibleOnly', True):
            vehicleVOs = self._updateData(self.__allVehicles.filter(REQ_CRITERIA.UNLOCKED))
        else:
            vehicleVOs = self._updateData(self.__allVehicles)
        self.as_setListDataS(vehicleVOs, None)
        return

    @process
    def onSelectVehicles(self, items):
        vehIntCD = int(items[0])
        vehicle = self._itemsCache.items.getItemByCD(typeCompDescr=vehIntCD)
        discountID, discountVal = self.__discountData[vehIntCD]
        vehicleName = vehicle.userName
        ctx = {'discount': discountVal,
         'vehicleName': vehicleName,
         'vehicleType': vehicle.type}
        is_ok = yield DialogsInterface.showDialog(meta=I18nConfirmDialogMeta('confirmApplyVehicleDiscount', ctx, ctx, meta=HtmlMessageDialogMeta('html_templates:newYear/dialogs', 'confirmVehDiscount', ctx, sourceKey='text'), focusedID=DIALOG_BUTTON_ID.SUBMIT))
        if is_ok:
            self._newYearController.vehDiscountsStorage.activateVehicleDiscount(discountID, self.__variadicDiscountID, vehicleName, vehIntCD, discountVal)
            self.onWindowClose()

    def _populate(self):
        super(NYApplyDiscountOnVehiclePopup, self)._populate()
        self._newYearController.onStateChanged += self.__onNyStateChanged

    def _dispose(self):
        self._newYearController.onStateChanged -= self.__onNyStateChanged
        super(NYApplyDiscountOnVehiclePopup, self)._dispose()

    def _makeVehicleVOAction(self, vehicle):
        return makeVehicleBasicVO(vehicle)

    def __onNyStateChanged(self, _):
        if not self._newYearController.isAvailable():
            self.destroy()


class NYRecruitWindow(QuestsRecruitWindow):
    _newYearController = dependency.descriptor(INewYearController)

    def __init__(self, ctx=None):
        ctx = ctx or {}
        self.__selNationID = 0
        self.__selFnameID = 1
        self.__selLnameID = 1
        self.__selIconID = 1
        nationIntId = INDICES[GUI_NATIONS[0]]
        firstNameID, lastNameID, iconID = self._getTankmanData(nationIntId)
        ctx.update({'isPremium': True,
         'fnGroup': firstNameID,
         'lnGroup': lastNameID,
         'iGroupID': iconID})
        super(NYRecruitWindow, self).__init__(ctx)
        self.__vdTankmanDescountID = ctx['questID']

    def onApply(self, data):
        self._newYearController.tankmanDiscountsStorage.reqruitTankmen(int(data.nation), int(data.vehicle), tankmen.SKILL_INDICES[data.tankmanRole], self.__vdTankmanDescountID)
        self.destroy()

    def _populate(self):
        super(NYRecruitWindow, self)._populate()
        self._newYearController.onStateChanged += self.__onNyStateChanged
        self._newYearController.tankmanDiscountsStorage.onTankmanChoicesChanged += self.__onTankmanChoicesChanged

    def _dispose(self):
        self._newYearController.onStateChanged -= self.__onNyStateChanged
        self._newYearController.tankmanDiscountsStorage.onTankmanChoicesChanged -= self.__onTankmanChoicesChanged
        super(NYRecruitWindow, self)._dispose()

    def __onNyStateChanged(self, _):
        if not self._newYearController.isAvailable():
            self.destroy()

    def __onTankmanChoicesChanged(self, _):
        newPassportData = self._newYearController.tankmanDiscountsStorage.getTankmanNextChoices(self.__selNationID)
        if newPassportData.firstNameID != self.__selFnameID or newPassportData.lastNameID != self.__selLnameID or newPassportData.iconID != self.__selIconID:
            self._paramsChangeHandler(self.__selNationID, None, None, None)
        return

    def _getTankmanData(self, nationID):
        tPassportData = self._newYearController.tankmanDiscountsStorage.getTankmanNextChoices(nationID)
        self.__selNationID = nationID
        self.__selFnameID = tPassportData.firstNameID
        self.__selLnameID = tPassportData.lastNameID
        self.__selIconID = tPassportData.iconID
        return (self.__selFnameID, self.__selLnameID, self.__selIconID)
