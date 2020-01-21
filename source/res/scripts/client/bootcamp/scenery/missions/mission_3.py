# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/scenery/missions/mission_3.py
import BigWorld
from bootcamp.scenery.AbstractMission import AbstractMission
from bootcamp.BootcampConstants import HINT_TYPE
from helpers.i18n import makeString
from debug_utils import LOG_ERROR

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
    FLANKINGFAILS2 = 16
    INIT_PARAMS = {PLAYERDETECTED: {'message': makeString('#bootcamp:hint/mission3/playerdetected'),
                      'hintTypeId': HINT_TYPE.HINT_B3_YOU_ARE_DETECTED,
                      'timeStartDelay': 2.5,
                      'timeDuration': 8.0,
                      'voiceover': 'vo_bc_you_are_detected'},
     FINDMOREENEMIES: {'message': makeString('#bootcamp:hint/mission3/findmoreenemies'),
                       'timeStartDelay': 1.0,
                       'timeDuration': 4.5,
                       'timeInnerCooldown': 15.0},
     FALLBACK: {'message': makeString('#bootcamp:hint/mission3/fallback'),
                'hintTypeId': HINT_TYPE.HINT_B3_FALL_BACK,
                'voiceover': 'vo_bc_retreat'},
     FLANKENEMIES: {'message': makeString('#bootcamp:hint/mission3/flankenemies'),
                    'hintTypeId': HINT_TYPE.HINT_B3_FLANK,
                    'voiceover': 'vo_bc_get_around_on_flank'},
     FOLIAGEINTROA: {'message': makeString('#bootcamp:hint/mission3/foliageintroa'),
                     'hintTypeId': HINT_TYPE.HINT_B3_FOLIAGE2,
                     'voiceover': 'vo_bc_do_not_shoot'},
     FOLIAGEINTROB: {'message': makeString('#bootcamp:hint/mission3/foliageintrob'),
                     'hintTypeId': HINT_TYPE.HINT_B3_FOLIAGE,
                     'voiceover': 'vo_bc_bushes_hide'},
     FOLIAGEKEEPMOVING: {'message': makeString('#bootcamp:hint/mission3/foliagekeepmoving'),
                         'hintTypeId': HINT_TYPE.HINT_B3_FOLIAGE,
                         'voiceover': 'vo_bc_move_forward'},
     FOLIAGECANTDETECT: {'message': makeString('#bootcamp:hint/mission3/foliagecantdetect'),
                         'timeDuration': 4.5,
                         'timeInnerCooldown': 15.0},
     FLANKINGFAILS: {'message': makeString('#bootcamp:hint/mission3/flankingfails'),
                     'hintTypeId': HINT_TYPE.HINT_B3_YOU_ARE_DETECTED,
                     'voiceover': 'vo_bc_shooting_unmask'},
     FLANKINGFAILS2: {'message': makeString('#bootcamp:hint/mission3/flankingfails2'),
                      'hintTypeId': HINT_TYPE.HINT_B3_YOU_ARE_DETECTED,
                      'voiceover': 'vo_bc_retreat'},
     FLANKINGWAIT: {'message': makeString('#bootcamp:hint/mission3/flankingwait'),
                    'timeDuration': -1.0,
                    'timeStartDelay': 3.0},
     CAPTUREBASE: {'message': makeString('#bootcamp:hint/mission3/capturebase'),
                   'hintTypeId': HINT_TYPE.HINT_B3_DO_CAPTURE,
                   'voiceover': 'vo_bc_capture_base'},
     CAPTUREWATCHOUT: {'message': makeString('#bootcamp:hint/mission3/capturewatchout'),
                       'hintTypeId': HINT_TYPE.HINT_B3_ENEMIES_HIDDEN,
                       'timeDuration': 8.0,
                       'voiceover': 'vo_bc_enemy_can_hide_be_careful'},
     CAPTURELOST: {'message': makeString('#bootcamp:hint/mission3/capturelost'),
                   'hintTypeId': HINT_TYPE.HINT_B3_CAPTURE_RESET,
                   'timeDuration': 8.0,
                   'voiceover': 'vo_bc_progress_capturing'},
     CAPTURETOGETHER: {'message': makeString('#bootcamp:hint/mission3/capturetogether'),
                       'hintTypeId': HINT_TYPE.HINT_B3_CAPTURE_TOGETHER,
                       'timeDuration': 8.0,
                       'voiceover': 'vo_bc_capture_speed'},
     CAPTUREHELP: {'message': makeString('#bootcamp:hint/mission3/capturehelp'),
                   'hintTypeId': HINT_TYPE.HINT_B3_DO_CAPTURE,
                   'voiceover': 'vo_bc_return_and_help'},
     CAPTUREINPROGRESS: {'message': makeString('#bootcamp:hint/mission3/captureinprogress'),
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
    COUNT = 6


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


class ZONES(object):
    FLANKING = 0
    STEALTH_0 = 1
    STEALTH_1 = 2
    STEALTH_2 = 3
    BASE = 4
    BASE_DRAFT = 5
    ALLIED_MAP_PART = 6
    ENEMIES_MAP_BACK = 7
    FALLBACK_DONE = 8
    FALLBACK_HIDDEN = 9
    ZONE_SIZE = 10
    PARAMS = {'FlankingZone_0': (FLANKING, True, False),
     'StealthZone_0': (STEALTH_0, True, False),
     'StealthZone_1': (STEALTH_1, True, False),
     'StealthZone_2': (STEALTH_2, True, False),
     'MapMiddleMarker_Allies': (ALLIED_MAP_PART, True, None),
     'MapMiddleMarker_Enemies': (ALLIED_MAP_PART, False, None),
     'MapEnemiesBaseMarker_Allies': (ENEMIES_MAP_BACK, False, None),
     'MapEnemiesBaseMarker_Enemies': (ENEMIES_MAP_BACK, True, None),
     'FallbackTrigger_back': (FALLBACK_DONE, True, None),
     'FallbackTrigger_forth': (FALLBACK_DONE, False, None),
     'fallbackTrigger_hiddenZone': (FALLBACK_HIDDEN, True, False),
     'EnemyBaseZone': (BASE_DRAFT, True, False)}


class Mission3(AbstractMission):
    _TOO_MANY_ENEMIES_NUM = 3
    _DETECTION_DELAY = 1.0

    def __init__(self, assistant):
        super(Mission3, self).__init__(assistant)
        self._hints = {v:self.createHint(**HINT.INIT_PARAMS[v]) for k, v in HINT.__dict__.iteritems() if isinstance(v, int)}
        self._markers = {v:self.createMarker(MARKER.INIT_PARAMS[v]) for k, v in MARKER.__dict__.iteritems() if isinstance(v, int)}
        self._updaters = ([self.updateStateStart, self.updateStateBeforeAdvance],
         [self.updateStateFlank_ProcessFallback, self.updateStateFlank_ProcessFlank, self.updateStateBeforeAdvance],
         [self.updateStateAdvance],
         [self.updateSateCapture],
         [self.updateStateCaptureUndefined],
         [self.updateStateCaptureFinal])
        if len(self._updaters) != PROGRESS.COUNT:
            LOG_ERROR('Wrong updaters list size( see PROGRESS class )')
        self._playerVehicle = self.playerVehicle()
        self._vehicleEnemy1stPack = [ self.createVehicle(name) for name in ('Miron Nebaluiev', 'Fridrih Simann', 'Matt Underlay') ]
        self._vehicleEnemy2ndPackMain = [ self.createVehicle(name) for name in ('James Brounge', 'Oda Nisura', 'Gavril Stolbov', 'Fabian Haupt') ]
        self._vehicleEnemy2ndPackSecondary = [ self.createVehicle(name) for name in ('Frank Dimmelton', 'John Dicker') ]
        self._vehicleEnemy2ndPackAll = self._vehicleEnemy2ndPackMain + self._vehicleEnemy2ndPackSecondary
        self._vehicleEnemyRepositionToDefendersPack = [self.createVehicle('Fabian Haupt')]
        self._vehicleEnemyDefendersPack = [self.createVehicle('Konrad Cerstvy')]
        self._vehicleAlliesDefendersPack = [ self.createVehicle(name) for name in ('Richard Bogelber', 'Keiko Simura', 'Sheng En') ]
        self._vehicleAlliesAttackersPack = [self.createVehicle('Siegward Eber')]
        self._enemiesAtFlank = {}
        self._detectedEnemiesList = set()
        self._allyAttackersDead = False
        self._allyAttackerAtEnemiesBase = False
        self._defendersFromCenterRepos = False
        self._playerDetected = False
        self._progressUndefinedTime = 0.0
        self._inZoneData = [False] * ZONES.ZONE_SIZE
        self._inZoneData[ZONES.ALLIED_MAP_PART] = True
        self._inZoneData[ZONES.FALLBACK_DONE] = True
        self._inZoneData[ZONES.FALLBACK_HIDDEN] = True
        self._halfWayToBasePassed = False
        self._progress = PROGRESS.START
        self._fallbackStartTime = None
        self._ignoreFallbackTimeToShowMarker = 15.0
        self._numOfDetectedManyEnemiesPack = 0
        self._playLastShotTime = None
        return

    def start(self):
        self.hideAllMarkers()
        for vehicle in self._vehicleEnemy2ndPackMain:
            self._enemiesAtFlank[vehicle.name] = True

        super(Mission3, self).start()
        self.playSound2D('vo_bc_detect_enemy_vehicles')
        self.playSound2D('bc_main_tips_task_start')

    def destroy(self):
        super(Mission3, self).destroy()
        self._updaters = None
        return

    def updateStateStart(self):
        if self._hints[HINT.FALLBACK].isNotShown:
            firstPackKilled = True
            for vehicle in self._vehicleEnemy1stPack:
                if vehicle.isAlive:
                    firstPackKilled = False

            if firstPackKilled:
                self.showMarker(MARKER.RECON)
        if self._playerDetected and not self._inZoneData[ZONES.FLANKING]:
            if self._numOfDetectedManyEnemiesPack >= self._TOO_MANY_ENEMIES_NUM:
                if not self._hints[HINT.FALLBACK].isActive and not self._hints[HINT.FALLBACK].isDisabled:
                    self.showHint(HINT.FALLBACK)
                    self.hideMarker(MARKER.RECON, False)
                    self._progress = PROGRESS.FLANK
                    self._fallbackStartTime = BigWorld.serverTime()
                    self._playCombatMusic()
        if self._inZoneData[ZONES.STEALTH_1] and not self._playerDetected:
            self._progress = PROGRESS.FLANK
            self._playCombatMusic()

    def updateStateFlank_ProcessFallback(self):
        if self._playerDetected and self._inZoneData[ZONES.ALLIED_MAP_PART] and not self._inZoneData[ZONES.FLANKING]:
            if not self._hints[HINT.FALLBACK].isActive and self._numOfDetectedManyEnemiesPack >= self._TOO_MANY_ENEMIES_NUM:
                self.hideAllMarkers(False)
                self.showHint(HINT.FALLBACK)
                self._fallbackStartTime = BigWorld.serverTime()
            if not self._inZoneData[ZONES.FALLBACK_DONE] and not self._inZoneData[ZONES.FALLBACK_HIDDEN]:
                if self._hints[HINT.FALLBACK].isActive and self._fallbackStartTime is not None:
                    if BigWorld.serverTime() > self._fallbackStartTime + self._ignoreFallbackTimeToShowMarker:
                        if not self.isMarkerVisible(MARKER.FALLBACK):
                            self.showMarker(MARKER.FALLBACK)
        if self.isMarkerVisible(MARKER.FALLBACK) and self._inZoneData[ZONES.FALLBACK_DONE]:
            self.hideMarker(MARKER.FALLBACK, False)
            self._fallbackStartTime = None
        if not self._playerDetected:
            if self._hints[HINT.FALLBACK].isActive:
                self.hideHint(HINT.FALLBACK)
        return

    def updateStateFlank_ProcessFlank(self):
        if not self._playerDetected or self._numOfDetectedManyEnemiesPack < self._TOO_MANY_ENEMIES_NUM:
            if not self._inZoneData[ZONES.FLANKING] and self._inZoneData[ZONES.ALLIED_MAP_PART]:
                if not self._hints[HINT.FLANKENEMIES].isActive and not self._hints[HINT.FLANKENEMIES].isDisabled:
                    self.showHint(HINT.FLANKENEMIES)
                    self.showMarker(MARKER.FLANK_START)
                    self._fallbackStartTime = None
        if self._playerDetected and self._inZoneData[ZONES.FLANKING]:
            if not self._hints[HINT.FLANKINGFAILS].isActive and not self._hints[HINT.FLANKINGFAILS2].isActive:
                if not self._markers[MARKER.FLANK_START].isVisible or self._inZoneData[ZONES.ENEMIES_MAP_BACK]:
                    self.hideAllMarkers(False)
                if not self._inZoneData[ZONES.ENEMIES_MAP_BACK]:
                    self.showMarker(MARKER.FLANK_START)
                    self._fallbackStartTime = None
                if self._playLastShotTime:
                    if BigWorld.serverTime() < self._playLastShotTime + self._DETECTION_DELAY:
                        self.showHint(HINT.FLANKINGFAILS)
                    else:
                        self.showHint(HINT.FLANKINGFAILS2)
        if self._playerDetected and self._inZoneData[ZONES.ENEMIES_MAP_BACK]:
            if self.isMarkerVisible(MARKER.FLANK_START):
                self.hideMarker(MARKER.FLANK_START, False)
            if self._hints[HINT.FLANKINGFAILS].isActive:
                self.hideHint(HINT.FLANKINGFAILS)
            if self._hints[HINT.FLANKINGFAILS2].isActive:
                self.hideHint(HINT.FLANKINGFAILS2)
            if self._hints[HINT.FALLBACK].isActive:
                self.hideHint(HINT.FALLBACK)
        if not self._playerDetected and self._inZoneData[ZONES.FLANKING]:
            if self._hints[HINT.FLANKINGFAILS].isActive:
                self.hideHint(HINT.FLANKINGFAILS)
            if self._hints[HINT.FLANKINGFAILS2].isActive:
                self.hideHint(HINT.FLANKINGFAILS2)
            if self._inZoneData[ZONES.STEALTH_0] and not self._inZoneData[ZONES.STEALTH_1]:
                if self._hints[HINT.FLANKENEMIES].isActive:
                    self.hideHint(HINT.FLANKENEMIES)
                self.showMarker(MARKER.FLANK_RECON)
                if not self._hints[HINT.FOLIAGEINTROB].isActive:
                    self.showHint(HINT.FOLIAGEINTROB)
            elif not self._inZoneData[ZONES.STEALTH_2]:
                self.showMarker(MARKER.FLANK_END)
                if self._numOfDetectedManyEnemiesPack > 0:
                    if not self._hints[HINT.FOLIAGEINTROA].isActive:
                        self.showHint(HINT.FOLIAGEINTROA)
            if self._inZoneData[ZONES.STEALTH_2]:
                if self._hints[HINT.FOLIAGEINTROA].isActive:
                    self.hideHint(HINT.FOLIAGEINTROA)
                if not self._hints[HINT.FLANKINGWAIT].isActive:
                    self.showHint(HINT.FLANKINGWAIT)
        return

    def updateStateBeforeAdvance(self):
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

    def updateStateAdvance(self):
        if self._inZoneData[ZONES.FLANKING]:
            if self._hints[HINT.FLANKINGWAIT].isActive:
                self.hideHint(HINT.FLANKINGWAIT)
        if not self._halfWayToBasePassed:
            self.showMarker(MARKER.BASE)
        else:
            self.showMarker(MARKER.BASE)
            self.showHint(HINT.CAPTUREBASE)
            self._progress = PROGRESS.CAPTURE

    def updateSateCapture(self):
        if self._inZoneData[ZONES.BASE]:
            if self._hints[HINT.CAPTUREINPROGRESS].isNotShown:
                self.showHint(HINT.CAPTUREINPROGRESS)
                self._hints[HINT.CAPTUREINPROGRESS].disable()
        numOfDetectedDefendersPack = 0
        for vehicle in self._detectedEnemiesList:
            if vehicle in self._vehicleEnemyDefendersPack or self._defendersFromCenterRepos and vehicle in self._vehicleEnemyRepositionToDefendersPack:
                numOfDetectedDefendersPack += 1

        if not self._inZoneData[ZONES.BASE] and numOfDetectedDefendersPack == 0:
            self.showMarker(MARKER.BASE)
            if not self._hints[HINT.CAPTUREBASE].isActive:
                self.showHint(HINT.CAPTUREBASE)
        else:
            if self.isMarkerVisible(MARKER.BASE):
                self.hideMarker(MARKER.BASE, False)
            if self._hints[HINT.CAPTUREBASE].isActive:
                self.hideHint(HINT.CAPTUREBASE)

    def updateStateCaptureUndefined(self):
        if self._progressUndefinedTime <= BigWorld.serverTime():
            self._progress = PROGRESS.CAPTURE_FINAL

    def updateStateCaptureFinal(self):
        if not self._hints[HINT.CAPTUREBASE].isDisabled and not self._allyAttackersDead and self._allyAttackerAtEnemiesBase:
            self._hints[HINT.CAPTUREBASE].disable()
        if not self._inZoneData[ZONES.BASE]:
            self.showMarker(MARKER.BASE)
            if not self._allyAttackersDead and self._allyAttackerAtEnemiesBase:
                if not self._hints[HINT.CAPTUREHELP].isActive:
                    self.showHint(HINT.CAPTUREHELP)
            elif not self._hints[HINT.CAPTUREBASE].isActive:
                self.showHint(HINT.CAPTUREBASE)
        else:
            if self.isMarkerVisible(MARKER.BASE):
                self.hideMarker(MARKER.BASE, False)
            if self._hints[HINT.CAPTUREHELP].isActive:
                self.hideHint(HINT.CAPTUREHELP)
            if self._hints[HINT.CAPTUREBASE].isActive:
                self.hideHint(HINT.CAPTUREBASE)
            if not self._allyAttackersDead and self._allyAttackerAtEnemiesBase:
                if self._hints[HINT.CAPTURETOGETHER].isNotShown:
                    self.showHint(HINT.CAPTURETOGETHER)

    def update(self):
        super(Mission3, self).update()
        self._numOfDetectedManyEnemiesPack = 0
        for vehicle in self._detectedEnemiesList:
            if vehicle in self._vehicleEnemy2ndPackAll:
                self._numOfDetectedManyEnemiesPack += 1

        if not self._allyAttackersDead:
            for vehicle in self._vehicleAlliesAttackersPack:
                if vehicle.isAlive:
                    break
            else:
                self._allyAttackersDead = True

        if self._progress >= PROGRESS.COUNT:
            LOG_ERROR('Wrong progress index', self._progress)
            self._progress = PROGRESS.START
        updaters = self._updaters[self._progress]
        for updater in updaters:
            updater()

    def showHint(self, hintID):
        self.hideAllHints()
        hint = self._hints[hintID]
        hint.show()

    def hideHint(self, hintID):
        hint = self._hints[hintID]
        if hint.isActive:
            hint.hide()

    def hideAllHints(self):
        for hint in self._hints.itervalues():
            if hint.isActive:
                hint.hide()

    def disableAllHints(self):
        for hint in self._hints.itervalues():
            if hint.isActive:
                hint.hide()
            hint.disable()

    def showMarker(self, markerID):
        marker = self._markers[markerID]
        if marker.isVisible:
            return
        self.hideAllMarkers(False)
        marker.show()

    def hideMarker(self, markerID, silently=True):
        marker = self._markers[markerID]
        marker.hide(silently)

    def hideAllMarkers(self, silently=True):
        for marker in self._markers.itervalues():
            marker.hide(silently)

    def isMarkerVisible(self, markerID):
        marker = self._markers[markerID]
        return marker.isVisible

    def onReceiveDamage(self, targetVehicle):
        if self._inZoneData[ZONES.BASE] and self.playerVehicle().health > 0:
            if targetVehicle and self._playerVehicle.team != targetVehicle.team:
                if not self._hints[HINT.CAPTURELOST].isActive:
                    self.showHint(HINT.CAPTURELOST)
        if self.playerVehicle().health <= 0:
            self.disableAllHints()

    def onEnemyObserved(self, isObserved):
        if isObserved:
            self._playerDetected = True
            self.__showHintPlayerDetected()
        else:
            self._playerDetected = False

    def onPlayerDetectEnemy(self, new, lost):
        if new is not None:
            for vehicle in new:
                if vehicle not in self._detectedEnemiesList and vehicle.isAlive:
                    self._detectedEnemiesList.add(vehicle)

            self.__showHintPlayerDetected()
        if lost is not None:
            for vehicle in lost:
                if vehicle in self._detectedEnemiesList:
                    self._detectedEnemiesList.remove(vehicle)

        return

    def onVehicleDestroyed(self, vehicle):
        if vehicle in self._detectedEnemiesList:
            self._detectedEnemiesList.remove(vehicle)

    def onPlayerShoot(self, aimInfo):
        self._playLastShotTime = BigWorld.serverTime()

    def onSetConstant(self, vehicle, name, value):
        if name == 'EnemiesRepositionStage':
            if value == 2:
                if vehicle.name in self._enemiesAtFlank.keys():
                    self._enemiesAtFlank[vehicle.name] = False
        elif name == 'DefendersRepositionStage':
            if value == 1:
                self._defendersFromCenterRepos = True
        elif name == 'AllyAttackerRepositionStage':
            if value == 1:
                self._allyAttackerAtEnemiesBase = True
            elif value == 2:
                if self._progress < PROGRESS.CAPTURE_UNDEFINED:
                    self._progress = PROGRESS.CAPTURE_UNDEFINED
                    self._progressUndefinedTime = BigWorld.serverTime() + 5.0

    def onTeamBasePointsUpdate(self, team, baseID, points, timeLeft, invadersCnt, capturingStopped):
        if team == self._playerVehicle.team:
            return
        if capturingStopped or invadersCnt == 0:
            self._inZoneData[ZONES.BASE] = False
        elif self._progress == PROGRESS.CAPTURE or self._allyAttackersDead or not self._allyAttackerAtEnemiesBase:
            self._inZoneData[ZONES.BASE] = True
        elif self._progress == PROGRESS.CAPTURE_FINAL:
            if invadersCnt > 1 or self._inZoneData[ZONES.BASE_DRAFT] and invadersCnt > 0:
                self._inZoneData[ZONES.BASE] = True
            else:
                self._inZoneData[ZONES.BASE] = False
        if self._inZoneData[ZONES.BASE]:
            if self._progress < PROGRESS.CAPTURE:
                self.hideAllHints()
                self.hideAllMarkers(False)
                self._progress = PROGRESS.CAPTURE

    def onTeamBaseCaptured(self, team, baseID):
        self.hideAllHints()
        self.hideAllMarkers(False)

    def onZoneTriggerActivated(self, name):
        if name == 'AroundBaseZone_0' or name == 'AroundBaseZone_1' or name == 'AroundBaseZone_2' or name == 'AroundBaseZone_3':
            if self._progress >= PROGRESS.ADVANCE:
                self._halfWayToBasePassed = True
        data = ZONES.PARAMS.get(name, None)
        if data:
            idx, value, _ = data
            if value is not None:
                self._inZoneData[idx] = value
        return

    def onZoneTriggerDeactivated(self, name):
        data = ZONES.PARAMS.get(name, None)
        if data:
            idx, _, value = data
            if value is not None:
                self._inZoneData[idx] = value
        return

    def __showHintPlayerDetected(self):
        if self._hints[HINT.PLAYERDETECTED].isNotShown:
            self.showHint(HINT.PLAYERDETECTED)
