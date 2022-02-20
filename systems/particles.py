class Particles(krcko.System):
	'''particle system'''


	import random



	density	  :int	= 4	
	container :krcko.rectangle = krcko.rectangle(350,350,-100,-25)
	fragments :List[str]	   = ['.', ',', "'"]

	def setup(self):
		#get player
		self.player_ent = self.scene.get_entity_from_name("player")
		#
		for fragment in self.fragments:
			self.spawn_particles(fragment)
	def update(self):
		pass	

	def cleanup(self):
		pass



	def spawn_particles(self, fragment :str) -> None:
		
		particles_component, _ = krcko.load_component(defs.PAT_DIR_PATH + "particles.json")

		eid 	= self.scene.add_entity(particles_component, ent_name = "particles")
		ptc_ent	= self.scene.get_entity(eid)	
		if not self.scene.entity_has_component(eid, "particles"):
			logging.error("failed to get particles entity.") 
			return

		ptc_ent['particles'].ascii = ord(fragment)

		index :int
		for index in range(0,int((self.container.height*self.container.width)/100) * int(self.density/len(self.fragments))):
			position :krcko.point =\
				 krcko.point(self.random.randint(self.container.y, self.container.height),\
						self.random.randint(self.container.x, self.container.width))

			ptc_ent['particles'].positions.append(position)

			
				
		





sys_instance = Particles()
