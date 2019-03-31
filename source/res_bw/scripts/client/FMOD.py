# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/FMOD.py
# Compiled at: 2010-05-25 20:46:16
try:
    from _FMOD import *
except ImportError:
    print 'WARNING: FMOD support is not enabled.'
    from _FMODStubs import *

import BigWorld
BigWorld.getSound = getSound
BigWorld.getSoundBanks = getSoundBanks
BigWorld.playSound = playSound
BigWorld.setDefaultSoundProject = setDefaultSoundProject
BigWorld.loadSoundBankIntoMemory = loadSoundBankIntoMemory
BigWorld.loadSoundBank = loadEventProject
BigWorld.loadSoundGroup = loadSoundGroup
BigWorld.reloadSoundBank = reloadEventProject
BigWorld.unloadSoundBankFromMemory = unloadSoundBankFromMemory
BigWorld.unloadSoundBank = unloadEventProject
BigWorld.unloadSoundGroup = unloadSoundGroup
BigWorld.setMasterVolume = setMasterVolume
del BigWorld
