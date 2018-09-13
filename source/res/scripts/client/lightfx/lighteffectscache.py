# Embedded file name: scripts/client/LightFx/LightEffectsCache.py
import ResMgr
import LightEffect

class LightEffectsCache:
    SETTINGS_PATH = 'scripts/alienware_light_fx.xml'
    __ACTION_MAPPING = {'Morph': 1,
     'Pulse': 2,
     'Color': 3}
    __lightEffects = {}

    @staticmethod
    def allEffects():
        return LightEffectsCache.__lightEffects

    @staticmethod
    def load():
        settingsSection = ResMgr.openSection(LightEffectsCache.SETTINGS_PATH)
        lightEffectsDesc = (section for section in settingsSection.values() if section.name == 'lightEffect')
        for lightEffectSection in lightEffectsDesc:
            LightEffectsCache.__addLightEffect(lightEffectSection)

    @staticmethod
    def __parseDescriptions(descriptionStr):
        descriptions = descriptionStr.split(',')
        result = []
        for descriptionStr in descriptions:
            result.append(descriptionStr.strip())

        return result

    @staticmethod
    def __addLightEffect(lightEffectSection):
        name = lightEffectSection.readString('name')
        duration = lightEffectSection.readFloat('duration')
        if duration == -1:
            duration = None
        lightActions = {}
        for section in lightEffectSection.values():
            if section.name == 'light':
                lightDescriptions = LightEffectsCache.__parseDescriptions(section.readString('lightDescription'))
                for lightDescription in lightDescriptions:
                    color = section.readVector4('color')
                    action = LightEffectsCache.__ACTION_MAPPING[section.readString('action')]
                    lightActions[lightDescription] = LightEffect.OneLightAction(lightDescription, color, action)

        LightEffectsCache.__lightEffects[name] = LightEffect.LightEffect(name, lightActions, duration)
        return

    @staticmethod
    def getEffect(effectName):
        return LightEffectsCache.__lightEffects[effectName]
