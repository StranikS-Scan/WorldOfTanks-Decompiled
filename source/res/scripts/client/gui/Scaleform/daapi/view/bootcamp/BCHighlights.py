# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCHighlights.py
from gui.Scaleform.daapi.view.meta.BCHighlightsMeta import BCHighlightsMeta
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP
import SoundGroups

class BCHighlights(BCHighlightsMeta):
    BUTTON_SOUNDS = ('InBattleExtinguisher', 'InBattleHealKit', 'InBattleRepairKit', 'StartBattleButton')
    HIGHLIGHT_NO_SOUNDS = ('LoadingRightButton', 'LoadingLeftButton')

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
        self.hideHint(componentID, shouldStop=False)

    def onComponentTriggered(self, componentID):
        LOG_DEBUG_DEV_BOOTCAMP('BCHighlights_onComponentTriggered', componentID)

    def showHint(self, componentID):
        LOG_DEBUG_DEV_BOOTCAMP('BCHighlights_showHint', componentID)
        self.__activeHints.add(componentID)
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
            self.__soundsBySoundID[soundID] = (componentID, snd)
            LOG_DEBUG_DEV_BOOTCAMP('BCHighlights_showHint - playing', soundID)
            snd.play()
        return

    def hideHint(self, componentID, shouldStop=True):
        soundID, snd = self.__soundsByComponentID.pop(componentID, (None, None))
        if snd is not None:
            LOG_DEBUG_DEV_BOOTCAMP('BCHighlights_hideHint', componentID, shouldStop)
            activeSoundComponentID, activeSound = self.__soundsBySoundID.get(soundID, None)
            if activeSound is snd:
                if shouldStop:
                    LOG_DEBUG_DEV_BOOTCAMP('BCHighlights_hideHint - stopping', soundID)
                    snd.stop()
                elif snd.isPlaying:
                    self.__orphanedSounds.append(activeSound)
                LOG_DEBUG_DEV_BOOTCAMP('BCHighlights_hideHint - removing from active sounds', soundID)
                del self.__soundsBySoundID[soundID]
        self.as_removeHighlightS(componentID)
        self.__activeHints.discard(componentID)
        return

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
