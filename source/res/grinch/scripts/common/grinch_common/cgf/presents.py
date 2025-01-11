# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/common/grinch_common/cgf/presents.py
import CGF
import Triggers
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes

@registerComponent
class PresentSunflowerHolder(object):
    category = 'Grinch'
    domain = CGF.DomainOption.DomainAll
    count = ComponentProperty(type=CGFMetaTypes.INT, editorName='count', value=50)
    radius = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='radius', value=40)

    def __init__(self):
        self.__positions = []

    def release(self, pos):
        self.__positions.append(pos)

    def acquire(self, root):
        positions = self.__positions
        if not positions:
            return None
        else:
            pos = min(positions, key=root.flatDistSqrTo)
            positions.remove(pos)
            return pos


@registerComponent
class PresentSunflowerSeed(object):
    category = 'Grinch'
    domain = CGF.DomainOption.DomainAll


@registerComponent
class PresentPickupAreaTriggerComponent(object):
    category = 'Grinch'
    domain = CGF.DomainOption.DomainAll
    trigger = ComponentProperty(type=CGFMetaTypes.LINK, editorName='AreaTrigger', value=Triggers.AreaTriggerComponent)

    def __init__(self):
        self.reactionID = None
        return


@registerComponent
class PresentDeliveryAreaTriggerComponent(object):
    category = 'Grinch'
    domain = CGF.DomainOption.DomainAll
    trigger = ComponentProperty(type=CGFMetaTypes.LINK, editorName='AreaTrigger', value=Triggers.AreaTriggerComponent)

    def __init__(self):
        self.enterReactionID = None
        self.exitReactionID = None
        return


@registerComponent
class DeliverableComponent(object):
    category = 'Grinch'
    domain = CGF.DomainOption.DomainAll


@registerComponent
class HomebaseComponent(object):
    category = 'Grinch'
    domain = CGF.DomainOption.DomainAll
    team = ComponentProperty(type=CGFMetaTypes.INT, editorName='Team', value=1)


@registerComponent
class IsAtHomebaseComponent(object):
    category = 'Grinch'
    domain = CGF.DomainOption.DomainAll
    base = ComponentProperty(type=CGFMetaTypes.LINK, value=CGF.GameObject)

    def __init__(self, base):
        self.base = base


@registerComponent
class DeliveredPresentComponent(object):
    category = 'Grinch'
    domain = CGF.DomainOption.DomainAll
    base = ComponentProperty(type=CGFMetaTypes.LINK, value=CGF.GameObject)

    def __init__(self, base):
        self.base = base


@registerComponent
class StolenPresentsComponent(object):
    category = 'Grinch'
    domain = CGF.DomainOption.DomainAll
    amount = ComponentProperty(type=CGFMetaTypes.INT, value=0)

    def increment(self):
        self.amount += 1


@registerComponent
class GrinchPresentCoreSpawnTarget(object):
    category = 'Grinch'
    domain = CGF.DomainOption.DomainAll


@registerComponent
class GrinchPresentEarlygameSpawnTargetA(object):
    category = 'Grinch'
    domain = CGF.DomainOption.DomainAll


@registerComponent
class GrinchPresentEarlygameSpawnTargetB(object):
    category = 'Grinch'
    domain = CGF.DomainOption.DomainAll


@registerComponent
class GrinchPresentEarlygameSpawnTargetC(object):
    category = 'Grinch'
    domain = CGF.DomainOption.DomainAll


@registerComponent
class GrinchPresentMidgameSpawnTarget(object):
    category = 'Grinch'
    domain = CGF.DomainOption.DomainAll


@registerComponent
class GrinchPresentLategameSpawnTarget(object):
    category = 'Grinch'
    domain = CGF.DomainOption.DomainAll


@registerComponent
class GrinchBotSpawnTarget(object):
    category = 'Grinch'
    domain = CGF.DomainOption.DomainAll
