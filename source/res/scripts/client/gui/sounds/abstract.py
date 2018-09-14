# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/sounds/abstract.py
import SoundGroups
from gui.sounds.sound_constants import SoundSystems, HQRenderState

class SoundSystemAbstract(object):

    def getID(self):
        """
        Unique sound system's identificator
        :return: id
        :rtype: int
        """
        raise NotImplementedError

    def init(self):
        pass

    def fini(self):
        pass

    def isMSR(self):
        """
        Is user's PC a weak for current sound system
        :return: bool
        """
        return False

    def enableDynamicPreset(self):
        """
        Switch on particular sound preset
        """
        pass

    def disableDynamicPreset(self):
        """
        Switch off particular sound preset
        """
        pass

    def setSoundSystem(self, value):
        """
        Switch between sound systems
        :param value: int - particular sound system index
        :return:
        """
        pass

    def setBassBoost(self, isEnabled):
        """
        Enable/disable bass boost.
        """
        pass

    def sendGlobalEvent(self, eventName, **params):
        """
        This method is used to send global event to the currently
        enabled sound system
        
        @param eventName: str
        @param params: key->value parameters
        @return:
        """
        pass

    def onEnvStart(self, environment):
        """
        This method is used to notify sound system about environment start
        
        @param environement: str
        @return:
        """
        pass

    def onEnvStop(self, environment):
        """
        This method is used to notify sound system about environment stop
        
        @param environement: str
        @return:
        """
        pass

    def __repr__(self):
        return 'SoundSystem(%s)' % SoundSystems.getUserName(self.getID())
