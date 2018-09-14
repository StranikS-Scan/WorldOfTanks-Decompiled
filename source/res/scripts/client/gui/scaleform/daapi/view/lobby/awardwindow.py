# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/AwardWindow.py
import BigWorld
from helpers.i18n import makeString as _ms
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.game_control import g_instance as g_gameCtrl
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.Scaleform.daapi.view.meta.AwardWindowMeta import AwardWindowMeta
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.managers.TextManager import TextType
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.managers.UtilsManager import ImageUrlProperties

class AwardWindow(View, AbstractWindowView, AwardWindowMeta, AppRef):

    def __init__(self, ctx):
        super(AwardWindow, self).__init__()
        self.__item = ctx.get('item')
        self.__achievedXp = ctx.get('xp')
        self.__nextXp = ctx.get('nextXp')
        self.__boughtVehicle = ctx.get('boughtVehicle', False)

    def onWindowClose(self):
        self.destroy()

    def onOKClick(self):
        self.onWindowClose()

    def _populate(self):
        super(AwardWindow, self)._populate()
        data = None
        if self.__item is not None:
            if self.__item.itemTypeID == GUI_ITEM_TYPE.TANKMAN:
                data = self._getTankmanData()
            elif self.__item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
                data = self._getVehicleData()
        if data is not None:
            self.as_setDataS(data)
        else:
            LOG_ERROR('Ref system award window item data is empty', self.__item)
            return self.destroy()
        return

    def _getTankmanData(self):
        if self.__achievedXp is not None:
            description = _ms(MENU.AWARDWINDOW_REFERRAL_TANKMAN_DESCRIPTION_NORMAL, expCount=BigWorld.wg_getIntegralFormat(self.__achievedXp), tankman=self.__item.roleUserName)
        else:
            description = _ms(MENU.AWARDWINDOW_REFERRAL_TANKMAN_DESCRIPTION_NOXP, tankman=self.__item.roleUserName)
        if self.__nextXp is not None:
            expCount = '%s<nobr>%s' % (BigWorld.wg_getIntegralFormat(self.__nextXp), self.app.utilsManager.getHtmlIconText(ImageUrlProperties(RES_ICONS.MAPS_ICONS_LIBRARY_XPCOSTICON, 18, 18, -8, 0)))
            additionalText = _ms(MENU.AWARDWINDOW_REFERRAL_NEXTTANKMAN, expCount=self.app.utilsManager.textManager.getText(TextType.CREDITS_TEXT, expCount))
        else:
            additionalText = ''
        return {'windowTitle': _ms(MENU.AWARDWINDOW_TITLE_NEWTANKMAN),
         'backImage': RES_ICONS.MAPS_ICONS_REFERRAL_AWARDBACK,
         'awardImage': RES_ICONS.MAPS_ICONS_REFERRAL_TANKMANMALE,
         'header': self.app.utilsManager.textManager.getText(TextType.HIGH_TITLE, _ms(MENU.AWARDWINDOW_REFERRAL_TANKMAN_HEADER)),
         'description': self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, description),
         'additionalText': self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, additionalText)}

    def _getVehicleData(self):
        if self.__boughtVehicle:
            descriptionText = _ms(MENU.AWARDWINDOW_REFERRAL_VEHICLE_DESCRIPTION_BOUGHT, vehicleName=self.__item.userName)
        elif self.__achievedXp is not None:
            descriptionText = _ms(MENU.AWARDWINDOW_REFERRAL_VEHICLE_DESCRIPTION_NORMAL, expCount=BigWorld.wg_getIntegralFormat(self.__achievedXp), vehicleName=self.__item.userName)
        else:
            descriptionText = _ms(MENU.AWARDWINDOW_REFERRAL_VEHICLE_DESCRIPTION_NOXP, vehicleName=self.__item.userName)
        return {'windowTitle': _ms(MENU.AWARDWINDOW_TITLE_NEWVEHICLE),
         'backImage': RES_ICONS.MAPS_ICONS_REFERRAL_AWARDBACK,
         'awardImage': self.__item.iconUnique,
         'header': self.app.utilsManager.textManager.getText(TextType.HIGH_TITLE, _ms(MENU.AWARDWINDOW_REFERRAL_VEHICLE_HEADER, vehicleName=self.__item.userName)),
         'description': self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, descriptionText),
         'additionalText': self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, _ms(MENU.AWARDWINDOW_REFERRAL_COMPLETE, modifiers=self._getModifiersText()))}

    def _getModifiersText(self):
        result = []
        for _, xpFactor in g_gameCtrl.refSystem.getRefPeriods():
            result.append('%s<nobr>x%s' % (self.app.utilsManager.getHtmlIconText(ImageUrlProperties(RES_ICONS.MAPS_ICONS_LIBRARY_XPCOSTICON, 18, 18, -8, 0)), BigWorld.wg_getNiceNumberFormat(xpFactor)))

        return ', '.join(result)
