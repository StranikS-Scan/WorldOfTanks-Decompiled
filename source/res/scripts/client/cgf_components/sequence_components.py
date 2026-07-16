# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/sequence_components.py
from __future__ import absolute_import
import CGF
from cgf_script.registration import ComponentProperty, registerComponent
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import List

@registerComponent
class OnDisappearPrefabSpawnComponent(object):
    category = 'Sequence'
    editorTitle = 'On Disappear Prefab Spawner'
    domain = CGF.Domain.ClientEditor
    prefab = ComponentProperty(type=CGF.PropertyType.String, editorName='prefab', value='', annotations={'path': '*.prefab'})


@registerComponent
class OnAppearPrefabSpawnComponent(object):
    category = 'Sequence'
    editorTitle = 'On Appear Prefab Spawner'
    domain = CGF.Domain.ClientEditor
    prefab = ComponentProperty(type=CGF.PropertyType.String, editorName='prefab', value='', annotations={'path': '*.prefab'})


@registerComponent
class SequenceSnapshotComponent(object):
    editorTitle = 'Sequence Snapshot'
    domain = CGF.Domain.Client


@registerComponent
class SequencePauseComponent(object):
    editorTitle = 'Sequence Pause'
    domain = CGF.Domain.Client


class PrefabSpawnerSystem(CGF.System):
    SpawnerActivated = CGF.ActivateReaction(CGF.ReactRw(OnAppearPrefabSpawnComponent), CGF.TransformComponent)
    SpawnerDeactivated = CGF.DeactivateReaction(CGF.ReactRw(OnDisappearPrefabSpawnComponent), CGF.TransformComponent)
    Reactions = CGF.Reactions(SpawnerActivated, SpawnerDeactivated)

    def update(self):
        for spawner, tr in self.reaction(self.SpawnerDeactivated):
            CGF.loadAndCreatePrefab(spawner.prefab, self.spaceID, tr.worldTransform, self._onLoaded)

        for spawner, tr in self.reaction(self.SpawnerActivated):
            CGF.loadAndCreatePrefab(spawner.prefab, self.spaceID, tr.worldTransform, self._onLoaded)

    @staticmethod
    def _onLoaded(objects, queue):
        root = objects[0]
        queue.activateGameObject(root)
