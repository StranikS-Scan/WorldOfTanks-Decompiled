# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bwobsolete_weather.py
import BigWorld
import ResMgr
import FX
import random
from functools import partial
import traceback
import Bloom
from Listener import Listenable
import Math
if BigWorld.component != 'editor':
    import game as Personality
else:
    import Personality
if BigWorld.component != 'editor':
    weatherXML = ResMgr.openSection('scripts/data/weather.xml')
else:
    weatherXML = ResMgr.openSection('scripts/data/weather.xml', True)

class WeatherSystem():

    def __init__(self, ds):
        self.name = ds.name
        self.skyBoxes = list(ds.readStrings('skyBox'))
        self.skyBoxModels = []
        self.rain = ds.readFloat('rain', 0.0)
        self.sun = ds.readVector4('sun', (1, 1, 1, 1))
        self.ambient = ds.readVector4('ambient', (1, 1, 1, 1))
        self.fog = ds.readVector4('fog', (1, 1, 1, 1))
        self.windSpeed = ds.readVector2('windSpeed', (0.0, 0.0))
        self.windGustiness = ds.readFloat('windGustiness', 0.0)
        self.skyBoxFogFactor = ds.readFloat('fogFactor', 0.15)
        self.bloom = ds['bloom']
        self.bloomPreset = ds.readString('bloom', 'Standard')
        self.fader = Math.Vector4Morph()
        self.fader.duration = 1.0
        f = self._fogAmount(self.fog[3])
        self.fader.target = (f,
         0,
         1,
         0)
        self.fx = None
        self.fxName = ds.readString('sfx')
        self.loaded = False
        return

    def _loadSkyBoxes(self, callback=None, immediate=False):
        if self.loaded:
            if callback:
                callback()
        elif not immediate:
            BigWorld.loadResourceListBG(self.skyBoxes, partial(self._onLoadSkyBoxes, callback))
        else:
            resourceRefs = {}
            for i in self.skyBoxes:
                try:
                    resourceRefs[i] = BigWorld.Model(i)
                except ValueError:
                    resourceRefs[i] = BigWorld.Model('')

            self._onLoadSkyBoxes(callback, resourceRefs)

    def _onLoadSkyBoxes(self, callback, resourceRef):
        self.loaded = True
        for sb in self.skyBoxes:
            try:
                self.skyBoxModels.append(resourceRef[sb])
            except ValueError:
                self.skyBoxModels.append(BigWorld.Model(''))

        if callback != None:
            callback()
        return

    def _unload(self):
        for i in self.skyBoxModels:
            BigWorld.delSkyBox(i, self.fader)

        self.skyBoxModels = []
        if self.fx != None:
            self.fx.detach()
            self.fx = None
        self.loaded = False
        return

    def _loadFX(self, callback=None):
        if self.fxName != '':
            BigWorld.loadResourceListBG(FX.prerequisites(self.fxName), partial(self._onLoadFX, callback))
        elif callback:
            callback()

    def _onLoadFX(self, callback, resourceRef):
        if self.fx != None:
            self.fx.detach()
            self.fx = None
        if self.loaded:
            self.fx = FX.Persistent(self.fxName, resourceRef)
            if BigWorld.component == 'editor':
                self.fx.attach(None)
            else:
                self.fx.attach(BigWorld.player())
            self.fx.go()
            if callback:
                callback()
        return

    def _fadeOutFX(self):
        return self.fx.stop() if self.fx != None else 0.0

    def fadeIn(self, fadingIn, fadeSpeed, immediate=False):
        curr = self.fader.value
        if fadingIn:
            if not self.loaded:
                print "calling fadeIn on a weather system that isn't loaded.  please call prepareResources() first", self.name
                traceback.print_stack()
                return
            for sb in self.skyBoxModels:
                if sb != None:
                    BigWorld.addSkyBox(sb, self.fader)

            f = self._fogAmount(self.fog[3])
            self.fader.duration = fadeSpeed - 0.1
            self.fader.target = (f,
             0,
             1,
             1)
            try:
                BigWorld.weather().windAverage(self.windSpeed[0], self.windSpeed[1])
                BigWorld.weather().windGustiness(self.windGustiness)
            except ValueError:
                pass
            except EnvironmentError:
                pass

            if self.bloom:
                Bloom.loadStyle(self.bloom, fadeSpeed)
            else:
                Bloom.selectPreset(self.bloomPreset, fadeSpeed)
        elif self.loaded:
            sfxFadeSpeed = self._fadeOutFX()
            if not immediate:
                fadeSpeed = max(fadeSpeed, sfxFadeSpeed)
            BigWorld.callback(fadeSpeed, self._unload)
            self.fader.duration = fadeSpeed - 0.1
            self.fader.target = (curr[0],
             curr[1],
             curr[2],
             0)
        return

    def _fogAmount(self, amount):
        return (amount - 1.0) * self.skyBoxFogFactor

    def prepareResources(self, callback=None, immediate=False):
        if not self.loaded:
            self._loadSkyBoxes(partial(self._loadFX, callback), immediate)
        elif callback:
            callback()

    def setFadeSpeed(self, duration):
        self.fader.duration = duration

    def edUnloadSkyBoxes(self):
        for sb in self.skyBoxModels:
            if sb != None:
                BigWorld.delSkyBox(sb, self.fader)

        return

    def edReloadSkyBoxes(self):
        self.tempCopy = self.skyBoxModels
        self.skyBoxModels = []
        for sb in self.skyBoxes:
            try:
                model = BigWorld.Model(sb)
            except ValueError:
                model = BigWorld.Model('')

            self.skyBoxModels.append(model)
            BigWorld.addSkyBox(model, self.fader)


class Weather(Listenable):

    def __init__(self):
        Listenable.__init__(self)
        self.fadeSpeed = 15.0
        self.system = None
        self.randomWeatherCallback = None
        self.summoning = False
        self.pendingWeatherChange = None
        self.localOverride = None
        self.overridenWeather = None
        self.onChangeSpace()
        return

    def toggleRandomWeather(self, force=None):
        if force != None:
            turningOff = not force
        else:
            turningOff = self.randomWeatherCallback != None
        stateChanged = False
        wasOn = self.randomWeatherCallback != None
        if turningOff and self.randomWeatherCallback != None:
            BigWorld.cancelCallback(self.randomWeatherCallback)
            self.randomWeatherCallback = None
            stateChanged = wasOn
        elif not turningOff:
            self._randomWeather(True)
            stateChanged = not wasOn
        if stateChanged:
            Personality.addChatMsg(-1, 'Random weather turned ' + ('on', 'off')[turningOff])
        return

    def isWeatherRandom(self):
        return self.randomWeatherCallback != None

    def nextWeatherSystem(self, direction, immediate=False):
        systems = self._weatherSystemsForCurrentSpace()
        idx = 0
        if self.system != None:
            for s in systems:
                if s.name == self.system.name:
                    break
                idx += 1

        if direction:
            idx += 1
        else:
            idx -= 1
        self.toggleRandomWeather(False)
        self.summon(systems[idx % len(systems)].name, immediate)
        return

    def _randomWeather(self, initial=False):
        if initial or self.randomWeatherCallback != None:
            self.randomWeatherCallback = BigWorld.callback(60.0, self._randomWeather)
            systems = self._weatherSystemsForCurrentSpace()
            ds = random.choice(systems)
            self.summon(ds.name)
        return

    def _setFadeSpeed(self, duration):
        self.fadeSpeed = max(0.1, duration)
        self.weatherController.duration = self.fadeSpeed
        self.sunlightController.duration = self.fadeSpeed
        self.ambientController.duration = self.fadeSpeed
        self.fogController.duration = self.fadeSpeed
        if self.system:
            self.system.setFadeSpeed(self.fadeSpeed)

    def _weatherSystemsForCurrentSpace(self):
        systems = weatherXML.values()
        return systems

    def onChangeSpace(self, spaceID=-1, spaceSettings=None):
        self.currentSpaceID = spaceID
        m = Math.Vector4Morph()
        m.duration = self.fadeSpeed
        m.target = (0, 0, 0, 0)
        m.time = m.duration
        BigWorld.weatherController(m)
        self.weatherController = m
        m = Math.Vector4Morph()
        m.duration = self.fadeSpeed
        m.target = (1, 1, 1, 1)
        m.time = m.duration
        BigWorld.sunlightController(m)
        self.sunlightController = m
        m = Math.Vector4Morph()
        m.duration = self.fadeSpeed
        m.target = (1, 1, 1, 1)
        m.time = m.duration
        BigWorld.ambientController(m)
        self.ambientController = m
        m = Math.Vector4Morph()
        m.duration = self.fadeSpeed
        m.target = (1, 1, 1, 1)
        m.time = m.duration
        BigWorld.fogController(m)
        self.fogController = m

    def summon(self, systemName, immediate=False, serverSync=False, resummon=False):
        if self.localOverride != None:
            self.overridenWeather = systemName
            systemName = self.localOverride
        if not resummon and self.system and self.system.name == systemName:
            return
        else:
            if resummon:
                self._setFadeSpeed(0.1)
            elif immediate:
                self._setFadeSpeed(2.5)
            else:
                self._setFadeSpeed(15.0)
            if self.summoning and not immediate:
                self.pendingWeatherChange = systemName
                self.listeners.weather(systemName=systemName)
                return
            for ds in weatherXML.values():
                if ds.name == systemName:
                    try:
                        if not serverSync and BigWorld.getEnvironmentSync():
                            p = BigWorld.player()
                            p.cell.syncServWeather(p.spaceID, systemName)
                    except KeyError:
                        pass
                    except AttributeError:
                        pass

                    system = WeatherSystem(ds)
                    self.summoning = True
                    self.listeners.weather(system=system)
                    system.prepareResources(partial(self._systemReadySummon, system, immediate, resummon), immediate)

            return

    def override(self, systemName, immediate=False):
        if systemName == None or systemName == '':
            self.localOverride = None
            self.summon(self.overridenWeather, immediate, serverSync=False, resummon=False)
            self.overridenWeather = None
        else:
            self.overridenWeather = self.system.name
            self.summon(systemName, immediate, serverSync=False, resummon=False)
            self.localOverride = systemName
        return

    def _systemReadySummon(self, system, immediate, resummon):
        if self.system:
            self.system.fadeIn(False, self.fadeSpeed, immediate)
            self.system = None
        if system != None:
            self.system = system
            self.system.fadeIn(True, self.fadeSpeed)
            self.skyBoxFogFactor = system.skyBoxFogFactor
            self.rain(system.rain)
            self.ambient(system.ambient)
            self.fog(system.fog, False)
            self.sun(system.sun)
            BigWorld.callback(self.fadeSpeed, self._onSystemSummoned)
        else:
            self._onSystemSummoned()
        return

    def _onSystemSummoned(self):
        self.listeners.weather(system=self.system)
        self.summoning = False
        if self.pendingWeatherChange != None:
            self.summon(self.pendingWeatherChange)
            self.pendingWeatherChange = None
        return

    def newSystemByName(self, systemName):
        for ds in weatherXML.values():
            if ds.name == systemName:
                system = WeatherSystem(ds)
                return system

        return None

    def _animateValue(self, value, v4a, index):
        expected = Math.Vector4(v4a.target)
        expected[index] = value
        v4a.target = expected

    def _animateVector4(self, v4a, value):
        v4a.target = value

    def rain(self, amount):
        self._animateValue(amount, self.weatherController, 0)

    def fog(self, value, applyToSystem=True):
        self._animateVector4(self.fogController, value)
        if applyToSystem:
            fogAmount = value[3]
            self._animateValue(self.system._fogAmount(fogAmount), self.system.fader, 0)

    def sun(self, value):
        value *= value.w
        value.w = 1.0
        self._animateVector4(self.sunlightController, value)

    def ambient(self, value):
        value *= value.w
        value.w = 1.0
        self._animateVector4(self.ambientController, value)


s_weather = None

def weather():
    global s_weather
    if not s_weather:
        s_weather = Weather()
    return s_weather


def fini():
    global s_weather
    if s_weather is not None:
        Personality.delCameraSpaceChangeListener(s_weather.onChangeSpace)
        s_weather = None
    return
