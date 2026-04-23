# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/customization_style_info/customization_style_info_view.py
from CurrentVehicle import g_currentVehicle
from frameworks.wulf import ViewSettings
from gui.customization.shared import C11nId
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.customization.customization_style_availability_model import CustomizationStyleAvailabilityModel
from gui.impl.gen.view_models.views.lobby.customization.customization_style_info_view_model import CustomizationStyleInfoViewModel
from gui.impl.gen.view_models.views.lobby.customization.customization_style_parameter_model import CustomizationStyleParameterModel
from gui.impl.lobby.customization.customization_bill_data_packer import fillBaseBillData
from gui.impl.lobby.customization.customization_style_info.style_info_helper import getSuitable, TAG_TO_PO_NAME, Parameters
from gui.impl.pub import ViewImpl
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from items.components.c11n_constants import SeasonType, CustomizationDisplayType
from skeletons.gui.customization import ICustomizationService
from vehicle_outfit.outfit import Area

class CustomizationStyleInfoView(ViewImpl):
    __slots__ = ('__ctx', '__c11nView', '__prevStyle', '__selectedStyle')
    __service = dependency.descriptor(ICustomizationService)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.customization.CustomizationStyleInfoView())
        settings.model = CustomizationStyleInfoViewModel()
        self.__ctx = None
        self.__prevStyle = None
        self.__selectedStyle = None
        super(CustomizationStyleInfoView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(CustomizationStyleInfoView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        self.__ctx = self.__service.getCtx()
        super(CustomizationStyleInfoView, self)._onLoading(*args, **kwargs)

    def _getEvents(self):
        return ((self.viewModel.onShowBuyWindow, self.__onShowBuyWindow), (self.__ctx.events.onShowStyleInfo, self.__onShowStyleInfo), (self.__ctx.events.onHideStyleInfo, self.__onClose))

    def __onShowStyleInfo(self, style=None):
        self.__prevStyle = self.__ctx.mode.modifiedStyle
        self.__selectedStyle = style or self.__ctx.mode.modifiedStyle
        if self.__selectedStyle is None:
            return
        else:
            if self.__prevStyle is None or self.__selectedStyle != self.__prevStyle:
                self.__installStyle(self.__selectedStyle)
            self.__fillModel()
            return

    def __fillModel(self):
        styleParams = self.__makeParams(self.__selectedStyle)
        styleName = self.__selectedStyle.userName
        styleInfo = self.__selectedStyle.longDescriptionSpecial
        suitableList = getSuitable(self.__selectedStyle, g_currentVehicle.item)
        with self.viewModel.transaction() as model:
            model.setStyleName(styleName)
            model.setStyleInfo(styleInfo)
            paramsList = model.getParameters()
            paramsList.clear()
            for param in styleParams:
                parameter = CustomizationStyleParameterModel()
                parameter.setPoId(param.get(Parameters.PO_ID, ''))
                parameter.setIcon(param.get(Parameters.ICON, ''))
                parameter.setValue(param.get(Parameters.VALUE, ''))
                paramsList.addViewModel(parameter)

            paramsList.invalidate()
            availableList = model.getAvailabilityList()
            availableList.clear()
            for condition in suitableList:
                availabilityModel = CustomizationStyleAvailabilityModel()
                availabilityModel.setTankNames(condition.get('tankNames', ''))
                availabilityModel.setIsPremium(condition.get('isPremium', False))
                availabilityModel.setIsPremiumIGR(condition.get('isPremiumIGR', False))
                nationsList = availabilityModel.getNations()
                levelsList = availabilityModel.getLevels()
                vehTypesList = availabilityModel.getVehTypes()
                nationsList.clear()
                levelsList.clear()
                vehTypesList.clear()
                for nation in condition.get('nations') or ():
                    nationsList.addString(nation)

                for level in condition.get('levels') or ():
                    levelsList.addString(level)

                for vehType in condition.get('vehType') or ():
                    vehTypesList.addString(vehType)

                nationsList.invalidate()
                levelsList.invalidate()
                vehTypesList.invalidate()
                availableList.addViewModel(availabilityModel)

            availableList.invalidate()
            fillBaseBillData(model.billData, ctx=self.__ctx)

    def __makeParams(self, style):
        params = []
        vehicleCD = g_currentVehicle.item.descriptor.makeCompactDescr()
        for season in SeasonType.COMMON_SEASONS:
            outfit = style.getOutfit(season, vehicleCD=vehicleCD)
            if not outfit:
                continue
            container = outfit.hull
            intCD = container.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).getItemCD()
            if not intCD:
                continue
            camo = self.__service.getItemByCD(intCD)
            if not camo or not camo.bonus:
                continue
            bonus = '+' + camo.bonus.getFormattedValue(g_currentVehicle.item)
            bonusId = TAG_TO_PO_NAME['bonus']
            bonusIcon = backport.image(R.images.gui.maps.icons.customization.style_info.bonus())
            params.append({Parameters.ICON: bonusIcon,
             Parameters.PO_ID: bonusId,
             Parameters.VALUE: bonus})
            break

        displayType = style.customizationDisplayType()
        iconMap = {CustomizationDisplayType.HISTORICAL: R.images.gui.maps.icons.customization.style_info.historical(),
         CustomizationDisplayType.NON_HISTORICAL: R.images.gui.maps.icons.customization.style_info.nonhistorical(),
         CustomizationDisplayType.FANTASTICAL: R.images.gui.maps.icons.customization.style_info.fantastical()}
        historicIcon = backport.image(iconMap[displayType])
        historicId = TAG_TO_PO_NAME[displayType]
        params.append({Parameters.ICON: historicIcon,
         Parameters.PO_ID: historicId})
        if style.isRentable:
            rentIcon = backport.image(R.images.gui.maps.icons.customization.style_info.rentable())
            rentId = TAG_TO_PO_NAME['rentable']
            params.append({Parameters.ICON: rentIcon,
             Parameters.PO_ID: rentId})
        if style.specialEventTag is not None:
            eventIcon = style.specialEventIcon
            eventId = TAG_TO_PO_NAME[style.specialEventTag]
            params.append({Parameters.ICON: eventIcon,
             Parameters.PO_ID: eventId})
        return params

    def __installStyle(self, style):
        slotId = C11nId(areaId=Area.MISC, slotType=GUI_ITEM_TYPE.STYLE, regionIdx=0)
        self.__ctx.mode.installItem(style.intCD, slotId)

    def __onClose(self):
        self.__selectedStyle = None
        if self.__prevStyle is None:
            slotId = C11nId(areaId=Area.MISC, slotType=GUI_ITEM_TYPE.STYLE, regionIdx=0)
            self.__ctx.mode.removeItem(slotId)
        elif self.__prevStyle != self.__ctx.mode.modifiedStyle:
            self.__installStyle(self.__prevStyle)
        self.__prevStyle = None
        return

    def __onShowBuyWindow(self):
        mainView = self.getParentView()
        if mainView:
            mainView.onCloseStyleInfo(needToRevertStyle=False)
            mainView.showBuyWindow()
