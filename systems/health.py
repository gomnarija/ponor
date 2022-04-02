class Health(krcko.System):
	'''health system'''


	import random


	def setup(self):
		
		#momo
		self.death_momo		=	krcko.Momo()
		self.death_momo.load(defs.MOM_DIR_PATH + "npc_death.momo")


		#set health
		for ent, eid in self.scene.gen_entities("health"):
			ent['health'].amount = ent['health'].max_health	


	def update(self):
		
		#at the end of the turn
		if krcko.ActionFlag.ENDING in self.turn_machine.action.flags:
			#
			for ent, eid in self.scene.gen_entities("health"):
				#
				if ent['health'].amount <= 0:
					self.die(eid)	
		
		

	def cleanup(self):
		pass


	def player_die(self) -> None:
		'''game over'''
		pass

	
	def die(self, eid :int) -> None:
		'''it's over'''


		if not self.scene.entity_has_component(eid, "health"):
			#
			logging.error("entity must have health component")
			return
		
		if eid == self.scene.get_eid_from_name("player"):
			self.player_die()
			return



		ent = self.scene.get_entity(eid)
		
		#destroy items from inventory
		# if it has one 
		if self.scene.entity_has_component(eid, "inventory"):
			#one by one
			item_eid :int 
			for item_eid in ent['inventory'].items:
				self.scene.del_entity(item_eid)

		#destroy ent 
		# (actually wait until end of turn to be purged, can still be used bellow)
		self.scene.del_entity(eid)



		#momo form
		# only for nps
		if not self.scene.entity_has_component(eid, "npc"):
			return
		


		default_field_name :str = "DEFAULT_DEATH"
		field_name :str		= ent['npc'].death_momo_field
	

		#run momo
		self.death_momo.add_arguments({'name' : ent['npc'].name})
		self.death_momo.run(fields=[default_field_name, field_name])

		#check if a given field name is loaded,
		# if not set it to default
		if not self.death_momo.has_field(field_name):
			field_name = default_field_name


		#form text
		text :str	=	self.death_momo.pick(field_name)	
		
		
		#
		momo_action	=	krcko.momo_info_action(text, self.game.controls['MOMO']['CONTINUE']) 
		


		#insert
		self.turn_machine.insert_action(momo_action)




sys_instance = Health()
