
--------------------------------------------------
				The example SFX xml spec
--------------------------------------------------

<!-- Actors in the effect system.  These are the resources used by events -->
<Actor>	muzzleSmoke
	<ParticleSystem>	sets/global/fx/particles/muzzle_smoke.xml	</ParticleSystem>
</Actor>

<Actor> muzzleFlash
	<Model>				sets/global/fx/actors/muzzle_flash.model		</Model>
</Actor>

<Actor>	healingBeam
	<ParticleSystem>	sets/global/fx/particles/healing_beam.xml	</ParticleSystem>
</Actor>

<!-- Joints in the effect system.  These attach the actors to the source upon invokation
of the special effect -->
<Joint>	muzzleSmoke
	<Node>	HP_muzzle	</Node>
</Joint>

<Joint>	muzzleFlash
	<Hardpoint>	muzzle			</Hardpoint>
</Joint>

<Joint>	healingBeam
	<Node>	HP_muzzle	</Node>
</Joint>


<!-- all events must return a duration.  thus the total length
	 is known, and the Attach objects can be asked to Detach at the end -->
<Event>
	<SwarmTargets>	healingBeam	
		<Node>	biped Neck	</Node>
					.
					.
					.					
	</SwarmTargets>
</Event>
<Event>
	<ForceParticle>	muzzleSmoke </ForceParticle>
</Event>
<Event>
	<PlayAction>	muzzleFlash
		<Action>	Flash	</Action>
	</PlayAction>
</Event>
<Event>
	<ForceParticle> healingBeam	</ForceParticle>
</Event>



--------------------------------------------------
				Using that SFX file.
				
The OneShot sfx will attach, and detach to the model
automatically, all you have to do is create it
and call go()

creation is always safe ( empty SFX can be created )
so you never need to check.
--------------------------------------------------
sfx.OneShotSFX( fileName ).go( gun )


--------------------------------------------------
				Using buffered SFX files.
				
- note that some things like pchang sparks happen
very often, and thus you would not like to allocate
particle memory every time.

- also, you'd like to cap the maximum amount of
them in effect at any time, to limit any worst-case
scenarios ( especially w.r.t memory )
--------------------------------------------------
sfx.bufferedOneShotSFX( fileName, gun )