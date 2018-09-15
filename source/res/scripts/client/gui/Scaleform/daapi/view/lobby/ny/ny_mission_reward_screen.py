# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ny/ny_mission_reward_screen.py
import BigWorld
from debug_utils import LOG_DEBUG, LOG_WARNING
from gui import makeHtmlString
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.lobby.ny.ny_common import NO_SETTING_BOX_ID, getRewardsRibbonData
from gui.Scaleform.daapi.view.meta.NYMissionRewardScreenMeta import NYMissionRewardScreenMeta
from gui.Scaleform.locale.NY import NY
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events.bonuses import VehiclesBonus
from helpers import i18n, dependency
from helpers import int2roman
from helpers.i18n import makeString
from new_year.new_year_sounds import NYSoundEvents
from skeletons.new_year import INewYearController
BOX_ANIM_MAPPING = {'any': '../flash/nyBoxAnimAny.swf',
 'asian': '../flash/nyBoxAnimAsian.swf',
 'traditionalWestern': '../flash/nyBoxAnimEurope.swf',
 'soviet': '../flash/nyBoxAnimSoviet.swf',
 'modernWestern': '../flash/nyBoxAnimWestern.swf'}
BOX_ANIM_MAPPING_LOW = {'any': '../flash/nyBoxAnimAny_low.swf',
 'asian': '../flash/nyBoxAnimAsian_low.swf',
 'traditionalWestern': '../flash/nyBoxAnimEurope_low.swf',
 'soviet': '../flash/nyBoxAnimSoviet_low.swf',
 'modernWestern': '../flash/nyBoxAnimWestern_low.swf'}

class NYMissionRewardScreen(LobbySubView, NYMissionRewardScreenMeta):
    _newYearController = dependency.descriptor(INewYearController)
    __background_alpha__ = 0.0

    def __init__(self, ctx=None):
        super(NYMissionRewardScreen, self).__init__(ctx)
        self.__nySetting = ctx.get('nySettingID')

    def onCloseWindow(self):
        self.destroy()

    def onOpenBtnClick(self):
        if self._newYearController.boxStorage.count > 0:
            if self.__requestToOpenBox():
                self.__restartAnimation()
        else:
            self.onCloseWindow()

    def onPlaySound(self, soundType):
        NYSoundEvents.playSound(soundType)

    def onToyObtained(self, level):
        NYSoundEvents.setRTPC(NYSoundEvents.RTPC_TOYS, int(level))

    def _populate(self):
        super(NYMissionRewardScreen, self)._populate()
        if not self._newYearController.isEnabled() or not self._newYearController.isAvailable():
            self.onCloseWindow()
        self.as_setInitDataS({'closeBtnLabel': NY.MISSIONREWARDSCREEN_CLOSEBTNLABEL,
         'header': NY.MISSIONREWARDSCREEN_HEADER,
         'headerExtra': NY.MISSIONREWARDSCREEN_HEADEREXTRA})
        if not self._newYearController.boxStorage.isUnderOpening():
            if self.__requestToOpenBox():
                self.__startAnimation()
        else:
            self.__startAnimation()
        self.__updateOpenBtnLabel()
        self._newYearController.boxStorage.onItemOpened += self.__onBoxOpened
        self._newYearController.boxStorage.onItemOpenError += self.__onBoxOpenError
        self._newYearController.boxStorage.onCountChanged += self.__onBoxCountChanged
        self._newYearController.onStateChanged += self.__onNyStateChanged

    def _dispose(self):
        self.onCreated -= self.__onCreated
        self._newYearController.boxStorage.onItemOpened -= self.__onBoxOpened
        self._newYearController.boxStorage.onItemOpenError += self.__onBoxOpenError
        self._newYearController.boxStorage.onCountChanged -= self.__onBoxCountChanged
        self._newYearController.onStateChanged -= self.__onNyStateChanged
        super(NYMissionRewardScreen, self)._dispose()

    def __onBoxOpened(self, _, bonuses):
        self.__showRewardAnimation(bonuses)
        self.__updateOpenBtnLabel()

    def __requestToOpenBox(self):
        return self._newYearController.boxStorage.open(self._newYearController.boxStorage.getItemIDBySetting(self.__nySetting))

    def __restartAnimation(self):
        setting_id = self.__getOpeningBoxSettingID()
        if setting_id is not None:
            LOG_DEBUG('Box "{}" animation restarting.'.format(setting_id))
            animMapping = BOX_ANIM_MAPPING_LOW if self.__isNeedLowQualityAnim() else BOX_ANIM_MAPPING
            self.as_restartAnimationS(animMapping.get(setting_id))
            NYSoundEvents.setBoxSwitch(setting_id)
        return

    def __startAnimation(self):
        setting_id = self.__getOpeningBoxSettingID()
        if setting_id is not None:
            LOG_DEBUG('Box "{}" animation starting.'.format(setting_id))
            animMapping = BOX_ANIM_MAPPING_LOW if self.__isNeedLowQualityAnim() else BOX_ANIM_MAPPING
            self.as_startAnimationS(animMapping.get(setting_id))
            NYSoundEvents.setBoxSwitch(setting_id)
        return

    def __showRewardAnimation(self, bonuses):
        for bonus in bonuses:
            if isinstance(bonus, VehiclesBonus):
                vehicle = bonus.getVehicles()[0][0]
                compensation = bonus.compensation(vehicle)
                if not compensation:
                    vehName = vehicle.name
                    vehIcon = RES_ICONS.getNyRewardVehicle(vehName.replace(':', '-'))
                    if vehIcon is not None:
                        self.as_setVehicleDataS({'vehicleSrc': vehIcon,
                         'vehicleDesk': makeHtmlString('html_templates:newYear', 'vehicle_reward', {'level': makeString(int2roman(vehicle.level)),
                                         'icon': vehicle.type if not vehicle.isElite else '{}_elite'.format(vehicle.type),
                                         'name': vehicle.userName})})
                break

        self.as_setRewardDataS(getRewardsRibbonData(bonuses))
        return

    def __onBoxOpenError(self, _):
        if self.isCreated():
            self.destroy()
        else:
            self.onCreated += self.__onCreated

    def __onCreated(self):
        self.destroy()

    def __onBoxCountChanged(self, *args):
        self.__updateOpenBtnLabel()

    def __onNyStateChanged(self, _):
        if not self._newYearController.isAvailable():
            self.destroy()

    def __updateOpenBtnLabel(self):
        count = self._newYearController.boxStorage.count
        if count > 0:
            txt = i18n.makeString(NY.MISSIONREWARDWINDOW_BUTTON_STATUSLABEL, count=str(count))
        else:
            txt = i18n.makeString(NY.MISSIONREWARDWINDOW_BUTTON_STATUSLABEL_NOITEMS)
        LOG_DEBUG('Button text changed: {}'.format(txt))
        self.as_setOpenBtnLabelS(txt)

    def __getOpeningBoxSettingID(self):
        boxId = self._newYearController.boxStorage.openingItemId
        descr = self._newYearController.boxStorage.getDescriptors().get(boxId)
        if descr:
            return descr.setting or NO_SETTING_BOX_ID
        else:
            LOG_WARNING("Couldn't find setting ID. Unknown box ID '{}'".format(boxId))
            return None

    @staticmethod
    def __isNeedLowQualityAnim():
        osVerId = BigWorld.getOSVersionId() >> 16
        if osVerId in (1281, 1282, 256):
            return True
        if osVerId == 1537:
            osBitness = BigWorld.getOSBitnessId()
            if osBitness == 1:
                return True
        return False
