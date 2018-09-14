# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ModuleInfoWindow.py
import BigWorld
from gui.shared import g_itemsCache
from gui.shared.utils import SHELLS_COUNT_PROP_NAME, SHELL_RELOADING_TIME_PROP_NAME, RELOAD_MAGAZINE_TIME_PROP_NAME, GUN_RELOADING_TYPE, GUN_CAN_BE_CLIP, GUN_NORMAL, GUN_CLIP, RELOAD_TIME_PROP_NAME, CLIP_ICON_PATH, EXTRA_MODULE_INFO
from gui.Scaleform.locale.MENU import MENU
from gui.shared.utils.functions import stripShortDescrTags
from items import ITEM_TYPE_NAMES
from helpers import i18n
from gui.shared.utils import ItemsParameters
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.meta.ModuleInfoMeta import ModuleInfoMeta

class ModuleInfoWindow(ModuleInfoMeta):

    def __init__(self, ctx = None):
        super(ModuleInfoWindow, self).__init__()
        self.moduleCompactDescr = int(ctx.get('moduleCompactDescr'))
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
        module = g_itemsCache.items.getItemByCD(self.moduleCompactDescr)
        description = ''
        if module.itemTypeName in (ITEM_TYPE_NAMES[9], ITEM_TYPE_NAMES[11]):
            description = stripShortDescrTags(module.fullDescription)
        if module.itemTypeName in (ITEM_TYPE_NAMES[9], ITEM_TYPE_NAMES[10], ITEM_TYPE_NAMES[11]):
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
        params = ItemsParameters.g_instance.get(module.descriptor, self.__vehicleDescr)
        moduleParameters = params.get('parameters', tuple())
        isGun = module.itemTypeName == ITEM_TYPE_NAMES[4]
        isShell = module.itemTypeName == ITEM_TYPE_NAMES[10]
        excludedParametersNames = []
        if isGun:
            gunReloadingType = dict(moduleParameters)[GUN_RELOADING_TYPE]
            if gunReloadingType == GUN_NORMAL:
                excludedParametersNames.append(SHELLS_COUNT_PROP_NAME)
                excludedParametersNames.append(RELOAD_MAGAZINE_TIME_PROP_NAME)
                excludedParametersNames.append(SHELL_RELOADING_TIME_PROP_NAME)
            elif gunReloadingType == GUN_CLIP:
                description = i18n.makeString(MENU.MODULEINFO_CLIPGUNLABEL)
                excludedParametersNames.append(RELOAD_TIME_PROP_NAME)
                extraModuleInfo = CLIP_ICON_PATH
            elif gunReloadingType == GUN_CAN_BE_CLIP:
                excludedParametersNames.append(SHELLS_COUNT_PROP_NAME)
                excludedParametersNames.append(RELOAD_MAGAZINE_TIME_PROP_NAME)
                excludedParametersNames.append(SHELL_RELOADING_TIME_PROP_NAME)
                otherParamsInfoList = []
                for paramType, paramValue in moduleParameters:
                    if paramType in excludedParametersNames:
                        otherParamsInfoList.append({'type': i18n.makeString(MENU.moduleinfo_params(paramType)),
                         'value': paramValue})

                imgPathArr = CLIP_ICON_PATH.split('..')
                imgPath = 'img://gui' + imgPathArr[1]
                moduleData['otherParameters'] = {'headerText': i18n.makeString(MENU.MODULEINFO_PARAMETERSCLIPGUNLABEL, imgPath),
                 'params': otherParamsInfoList}
        moduleData['description'] = description
        excludedParametersNames.append(GUN_RELOADING_TYPE)
        paramsList = []
        for paramType, paramValue in moduleParameters:
            if paramType not in excludedParametersNames:
                paramsList.append({'type': i18n.makeString(MENU.moduleinfo_params(paramType)),
                 'value': paramValue})

        moduleData['parameters'] = {'headerText': i18n.makeString(MENU.MODULEINFO_PARAMETERSLABEL) if len(paramsList) > 0 else '',
         'params': paramsList}
        moduleData[EXTRA_MODULE_INFO] = extraModuleInfo
        moduleCompatibles = params.get('compatible', tuple())
        for paramType, paramValue in moduleCompatibles:
            compatible = moduleData.get('compatible')
            compatible.append({'type': i18n.makeString(MENU.moduleinfo_compatible(paramType)),
             'value': paramValue})

        if module.itemTypeName == ITEM_TYPE_NAMES[11]:
            effectsNametemplate = '#artefacts:%s/%s'
            moduleData['effects'] = {'effectOnUse': i18n.makeString(effectsNametemplate % (module.name, 'onUse')),
             'effectAlways': i18n.makeString(effectsNametemplate % (module.name, 'always')),
             'effectRestriction': i18n.makeString(effectsNametemplate % (module.name, 'restriction'))}
        if isShell and self.__isAdditionalInfoShow is not None:
            moduleData['additionalInfo'] = self.__isAdditionalInfoShow
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
