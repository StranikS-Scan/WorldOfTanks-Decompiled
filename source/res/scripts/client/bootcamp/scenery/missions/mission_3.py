# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/scenery/missions/mission_3.py
import BigWorld
import MusicControllerWWISE as MC
from bootcamp.scenery.AbstractMission import AbstractMission
from constants import HINT_TYPE
from helpers.i18n import makeString
import SoundGroups

class HINT(object):
    PLAYERDETECTED = 0
    FINDMOREENEMIES = 1
    FALLBACK = 2
    FLANKENEMIES = 3
    FOLIAGEINTROA = 4
    FOLIAGEINTROB = 5
    FOLIAGEKEEPMOVING = 6
    FOLIAGECANTDETECT = 7
    FLANKINGFAILS = 8
    FLANKINGWAIT = 9
    CAPTUREBASE = 10
    CAPTUREWATCHOUT = 11
    CAPTURELOST = 12
    CAPTURETOGETHER = 13
    CAPTUREHELP = 14
    CAPTUREINPROGRESS = 15
    INIT_PARAMS = {PLAYERDETECTED: {'message': makeString('#bootcamp:HINT_MISSION3_PLAYERDETECTED'),
                      'hintTypeId': HINT_TYPE.HINT_B3_YOU_ARE_DETECTED,
                      'timeStartDelay': 2.5,
                      'timeDuration': 8.0,
                      'voiceover': 'vo_bc_you_are_detected'},
     FINDMOREENEMIES: {'message': makeString('#bootcamp:HINT_MISSION3_FINDMOREENEMIES'),
                       'timeStartDelay': 1.0,
                       'timeDuration': 4.5,
                       'timeInnerCooldown': 15.0},
     FALLBACK: {'message': makeString('#bootcamp:HINT_MISSION3_FALLBACK'),
                'hintTypeId': HINT_TYPE.HINT_B3_FALL_BACK,
                'voiceover': 'vo_bc_retreat'},
     FLANKENEMIES: {'message': makeString('#bootcamp:HINT_MISSION3_FLANKENEMIES'),
                    'hintTypeId': HINT_TYPE.HINT_B3_FLANK,
                    'voiceover': 'vo_bc_get_around_on_flank'},
     FOLIAGEINTROA: {'message': makeString('#bootcamp:HINT_MISSION3_FOLIAGEINTROA'),
                     'hintTypeId': HINT_TYPE.HINT_B3_FOLIAGE2,
                     'voiceover': 'vo_bc_do_not_shoot'},
     FOLIAGEINTROB: {'message': makeString('#bootcamp:HINT_MISSION3_FOLIAGEINTROB'),
                     'hintTypeId': HINT_TYPE.HINT_B3_FOLIAGE,
                     'voiceover': 'vo_bc_bushes_hide'},
     FOLIAGEKEEPMOVING: {'message': makeString('#bootcamp:HINT_MISSION3_FOLIAGEKEEPMOVING'),
                         'hintTypeId': HINT_TYPE.HINT_B3_FOLIAGE,
                         'voiceover': 'vo_bc_move_forward'},
     FOLIAGECANTDETECT: {'message': makeString('#bootcamp:HINT_MISSION3_FOLIAGECANTDETECT'),
                         'timeDuration': 4.5,
                         'timeInnerCooldown': 15.0},
     FLANKINGFAILS: {'message': makeString('#bootcamp:HINT_MISSION3_FLANKINGFAILS'),
                     'hintTypeId': HINT_TYPE.HINT_B3_YOU_ARE_DETECTED,
                     'voiceover': 'vo_bc_shooting_unmask'},
     FLANKINGWAIT: {'message': makeString('#bootcamp:HINT_MISSION3_FLANKINGWAIT'),
                    'timeDuration': -1.0,
                    'timeStartDelay': 3.0},
     CAPTUREBASE: {'message': makeString('#bootcamp:HINT_MISSION3_CAPTUREBASE'),
                   'hintTypeId': HINT_TYPE.HINT_B3_DO_CAPTURE,
                   'voiceover': 'vo_bc_capture_base'},
     CAPTUREWATCHOUT: {'message': makeString('#bootcamp:HINT_MISSION3_CAPTUREWATCHOUT'),
                       'hintTypeId': HINT_TYPE.HINT_B3_ENEMIES_HIDDEN,
                       'timeDuration': 8.0,
                       'voiceover': 'vo_bc_enemy_can_hide_be_careful'},
     CAPTURELOST: {'message': makeString('#bootcamp:HINT_MISSION3_CAPTURELOST'),
                   'hintTypeId': HINT_TYPE.HINT_B3_CAPTURE_RESET,
                   'timeDuration': 8.0,
                   'voiceover': 'vo_bc_progress_capturing'},
     CAPTURETOGETHER: {'message': makeString('#bootcamp:HINT_MISSION3_CAPTURETOGETHER'),
                       'hintTypeId': HINT_TYPE.HINT_B3_CAPTURE_TOGETHER,
                       'timeDuration': 8.0,
                       'voiceover': 'vo_bc_capture_speed'},
     CAPTUREHELP: {'message': makeString('#bootcamp:HINT_MISSION3_CAPTUREHELP'),
                   'hintTypeId': HINT_TYPE.HINT_B3_DO_CAPTURE,
                   'voiceover': 'vo_bc_return_and_help'},
     CAPTUREINPROGRESS: {'message': makeString('#bootcamp:HINT_MISSION3_CAPTUREINPROGRESS'),
                         'hintTypeId': HINT_TYPE.HINT_B3_CAPTURE_IN_PROGRESS,
                         'timeDuration': 8.0,
                         'voiceover': 'vo_bc_capturing_base_in_process'}}


class PROGRESS(object):
    START = 0
    FLANK = 1
    ADVANCE = 2
    CAPTURE = 3
    CAPTURE_UNDEFINED = 4
    CAPTURE_FINAL = 5


class MARKER(object):
    RECON = 0
    FLANK_START = 1
    FLANK_RECON = 2
    FLANK_END = 3
    BASE_HALFWAY = 4
    BASE = 5
    FALLBACK = 6
    INIT_PARAMS = {RECON: 'ReconMarker_0',
     FLANK_START: 'StealthZoneMarker_0',
     FLANK_RECON: 'StealthZoneMarker_1',
     FLANK_END: 'StealthZoneMarker_2',
     BASE_HALFWAY: 'StealthZoneMarker_Back',
     BASE: 'EnemiesBaseMarker_0',
     FALLBACK: 'FallbackMarker'}


class Mission3(AbstractMission):
    _TOO_MANY_ENEMIES_NUM = 3

    def __init__(self, assistant):
        super(Mission3, self).__init__(assistant)
        self._hints = dict(((v, self.createHint(**HINT.INIT_PARAMS[v])) for k, v in HINT.__dict__.iteritems() if isinstance(v, int)))
        self._markers = dict(((v, self.createMarker(MARKER.INIT_PARAMS[v])) for k, v in MARKER.__dict__.iteritems() if isinstance(v, int)))
        self._playerVehicle = self.playerVehicle()
        self._vehicleEnemy1stPack = [ self.createVehicle(name) for name in ('Miron Nebaluiev', 'Fridrih Simann', 'Matt Underlay') ]
        self._vehicleEnemy2ndPackMain = [ self.createVehicle(name) for name in ('James Brounge', 'Oda Nisura', 'Gavril Stolbov', 'Fabian Haupt') ]
        self._vehicleEnemy2ndPackSecondary = [ self.createVehicle(name) for name in ('Frank Dimmelton', 'John Dicker') ]
        self._vehicleEnemy2ndPackAll = self._vehicleEnemy2ndPackMain + self._vehicleEnemy2ndPackSecondary
        self._vehicleEnemyDefendersPack = [ self.createVehicle(name) for name in ('Fabian Haupt', 'Konrad Cerstvy') ]
        self._vehicleAlliesDefendersPack = [ self.createVehicle(name) for name in ('Richard Bogelber', 'Keiko Simura', 'Sheng En') ]
        self._vehicleAlliesAttackersPack = [self.createVehicle('Siegward Eber')]
        self._enemiesAtFlank = {}
        self._detectedEnemiesList = set()
        self._allyAttackersDead = False
        self._allyAttackerAtEnemiesBase = False
        self._playerDetected = False
        self._progressUndefinedTime = 0.0
        self._inZoneFlanking = False
        self._inZoneStealth_0 = False
        self._inZoneStealth_1 = False
        self._inZoneStealth_2 = False
        self._inZoneBase = False
        self._inZoneAlliedMapPart = True
        self._inZoneEnemiesMapBack = False
        self._halfWayToBasePassed = False
        self._inZoneFallbackDone = True
        self._inZoneFallbackHidden = True
        self._progress = PROGRESS.START
        self._fallbackStartTime = None
        self._ignoreFallbackTimeToShowMarker = 15.0
        return

    def start(self):
        self.hideAllMarkers()
        for vehicle in self._vehicleEnemy2ndPackMain:
            self._enemiesAtFlank[vehicle.name] = True

        super(Mission3, self).start()
        self.playSound2D('vo_bc_detect_enemy_vehicles')
        self.playSound2D('bc_main_tips_task_start')

    def update(self):
        super(Mission3, self).update()
        numOfDetectedManyEnemiesPack = 0
        for vehicle in self._detectedEnemiesList:
            if vehicle in self._vehicleEnemy2ndPackAll:
                numOfDetectedManyEnemiesPack += 1

        if not self._allyAttackersDead:
            for vehicle in self._vehicleAlliesAttackersPack:
                if vehicle.isAlive:
                    break
            else:
                self._allyAttackersDead = True

        if self._progress == PROGRESS.START:
            if self._hints[HINT.FALLBACK].isNotShown:
                firstPackKilled = True
                for vehicle in self._vehicleEnemy1stPack:
                    if vehicle.isAlive:
                        firstPackKilled = False

                if firstPackKilled:
                    self.showMarker(self._markers[MARKER.RECON])
            if numOfDetectedManyEnemiesPack >= self._TOO_MANY_ENEMIES_NUM and self._playerDetected and not self._inZoneFlanking:
                if not self._hints[HINT.FALLBACK].isActive and not self._hints[HINT.FALLBACK].isDisabled:
                    self.showHint(self._hints[HINT.FALLBACK])
                    self._markers[MARKER.RECON].hide()
                    self._progress = PROGRESS.FLANK
                    self._fallbackStartTime = BigWorld.time()
                    if not MC.g_musicController.isPlaying(MC.MUSIC_EVENT_COMBAT):
                        MC.g_musicController.muteMusic(False)
            if self._inZoneStealth_1 and not self._playerDetected:
                self._progress = PROGRESS.FLANK
                if not MC.g_musicController.isPlaying(MC.MUSIC_EVENT_COMBAT):
                    MC.g_musicController.muteMusic(False)
        if self._progress == PROGRESS.FLANK:
            if not self._inZoneFlanking and self._inZoneAlliedMapPart:
                if not self._playerDetected or numOfDetectedManyEnemiesPack < self._TOO_MANY_ENEMIES_NUM:
                    if not self._hints[HINT.FLANKENEMIES].isActive and not self._hints[HINT.FLANKENEMIES].isDisabled:
                        self.showHint(self._hints[HINT.FLANKENEMIES])
                        self.showMarker(self._markers[MARKER.FLANK_START])
                        self._fallbackStartTime = None
            if self._playerDetected:
                if self._inZoneFlanking:
                    if not self._hints[HINT.FLANKINGFAILS].isActive:
                        self.hideAllMarkers(False)
                        if not self._inZoneEnemiesMapBack:
                            self.showMarker(self._markers[MARKER.FLANK_START])
                            self._fallbackStartTime = None
                        self.showHint(self._hints[HINT.FLANKINGFAILS])
                elif self._inZoneAlliedMapPart:
                    if not self._hints[HINT.FALLBACK].isActive and numOfDetectedManyEnemiesPack >= self._TOO_MANY_ENEMIES_NUM:
                        self.hideAllMarkers(False)
                        self.showHint(self._hints[HINT.FALLBACK])
                        self._fallbackStartTime = BigWorld.time()
                    if self._hints[HINT.FALLBACK].isActive and self._fallbackStartTime is not None:
                        if BigWorld.time() > self._fallbackStartTime + self._ignoreFallbackTimeToShowMarker:
                            if not self._markers[MARKER.FALLBACK].isVisible:
                                if not self._inZoneFallbackDone and not self._inZoneFallbackHidden:
                                    self.showMarker(self._markers[MARKER.FALLBACK])
            if self._markers[MARKER.FALLBACK].isVisible and self._inZoneFallbackDone:
                self._markers[MARKER.FALLBACK].hide()
                self._fallbackStartTime = None
            if self._playerDetected and self._inZoneEnemiesMapBack:
                if self._markers[MARKER.FLANK_START].isVisible:
                    self._markers[MARKER.FLANK_START].hide()
                if self._hints[HINT.FLANKINGFAILS].isActive:
                    self._hints[HINT.FLANKINGFAILS].hide()
                if self._hints[HINT.FALLBACK].isActive:
                    self._hints[HINT.FALLBACK].hide()
            if not self._playerDetected:
                if self._hints[HINT.FALLBACK].isActive:
                    self._hints[HINT.FALLBACK].hide()
            if self._inZoneFlanking and not self._playerDetected:
                if self._hints[HINT.FLANKINGFAILS].isActive:
                    self._hints[HINT.FLANKINGFAILS].hide()
                if self._inZoneStealth_0 and not self._inZoneStealth_1:
                    if self._hints[HINT.FLANKENEMIES].isActive:
                        self._hints[HINT.FLANKENEMIES].hide()
                    self.showMarker(self._markers[MARKER.FLANK_RECON])
                    if not self._hints[HINT.FOLIAGEINTROB].isActive:
                        self.showHint(self._hints[HINT.FOLIAGEINTROB])
                elif not self._inZoneStealth_2:
                    self.showMarker(self._markers[MARKER.FLANK_END])
                    if numOfDetectedManyEnemiesPack > 0:
                        if not self._hints[HINT.FOLIAGEINTROA].isActive:
                            self.showHint(self._hints[HINT.FOLIAGEINTROA])
                if self._inZoneStealth_2:
                    if self._hints[HINT.FOLIAGEINTROA].isActive:
                        self._hints[HINT.FOLIAGEINTROA].hide()
                    if not self._hints[HINT.FLANKINGWAIT].isActive:
                        self.showHint(self._hints[HINT.FLANKINGWAIT])
        if self._progress < PROGRESS.ADVANCE:
            for vehicle in self._vehicleEnemy2ndPackMain:
                if not vehicle.isAlive:
                    self._enemiesAtFlank[vehicle.name] = False

            for vehicle in self._vehicleEnemy2ndPackMain:
                if self._enemiesAtFlank[vehicle.name]:
                    break
            else:
                if self._progress < PROGRESS.ADVANCE:
                    self._progress = PROGRESS.ADVANCE
                    self.hideAllHints()
                    self.hideAllMarkers(False)
        if self._progress == PROGRESS.ADVANCE:
            if self._inZoneFlanking:
                if self._hints[HINT.FLANKINGWAIT].isActive:
                    self._hints[HINT.FLANKINGWAIT].hide()
            if not self._halfWayToBasePassed:
                self.showMarker(self._markers[MARKER.BASE])
            else:
                self.showMarker(self._markers[MARKER.BASE])
                self.showHint(self._hints[HINT.CAPTUREBASE])
                self._progress = PROGRESS.CAPTURE
        if self._progress == PROGRESS.CAPTURE:
            if self._inZoneBase:
                if self._hints[HINT.CAPTUREINPROGRESS].isNotShown:
                    self.showHint(self._hints[HINT.CAPTUREINPROGRESS])
                    self._hints[HINT.CAPTUREINPROGRESS].disable()
            numOfDetectedDefendersPack = 0
            for vehicle in self._detectedEnemiesList:
                if vehicle in self._vehicleEnemyDefendersPack:
                    numOfDetectedDefendersPack += 1

            if not self._inZoneBase and numOfDetectedDefendersPack == 0:
                self.showMarker(self._markers[MARKER.BASE])
                if not self._hints[HINT.CAPTUREBASE].isActive:
                    self.showHint(self._hints[HINT.CAPTUREBASE])
            else:
                if self._markers[MARKER.BASE].isVisible:
                    self._markers[MARKER.BASE].hide()
                if self._hints[HINT.CAPTUREBASE].isActive:
                    self._hints[HINT.CAPTUREBASE].hide()
        if self._progress == PROGRESS.CAPTURE_UNDEFINED:
            if self._progressUndefinedTime <= BigWorld.time():
                self._progress = PROGRESS.CAPTURE_FINAL
        if self._progress == PROGRESS.CAPTURE_FINAL:
            if not self._hints[HINT.CAPTUREBASE].isDisabled and not self._allyAttackersDead and self._allyAttackerAtEnemiesBase:
                self._hints[HINT.CAPTUREBASE].disable()
            if not self._inZoneBase:
                self.showMarker(self._markers[MARKER.BASE])
            elif self._markers[MARKER.BASE].isVisible:
                self._markers[MARKER.BASE].hide()
            if not self._inZoneBase:
                if not self._allyAttackersDead and self._allyAttackerAtEnemiesBase:
                    if not self._hints[HINT.CAPTUREHELP].isActive:
                        self.showHint(self._hints[HINT.CAPTUREHELP])
                elif not self._hints[HINT.CAPTUREBASE].isActive:
                    self.showHint(self._hints[HINT.CAPTUREBASE])
            else:
                if self._hints[HINT.CAPTUREHELP].isActive:
                    self._hints[HINT.CAPTUREHELP].hide()
                if self._hints[HINT.CAPTUREBASE].isActive:
                    self._hints[HINT.CAPTUREBASE].hide()
                if not self._allyAttackersDead and self._allyAttackerAtEnemiesBase:
                    if self._hints[HINT.CAPTURETOGETHER].isNotShown:
                        self.showHint(self._hints[HINT.CAPTURETOGETHER])
        return

    def isAnyHintActive(self):
        return any((self._hints[hintID].isActive for hintID in self._hints))

    def showHint(self, hint):
        self.hideAllHints()
        hint.show()

    def hideAllHints(self):
        for hint in self._hints.itervalues():
            if hint.isActive:
                hint.hide()

    def disableAllHints(self):
        for hint in self._hints.itervalues():
            if hint.isActive:
                hint.hide()
            hint.disable()

    def showMarker(self, marker):
        if marker.isVisible:
            return
        self.hideAllMarkers(False)
        marker.show()

    def hideAllMarkers(self, silently=True):
        for marker in self._markers.itervalues():
            marker.hide(silently)

    def onReceiveDamage(self, targetVehicle):
        if self._inZoneBase and self.playerVehicle().health > 0:
            if not self._hints[HINT.CAPTURELOST].isActive:
                self.showHint(self._hints[HINT.CAPTURELOST])
        if self.playerVehicle().health <= 0:
            self.disableAllHints()

    def onEnemyObserved(self, isObserved):
        if isObserved:
            self._playerDetected = True
            if self._hints[HINT.PLAYERDETECTED].isNotShown:
                self.showHint(self._hints[HINT.PLAYERDETECTED])
        else:
            self._playerDetected = False

    def onPlayerDetectEnemy(self, new, lost):
        if new is not None:
            for vehicle in new:
                if vehicle not in self._detectedEnemiesList and vehicle.isAlive:
                    self._detectedEnemiesList.add(vehicle)

        if lost is not None:
            for vehicle in lost:
                if vehicle in self._detectedEnemiesList:
                    self._detectedEnemiesList.remove(vehicle)

        return

    def onVehicleDestroyed(self, vehicle):
        if vehicle in self._detectedEnemiesList:
            self._detectedEnemiesList.remove(vehicle)

    def onSetConstant(self, vehicle, name, value):
        if name == 'EnemiesRepositionStage':
            if value == 2:
                if vehicle.name in self._enemiesAtFlank.keys():
                    self._enemiesAtFlank[vehicle.name] = False
        elif name == 'AllyAttackerRepositionStage':
            if value == 1:
                self._allyAttackerAtEnemiesBase = True
            elif value == 2:
                if self._progress < PROGRESS.CAPTURE_UNDEFINED:
                    self._progress = PROGRESS.CAPTURE_UNDEFINED
                    self._progressUndefinedTime = BigWorld.time() + 5.0

    def onZoneTriggerActivated(self, name):
        if name == 'FlankingZone_0':
            self._inZoneFlanking = True
        elif name == 'StealthZone_0':
            self._inZoneStealth_0 = True
        elif name == 'StealthZone_1':
            self._inZoneStealth_1 = True
        elif name == 'StealthZone_2':
            self._inZoneStealth_2 = True
        elif name == 'AroundBaseZone_0' or name == 'AroundBaseZone_1' or name == 'AroundBaseZone_2' or name == 'AroundBaseZone_3':
            if self._progress >= PROGRESS.ADVANCE:
                self._halfWayToBasePassed = True
        elif name == 'EnemyBaseZone':
            pass
        if name == 'MapMiddleMarker_Allies':
            self._inZoneAlliedMapPart = True
        elif name == 'MapMiddleMarker_Enemies':
            self._inZoneAlliedMapPart = False
        elif name == 'MapEnemiesBaseMarker_Allies':
            self._inZoneEnemiesMapBack = False
        elif name == 'MapEnemiesBaseMarker_Enemies':
            self._inZoneEnemiesMapBack = True
        elif name == 'FallbackTrigger_back':
            self._inZoneFallbackDone = True
        elif name == 'FallbackTrigger_forth':
            self._inZoneFallbackDone = False
        elif name == 'fallbackTrigger_hiddenZone':
            self._inZoneFallbackHidden = True

    def onZoneTriggerDeactivated(self, name):
        if name == 'FlankingZone_0':
            self._inZoneFlanking = False
        elif name == 'StealthZone_0':
            self._inZoneStealth_0 = False
        elif name == 'StealthZone_1':
            self._inZoneStealth_1 = False
        elif name == 'StealthZone_2':
            self._inZoneStealth_2 = False
        elif name == 'AroundBaseZone_0' or name == 'AroundBaseZone_1' or name == 'AroundBaseZone_2' or name == 'AroundBaseZone_3':
            pass
        elif name == 'EnemyBaseZone':
            pass
        elif name == 'fallbackTrigger_hiddenZone':
            self._inZoneFallbackHidden = False

    def onTeamBasePointsUpdate(self, team, baseID, points, timeLeft, invadersCnt, capturingStopped):
        if team == self._playerVehicle.team:
            return
        if capturingStopped or invadersCnt == 0:
            self._inZoneBase = False
        elif self._progress == PROGRESS.CAPTURE or self._allyAttackersDead or not self._allyAttackerAtEnemiesBase:
            self._inZoneBase = True
        elif self._progress == PROGRESS.CAPTURE_FINAL:
            if invadersCnt > 1:
                self._inZoneBase = True
            else:
                self._inZoneBase = False
        if self._inZoneBase:
            if self._progress < PROGRESS.CAPTURE:
                self.hideAllHints()
                self.hideAllMarkers(False)
                self._progress = PROGRESS.CAPTURE

    def onTeamBaseCaptured(self, team, baseID):
        self.hideAllHints()
        self.hideAllMarkers(False)
