# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ModuleInfoWindow.py
from gui.Scaleform.daapi.view.meta.ModuleInfoMeta import ModuleInfoMeta
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.locale.MENU import MENU
from gui.shared.formatters import text_styles
from gui.shared.items_parameters import params_helper, formatters
from gui.shared.utils import GUN_RELOADING_TYPE, GUN_CAN_BE_CLIP, GUN_CLIP, CLIP_ICON_PATH, EXTRA_MODULE_INFO, HYDRAULIC_ICON_PATH
from gui.Scaleform.genConsts.SLOT_HIGHLIGHT_TYPES import SLOT_HIGHLIGHT_TYPES
from gui.shared.utils.functions import stripShortDescrTags, stripColorTagDescrTags
from helpers import dependency
from helpers import i18n
from gui.shared.gui_items import GUI_ITEM_TYPE
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_DEF_SHOT_DISTANCE = 720

class ModuleInfoWindow(ModuleInfoMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, ctx=None):
        super(ModuleInfoWindow, self).__init__()
        self.moduleCompactDescr = ctx.get('moduleCompactDescr')
        assert self.moduleCompactDescr, 'module compact descriptor must be defined'
        self.__vehicleDescr = ctx.get('vehicleDescr')
        self.__isAdditionalInfoShow = ctx.get('isAdditionalInfoShow')

    def onCancelClick(self):
        self.destroy()

    def onActionButtonClick(self):
        pass

    def onWindowClose(self):
        self.destroy()

    def _populate(self):
        super(View, self)._populate()
        module = self.itemsCache.items.getItemByCD(self.moduleCompactDescr)
        description = ''
        if module.itemTypeID in (GUI_ITEM_TYPE.OPTIONALDEVICE, GUI_ITEM_TYPE.EQUIPMENT):
            description = stripColorTagDescrTags(module.fullDescription)
        if module.itemTypeID in (GUI_ITEM_TYPE.OPTIONALDEVICE, GUI_ITEM_TYPE.SHELL, GUI_ITEM_TYPE.EQUIPMENT):
            icon = module.icon
        else:
            icon = module.level
        extraModuleInfo = ''
        moduleData = {'name': module.longUserName,
         'windowTitle': ' '.join([module.longUserName, i18n.makeString(MENU.MODULEINFO_TITLE)]),
         'type': module.itemTypeName,
         'description': description,
         'level': icon,
         'params': [],
         'compatible': [],
         'effects': {},
         'moduleLabel': module.getGUIEmblemID(),
         'moduleLevel': module.level}
        params = params_helper.get(module, self.__vehicleDescr)
        moduleParameters = params.get('parameters', {})
        formattedModuleParameters = formatters.getFormattedParamsList(module.descriptor, moduleParameters)
        extraParamsInfo = params.get('extras', {})
        isGun = module.itemTypeID == GUI_ITEM_TYPE.GUN
        isShell = module.itemTypeID == GUI_ITEM_TYPE.SHELL
        isChassis = module.itemTypeID == GUI_ITEM_TYPE.CHASSIS
        isOptionalDevice = module.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE
        excludedParametersNames = extraParamsInfo.get('excludedParams', tuple())
        if isGun:
            if 'maxShotDistance' in moduleParameters:
                if moduleParameters['maxShotDistance'] >= _DEF_SHOT_DISTANCE:
                    excludedParametersNames += ('maxShotDistance',)
            gunReloadingType = extraParamsInfo[GUN_RELOADING_TYPE]
            if gunReloadingType == GUN_CLIP:
                description = i18n.makeString(MENU.MODULEINFO_CLIPGUNLABEL)
                extraModuleInfo = CLIP_ICON_PATH
            elif gunReloadingType == GUN_CAN_BE_CLIP:
                otherParamsInfoList = []
                for paramName, paramValue in formattedModuleParameters:
                    if paramName in excludedParametersNames:
                        otherParamsInfoList.append({'type': formatters.formatModuleParamName(paramName) + '\n',
                         'value': text_styles.stats(paramValue)})

                imgPathArr = CLIP_ICON_PATH.split('..')
                imgPath = 'img://gui' + imgPathArr[1]
                moduleData['otherParameters'] = {'headerText': i18n.makeString(MENU.MODULEINFO_PARAMETERSCLIPGUNLABEL, imgPath),
                 'params': otherParamsInfoList}
        if isChassis:
            if moduleParameters['isHydraulic']:
                description = i18n.makeString(MENU.MODULEINFO_HYDRAULICCHASSISLABEL)
                extraModuleInfo = HYDRAULIC_ICON_PATH
        moduleData['description'] = description
        paramsList = []
        for paramName, paramValue in formattedModuleParameters:
            if paramName not in excludedParametersNames:
                paramsList.append({'type': formatters.formatModuleParamName(paramName) + '\n',
                 'value': text_styles.stats(paramValue)})

        moduleData['parameters'] = {'headerText': i18n.makeString(MENU.MODULEINFO_PARAMETERSLABEL) if paramsList else '',
         'params': paramsList}
        moduleData[EXTRA_MODULE_INFO] = extraModuleInfo
        moduleCompatibles = params.get('compatible', tuple())
        for paramType, paramValue in moduleCompatibles:
            compatible = moduleData.get('compatible')
            compatible.append({'type': i18n.makeString(MENU.moduleinfo_compatible(paramType)),
             'value': paramValue})

        if module.itemTypeID == GUI_ITEM_TYPE.EQUIPMENT:
            effectsNametemplate = '#artefacts:%s/%s'
            if self.lobbyContext.getServerSettings().spgRedesignFeatures.isStunEnabled():
                isRemovingStun = module.isRemovingStun
            else:
                isRemovingStun = False
            onUseStr = 'removingStun/onUse' if isRemovingStun else 'onUse'
            moduleData['effects'] = {'effectOnUse': i18n.makeString(effectsNametemplate % (module.name, onUseStr)),
             'effectAlways': i18n.makeString(effectsNametemplate % (module.name, 'always')),
             'effectRestriction': i18n.makeString(effectsNametemplate % (module.name, 'restriction'))}
            cooldownSeconds = module.descriptor.cooldownSeconds
            if cooldownSeconds > 0:
                moduleData['addParams'] = {'type': formatters.formatModuleParamName('cooldownSeconds') + '\n',
                 'value': text_styles.stats(cooldownSeconds) + '\n'}
        if isShell and self.__isAdditionalInfoShow is not None:
            moduleData['additionalInfo'] = self.__isAdditionalInfoShow
        if isOptionalDevice:
            moduleData['highlightType'] = SLOT_HIGHLIGHT_TYPES.EQUIPMENT_PLUS if module.isDeluxe() else SLOT_HIGHLIGHT_TYPES.NO_HIGHLIGHT
        self.as_setModuleInfoS(moduleData)
        self._updateActionButton()
        return

    def _updateActionButton(self):
        isButtonVisible = False
        buttonLabel = ''
        canPurchase, canUnlock = False, False
        isButtonVisible = canPurchase or canUnlock
        if canPurchase:
            buttonLabel = i18n.makeString(MENU.CONTEXTMENU_BUY)
        elif canUnlock:
            buttonLabel = i18n.makeString(MENU.UNLOCKS_UNLOCKBUTTON)
        buttonData = {'visible': isButtonVisible,
         'label': buttonLabel}
        self.as_setActionButtonS(buttonData)
