class NPCController(krcko.System):
	


	import random

	def setup(self):	
		#get player
		self.player_ent = self.scene.get_entity_from_name("player")


	def update(self):
		
		#get current room rect
		self.room_rect	= 	self.player_ent['player'].room_rect

		#get current action
		action = self.turn_machine.action
		

		#at the end of the turn
		if krcko.ActionFlag.ENDING in action.flags:
			#
			for npc_ent, npc_eid in self.scene.gen_entities("npc"):
				#check for player interaction,	
				self.player_interaction_detection(npc_eid)
	

	def cleanup(self):
		pass



	def player_interaction(self, npc_eid :int) -> None:
		'''sends momo action for player/npc interaction'''
		
		npc_ent		=	self.scene.get_entity(npc_eid)

		if "npc" not in npc_ent.keys():
			logging.error("failed to get npc entity")	
			return
		

		continue_action		=	krcko.create_action("CONTINUE", [], [], [])
		


		continue_key :str	=	self.game.controls['MOMO']['CONTINUE']

		momo_action		=	krcko.create_action("MOMO",\
							[krcko.ActionFlag.HALTING],['text','actions','action_names','action_keys'],\
								["gavran ispred tebe", [continue_action], ["nastavi"], [continue_key]])

		
		
		#insert
		self.turn_machine.insert_action(momo_action)	




	def player_interaction_detection(self, npc_eid :int) -> bool:
		'''Check if player is close enough to interact with npc'''
		
		
		npc_ent	= self.scene.get_entity(npc_eid)
		if "npc" not in npc_ent.keys():
			logging.error("failed to get npc entity")
			return
		

		#player
		pp	=	krcko.point(self.player_ent['position'].y,
							self.player_ent['position'].x)
		#npc
		np	=	krcko.point(npc_ent['position'].y,
						npc_ent['position'].x)

		#must be in the same room as the player
		if not self.room_rect.contains_point(np):
			return False

		#check distance
		if pp.distance(np) < 2:
			self.player_interaction(npc_eid)
			return True

		return False



sys_instance = NPCController()
