class NPCController(krcko.System):
	


	import random

	def setup(self):	
		#get player
		self.player_ent = self.scene.get_entity_from_name("player")

		#momo
		self.interaction_momo = krcko.Momo()
		self.interaction_momo.load(defs.MOM_DIR_PATH + "npc_interaction.momo")

		#
		for npc_ent, npc_eid in self.scene.gen_entities("npc"):
			#set name from template
			if self.scene.entity_has_component(npc_eid, "template"):
				npc_ent['npc'].name = npc_ent['template'].name


	def update(self):
		
		#get current room rect
		self.room_rect	= 	self.player_ent['player'].room_rect


		#get current action
		action = self.turn_machine.action
		

		#at the end of the turn
		if krcko.ActionFlag.ENDING in self.turn_machine.action.flags:
			#
			for npc_ent, npc_eid in self.scene.gen_entities("npc"):
				#check if npc is interacting with player
				if self.player_interaction_detection(npc_eid):
					#if it's agressive
					if npc_ent['npc'].agro > 50:
						#attack player
						self.attack_player(npc_eid)
						

		#agro up if attacked
		# attack action detection
		if self.turn_machine.action_name == "ATTACK":
			#if attacker is player
			if self.turn_machine.action.attacker_eid ==\
				self.scene.get_eid_from_name("player"):
				#and target is npc 
				if self.scene.entity_has_component(self.turn_machine.action.target_eid, "npc"):
					#get npc 
					npc_ent = self.scene.get_entity(self.turn_machine.action.target_eid)
					#set agro to 100, unless it's -1
					if npc_ent['npc'].agro != -1:
						npc_ent['npc'].agro = 100





	

	def cleanup(self):
		pass


					


	def attack_player(self, npc_eid :int) -> None:
		'''sends ATTTACK action with a given npc attacking player'''
		
		#NON ENDING ATTACK

		#ent given must be npc
		if not self.scene.entity_has_component(npc_eid, "npc"):
			logging.error("failed to get npc entity.")
			return


		#get player eid 
		player_eid :int		=	self.scene.get_eid_from_name("player")
		attack_action		=	krcko.create_action("ATTACK",[],\
								['attacker_eid', 'target_eid'],\
									[npc_eid, player_eid])	
	
		#insert action	
		self.turn_machine.insert_action(attack_action)	



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
		


		#momo
		self.interaction_momo.add_arguments({'name' : npc_ent['npc'].name})
		self.interaction_momo.run(fields=["OPTION_CONTINUE","OPTION_ATTACK", "DEFAULT"])


		#don't do anything
		continue_action			=	krcko.create_action("CONTINUE", [], [], [])#
		continue_key :str		=	self.game.controls['MOMO']['CONTINUE']
		continue_option_text :str	=	self.interaction_momo.pick("OPTION_CONTINUE")


		#attack npc
		# send out action with attacker and targer eids 
		player_eid :int			=	self.scene.get_eid_from_name("player")
		attack_action			=	krcko.create_action("ATTACK",[krcko.ActionFlag.ENDING],\
								['attacker_eid', 'target_eid'],\
									[player_eid, npc_eid])	
	
		attack_key :str			=	self.game.controls['MOMO']['ATTACK']
		attack_option_text :str		=	self.interaction_momo.pick("OPTION_ATTACK")


		#momo form text
		text :str			=	self.interaction_momo.pick("DEFAULT")


		#create momo action
		momo_action			=	krcko.momo_action(text, [continue_action, attack_action], [continue_option_text, attack_option_text], [continue_key, attack_key])

	
		#insert momo action
		self.turn_machine.insert_action(momo_action)	




	def player_interaction_detection(self, npc_eid :int) -> bool:
		'''Check if player is close enough to interact with npc'''
		
		
		npc_ent	= self.scene.get_entity(npc_eid)
		if "npc" not in npc_ent.keys():
			logging.error("failed to get npc entity")
			return False
		

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
		#  dont't interact again
		if npc_ent['npc'].is_interacting == True:
			#check radius
			if pp.distance(np) >= 2:
				#not interacting anymore
				npc_ent['npc'].is_interacting = False
				return False
			#don't interact again
			return True


		#check distance
		if pp.distance(np) < 2:
			#is interacting
			npc_ent['npc'].is_interacting = True
			#agro down
			if npc_ent['npc'].agro < 50:
				self.player_interaction(npc_eid)
			return True

		return False



sys_instance = NPCController()
