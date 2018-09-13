# Embedded file name: scripts/client/Vibroeffects/EffectsSettings.py
import ResMgr

class EffectsSettings:
    DELAY_BETWEEN_EFFECTS = 0.1
    COUNT_INFINITY = 4294967295L
    CFG_FOLDER = 'vibroeffects/'
    AccelerationThreshold = 0.0
    DecelerationThreshold = 0.0

    class Groups:
        ENGINE = 'engine'
        ACCELERATION = 'acceleration'
        SHOTS = 'shots'
        HITS = 'hits'
        DAMAGE = 'damage'
        GUI = 'gui'
        COLLISIONS = 'collisions'
        AllGroupNames = [ENGINE,
         ACCELERATION,
         SHOTS,
         HITS,
         DAMAGE,
         GUI,
         COLLISIONS]

    __effects = {}
    __overlappedGainMultiplier = 0
    __guiButtonsVibrations = {}

    @staticmethod
    def __loadGuiButtonsSettings(buttonsSection):
        for buttonType, effectNameSection in buttonsSection.items():
            EffectsSettings.__guiButtonsVibrations[buttonType] = effectNameSection.asString

    @staticmethod
    def loadSettings():
        root = ResMgr.openSection(EffectsSettings.CFG_FOLDER + 'effects_settings.xml')
        EffectsSettings.__loadGuiButtonsSettings(root['buttons'])
        effectsSection = root['effects']
        if effectsSection is not None:
            effects = [ section for section in effectsSection.values() if section.name == 'effect' ]
            for effect in effects:

                class EffectData:
                    pass

                data = EffectData()
                data.priority = effect.readInt('priority')
                data.group = effect.readString('group')
                EffectsSettings.__effects[effect.readString('name')] = data

        EffectsSettings.__overlappedGainMultiplier = root.readFloat('overlapped_gain_multiplier', 0.0)
        if EffectsSettings.__overlappedGainMultiplier < 0.0:
            EffectsSettings.__overlappedGainMultiplier = 0.0
        elif EffectsSettings.__overlappedGainMultiplier > 1.0:
            EffectsSettings.__overlappedGainMultiplier = 1.0
        EffectsSettings.AccelerationThreshold = root.readFloat('acceleration_threshold', 0.0)
        EffectsSettings.DecelerationThreshold = root.readFloat('deceleration_threshold', 0.0)
        return

    @staticmethod
    def getEffectPriority(effectName):
        if effectName in EffectsSettings.__effects:
            return EffectsSettings.__effects[effectName].priority
        raise Exception("Cannot find effect's priority " + effectName)

    @staticmethod
    def getOverlappedGainMultiplier():
        return EffectsSettings.__overlappedGainMultiplier

    @staticmethod
    def getGroupForEffect(effectName):
        if effectName in EffectsSettings.__effects:
            return EffectsSettings.__effects[effectName].group
        raise Exception("Cannot find effect's group " + effectName)

    @staticmethod
    def getButtonEffect(buttonType):
        return EffectsSettings.__guiButtonsVibrations.get(buttonType, None)
