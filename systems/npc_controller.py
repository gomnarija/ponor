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
		'''sends momo action for player/npc interaction
			options:
				continue
				talk
				attack
		'''
		
		npc_ent		=	self.scene.get_entity(npc_eid)

		if "npc" not in npc_ent.keys():
			logging.error("failed to get npc entity")	
			return
		

		#don't do anything
		continue_action		=	krcko.create_action("CONTINUE", [], [], [])#
		continue_key :str	=	self.game.controls['MOMO']['CONTINUE']
		continue_text :str	=	"nastavi"


		#attack npc
		# send out action with attacker and targer eids 
		player_eid :int		=	self.scene.get_eid_from_name("player")
		attack_action		=	krcko.create_action("ATTACK",[],\
								['attacker_eid', 'target_eid'],\
									[player_eid, npc_eid])	
	
		attack_key :str		=	self.game.controls['MOMO']['ATTACK']
		attack_text :str	=	"napadni"



		#create momo action
		momo_action		=	krcko.create_action("MOMO",\
							[krcko.ActionFlag.HALTING, krcko.ActionFlag.INSERTING],\
								['text','actions','action_names','action_keys'],\
								["gavran ispred tebe",[continue_action, attack_action], [continue_text, attack_text], [continue_key, attack_key]])
		
		
		#insert momo action
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

		#if it's already interacting 
		# check if player is still inside radius
		# dont't interact again
		if npc_ent['npc'].is_interacting == True:
			#check radius
			if pp.distance(np) >= 2:
				#not interacting anymore
				npc_ent['npc'].is_interacting = False
			#don't interact again
			return


		#check distance
		if pp.distance(np) < 2:
			#is interacting
			npc_ent['npc'].is_interacting = True
			self.player_interaction(npc_eid)
			return True

		return False



sys_instance = NPCController()
