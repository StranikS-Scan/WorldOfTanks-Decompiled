# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCHighlights.py
from gui.Scaleform.daapi.view.meta.BCHighlightsMeta import BCHighlightsMeta
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP, LOG_ERROR_BOOTCAMP
from helpers import dependency
from skeletons.gui.shared import IItemsCache
import SoundGroups

class BCHighlights(BCHighlightsMeta):
    BUTTON_SOUNDS = ('AmmunitionEquipment', 'AmmunitionOptionalDevices', 'BattleType', 'FightButton', 'FirstTankman', 'HangarButton', 'OptionalDevice', 'PersonalCaseClose', 'PersonalCaseOption', 'PersonalCaseSkill', 'PersonalCaseSkillSelect', 'QuestsControl', 'RandomBattle', 'ResearchButton', 'ResearchNode', 'ResearchNodeTankII', 'ServiceAccept', 'ServiceSlot', 'ServiceSlotRepairOption', 'TechNodeUsa', 'TechTreeButton', 'VehicleBuyAcademy', 'VehicleBuyAccept', 'VehiclePreviewUnlockButton', 'InBattleExtinguisher', 'InBattleHealKit', 'InBattleRepairKit', 'SecondTank')
    HIGHLIGHT_NO_SOUNDS = ('LoadingRightButton', 'LoadingLeftButton', 'StartBattleButton', 'AmmunitionSlot', 'DialogAccept')

    def __init__(self, settings):
        super(BCHighlights, self).__init__()
        self.__soundsByComponentID = {}
        self.__soundsBySoundID = {}
        self.__orphanedSounds = []
        self.__activeHints = set()
        self.__descriptors = settings['descriptors']
        self.__componentsAnimationFinished = {}

    def setDescriptors(self, descriptors):
        self.as_setDescriptorsS(descriptors)

    def onHighlightAnimationComplete(self, componentID):
        LOG_DEBUG_DEV_BOOTCAMP('BCHighlights_onHintAnimationComplete', componentID)
        from bootcamp.Bootcamp import g_bootcamp
        from bootcamp.BootcampGarage import g_bootcampGarage
        g_bootcampGarage.resumeLesson()
        if g_bootcampGarage is not None and g_bootcamp.isInGarageState():
            g_bootcampGarage.showNextHint()
        self.hideHint(componentID, shouldStop=False)
        return

    def onComponentTriggered(self, componentID):
        LOG_DEBUG_DEV_BOOTCAMP('BCHighlights_onComponentTriggered', componentID)

    def showHint(self, componentID):
        LOG_DEBUG_DEV_BOOTCAMP('BCHighlights_showHint', componentID)
        self.__activeHints.add(componentID)
        self.updateDescriptors(componentID)
        self.as_addHighlightS(componentID)
        if componentID not in self.HIGHLIGHT_NO_SOUNDS:
            soundID = 'bc_new_ui_element_button' if componentID in self.BUTTON_SOUNDS else 'bc_new_ui_element'
            activeSoundComponentID, activeSound = self.__soundsBySoundID.get(soundID, (None, None))
            if activeSound is not None and activeSound.isPlaying:
                LOG_DEBUG_DEV_BOOTCAMP('BCHighlights_showHint - skipping {0} (already playing from component {1})'.format(soundID, activeSoundComponentID))
                return
            prevSoundID, snd = self.__soundsByComponentID.get(componentID, (None, None))
            if snd is None:
                snd = SoundGroups.g_instance.getSound2D(soundID)
                self.__soundsByComponentID[componentID] = (soundID, snd)
            else:
                assert prevSoundID == soundID
            self.__soundsBySoundID[soundID] = (componentID, snd)
            LOG_DEBUG_DEV_BOOTCAMP('BCHighlights_showHint - playing', soundID)
            snd.play()
        if componentID not in ('HangarButton', 'TechTreeButton', 'SecondTank'):
            from bootcamp.BootcampGarage import g_bootcampGarage
            g_bootcampGarage.resumeLesson()
        return

    def hideHint(self, componentID, shouldStop=True):
        soundID, snd = self.__soundsByComponentID.pop(componentID, (None, None))
        if snd is not None:
            LOG_DEBUG_DEV_BOOTCAMP('BCHighlights_hideHint', componentID, shouldStop)
            activeSoundComponentID, activeSound = self.__soundsBySoundID.get(soundID, None)
            if activeSound is snd:
                assert activeSoundComponentID == componentID
                if shouldStop:
                    LOG_DEBUG_DEV_BOOTCAMP('BCHighlights_hideHint - stopping', soundID)
                    snd.stop()
                elif snd.isPlaying:
                    self.__orphanedSounds.append(activeSound)
                LOG_DEBUG_DEV_BOOTCAMP('BCHighlights_hideHint - removing from active sounds', soundID)
                del self.__soundsBySoundID[soundID]
            else:
                assert not snd.isPlaying
        self.as_removeHighlightS(componentID)
        self.__activeHints.discard(componentID)
        return

    def hideAllHints(self):
        LOG_DEBUG_DEV_BOOTCAMP('BCHighlights_hideAllHints')
        hintsToHide = list(self.__activeHints)
        for componentID in hintsToHide:
            self.hideHint(componentID)

    def updateDescriptors(self, componentID):
        from bootcamp.BootcampLobbyHintsConfig import g_bootcampHintsConfig
        from bootcamp.BootcampGarage import g_bootcampGarage
        nationData = g_bootcampGarage.getNationData()
        component = g_bootcampHintsConfig.objects[componentID]
        if componentID == 'ResearchNode':
            component['asInt'] = nationData['module']
        elif componentID == 'AmmunitionSlot':
            component['path'] = 'ammunitionPanel.{0}'.format(nationData['module_type'])
        elif componentID == 'ResearchNodeTankII':
            component['asInt'] = nationData['vehicle_second']
        elif componentID == 'TechNodeUsa':
            component['asInt'] = nationData['vehicle_first']
        elif componentID == 'ServiceSlotRepairOption':
            component['asInt'] = nationData['consumable']
        elif componentID == 'OptionalDevice':
            component['asInt'] = nationData['equipment']
        elif componentID == 'PersonalCaseSkill':
            component['skillId'] = nationData['perk']
        elif componentID == 'SkillSlot':
            component['skillId'] = nationData['perk']
        elif componentID == 'SecondTank':
            itemsCache = dependency.instance(IItemsCache)
            vehicleCD = nationData['vehicle_second']
            vehicle = itemsCache.items.getItemByCD(vehicleCD)
            component['TankIndex'] = str(vehicle.invID)
        self.setDescriptors(g_bootcampHintsConfig.getItems())

    def _populate(self):
        super(BCHighlights, self)._populate()
        self.setDescriptors(self.__descriptors)

    def _dispose(self):
        super(BCHighlights, self)._dispose()
        for _, sound in self.__soundsByComponentID.itervalues():
            sound.stop()

        self.__soundsByComponentID.clear()
        self.__soundsBySoundID.clear()
        del self.__orphanedSounds[:]
