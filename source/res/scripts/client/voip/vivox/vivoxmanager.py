# Embedded file name: scripts/client/VOIP/Vivox/VivoxManager.py
import BigWorld
from VOIP import constants
from VOIP.VOIPManager import VOIPManager, LOG_VOIP_INT
from debug_utils import verify
import math

class VivoxManager(VOIPManager):

    def __init__(self, channelsMgr):
        LOG_VOIP_INT('VivoxManager.create')
        VOIPManager.__init__(self, channelsMgr)

    def destroy(self):
        LOG_VOIP_INT('VivoxManager.destroy')
        VOIPManager.destroy(self)

    def getVADProperties(self):
        LOG_VOIP_INT('VivoxManager.getVADProperties')
        cmd = {constants.KEY_COMMAND: constants.CMD_REQ_AUX_GET_VAD_PROPERTIES}
        BigWorld.VOIP.command(cmd)

    def setVADProperties(self, hangover, sensitivity):
        LOG_VOIP_INT('VivoxManager.setVADProperties')
        cmd = {constants.KEY_COMMAND: constants.CMD_REQ_AUX_SET_VAD_PROPERTIES,
         constants.KEY_VAD_HANGOVER: str(hangover),
         constants.KEY_VAD_SENSITIVITY: str(sensitivity)}
        BigWorld.VOIP.command(cmd)
        LOG_VOIP_INT('VOIPManager::setVADProperties %d %d' % (hangover, sensitivity))

    def __normalizeVoices(self):
        LOG_VOIP_INT('VivoxManager.__normalizeVoices')
        myOwnUri = self.channelsMgr.loginName

        def speaking(channelUser):
            return float(channelUser['energy']) > 0 and channelUser['uri'] != myOwnUri and channelUser['talking']

        speakingChannelUsers = filter(speaking, self.channelUsers.values())
        for channelUser in speakingChannelUsers:
            if channelUser['talking']:
                volumeUpdateDelta = BigWorld.time() - channelUser['lastVolumeUpdateTime']
                if volumeUpdateDelta > 0.1:
                    currentEnergy = float(channelUser['energy'])
                    desiredVolume = constants.NORMAL_VOLUME + math.log(1 / currentEnergy, constants.LOGARITHM_BASE)
                    desiredVolume = round(desiredVolume)
                    LOG_VOIP_INT('setting user %s volume %f energy %f' % (channelUser['uri'], desiredVolume, currentEnergy))
                    self.setParticipantVolume(channelUser['uri'], desiredVolume)
                    channelUser['lastVolumeUpdateTime'] = BigWorld.time()

    def _muteParticipantForMe(self, dbid, mute):
        LOG_VOIP_INT('VivoxManager._muteParticipantForMe')
        verify(dbid in self.channelUsers)
        self.channelUsers[dbid]['muted'] = mute
        uri = self.channelUsers[dbid]['uri']
        cmd = {}
        cmd[constants.KEY_COMMAND] = constants.CMD_SET_PARTICIPANT_MUTE
        cmd[constants.KEY_PARTICIPANT_URI] = uri
        cmd[constants.KEY_STATE] = str(mute)
        BigWorld.VOIP.command(cmd)
        LOG_VOIP_INT('mute_for_me: %d, %s' % (dbid, str(mute)))
        self.onParticipantMute(dbid, mute)
        return True

    def _setMicMute(self, muted):
        LOG_VOIP_INT('VivoxManager.setMicMute: %s' % str(muted))
        cmd = {constants.KEY_COMMAND: 'mute_mic',
         constants.KEY_STATE: str(muted)}
        BigWorld.VOIP.command(cmd)

    def setParticipantVolume(self, uri, volume):
        LOG_VOIP_INT('VivoxManager.setParticipantVolume')
        volumeToSet = int(volume)
        if volumeToSet > 100:
            volumeToSet = 100
        cmd = {constants.KEY_COMMAND: constants.CMD_SET_PARTICIPANT_VOLUME,
         constants.KEY_PARTICIPANT_URI: uri,
         constants.KEY_VOLUME: str(volumeToSet)}
        BigWorld.VOIP.command(cmd)
