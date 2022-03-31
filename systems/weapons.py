class Weapons(krcko.System):
	'''weapon stuff :)'''
	

	import random

	
	def setup(self):
		self.inspect_momo = krcko.Momo()
		self.inspect_momo.load(defs.MOM_DIR_PATH + "item_inspect.momo")

		self.attack_momo = krcko.Momo()
		self.attack_momo.load(defs.MOM_DIR_PATH + "weapon_attack.momo")
		


	def update(self):
		
		#weapon inspection action detection :*)
		if self.turn_machine.action_name == "INSPECT_WEAPON":
			self.do_inspect(self.turn_machine.action.item_eid, 1)	



		#attack action detection
		if self.turn_machine.action_name == "ATTACK":
			self.do_attack(self.turn_machine.action.attacker_eid,\
					self.turn_machine.action.target_eid)

	def cleanup(self):
		pass





	def do_attack(self, attacker_eid :int, target_eid :int) -> None:
		'''attack target if attacker has an equipped weapon'''

		#player is attacking
		if attacker_eid == self.scene.get_eid_from_name("player"):
			self.player_attack(target_eid)
		#player is target
		else:
			self.npc_attack(attacker_eid)
	

	

	def get_equipped_weapon_damage(self, eid :int) -> tuple[bool, tuple[int, int]]:
		'''check if entity has a weapon equipped in inventory
			return (is_equipped, (weapon_eid, total damage))'''
		

		#must have inventory component
		if not self.scene.entity_has_component(eid, "inventory"):
			logggin.error("entity must have inventory component")
			return (False, 0)

		#get entity
		ent	=	self.scene.get_entity(eid)
	
		has_weapon :bool = False
		damage :int = 0
		eq_eid :int = 0

		
		#has an item equipped
		if len(ent['inventory'].hands) == 1:
			eq_eid = ent['inventory'].hands[0]
			#must be item, weapon
			if self.scene.entity_has_component(eq_eid, "item") and\
				self.scene.entity_has_component(eq_eid, "weapon"):
				#
				has_weapon = True
			
				#get weapon entity
				weapon_ent = self.scene.get_entity(eq_eid)
				
				#calculate damage
				base_damage :int = weapon_ent['weapon'].damage
				crt_chance :int  = weapon_ent['weapon'].critical_strike_chance
				#try crit, else base 
				damage += base_damage * 2 if krcko.dice_roll(crt_chance) else base_damage
		#doesn't 
		else:
			pass


		return has_weapon, (eq_eid, damage)	



	def player_empty_attack(self) -> None:
		'''player trying to attack someone with no weapon equipped,
			sends out momo form'''


		#run momo
		self.attack_momo.run(fields = ["OPTION_CONTINUE",\
						 "EMPTY"])



		#continue
		continue_action			=	krcko.create_action("CONTINUE", [], [], [])
		continue_key			=	self.game.controls["MOMO"]["CONTINUE"]
		continue_option_text		=	self.attack_momo.pick("OPTION_CONTINUE")


		#momo form text
		text :str			=	self.attack_momo.pick("EMPTY")

		#momo action
		momo_action			=	krcko.momo_action(text, [continue_action], [continue_option_text], [continue_key])


		#insert
		self.turn_machine.insert_action(momo_action)	




	def player_attack(self, target_eid :int) -> None:
		'''player is attacking someone with a weapon'''	
		

		#target must be a npc
		# and must have health
		if not self.scene.entity_has_component(target_eid, "npc") or\
			not self.scene.entity_has_component(target_eid, "health"):
				logging.error("weapon target must be a npc and must have health.")
				return
	
		#get target entity
		target_ent	=	self.scene.get_entity(target_eid)
		#get player entity, eid
		player_ent	=	self.scene.get_entity_from_name("player")
		player_eid :int	=	self.scene.get_eid_from_name("player")

		#check if player has a weapon in hand
		# and count total damage
		has_weapon :bool
		weapon_eid :int
		damage	:int
		has_weapon, (weapon_eid, damage) = self.get_equipped_weapon_damage(player_eid)	

		#no weapon equipped
		if not has_weapon:
			self.player_empty_attack()
			return
	
		
		#ATTACK
		target_ent['health'].amount -= damage

	
		#momo form
		# attack, continue	


		#get weapon ent
		if not self.scene.entity_has_component(weapon_eid, "weapon"):
			logging.error("failed to get weapon entity.")
			return
		#
		weapon_ent = self.scene.get_entity(weapon_eid)


		#
		npc_name :str		=	target_ent['npc'].name
		default_field_name :str	=	"DEFAULT_ATTACKING"
		field_name :str 	=	weapon_ent['weapon'].attacking_momo_field	
		




		#run momo
		self.attack_momo.add_arguments({'name' : npc_name, 'damage' : damage})
		self.attack_momo.run(fields = ["OPTION_RUN",\
						 "OPTION_ATTACK",\
							default_field_name,\
								field_name])

		#if a given field_name doesn't exist
		# set it to default
		if not self.attack_momo.has_field(field_name):
			field_name = default_field_name




		#attack
		attack_action 			=	 krcko.create_action("ATTACK", [krcko.ActionFlag.ENDING],\
										['attacker_eid', 'target_eid'],\
											[player_eid, target_eid])
		#
		attack_key :str			= 	self.game.controls['MOMO']['ATTACK']
		attack_option_text :str		= 	self.attack_momo.pick("OPTION_ATTACK")


		#continue
		continue_action			=	krcko.create_action("CONTINUE", [], [], [])
		continue_key			=	self.game.controls["MOMO"]["CONTINUE"]
		continue_option_text		=	self.attack_momo.pick("OPTION_RUN")


		#momo form text
		text :str			=	self.attack_momo.pick(field_name)

		#momo action
		momo_action			=	krcko.momo_action(text, [attack_action, continue_action], [attack_option_text, continue_option_text], [attack_key, continue_key])


		#insert
		self.turn_machine.insert_action(momo_action)	



	def npc_attack(self, npc_eid :int) -> None:
		'''npc is attacking player with a weapon'''	
		

		#attacker must be a npc
		# and must have inventory
		if not self.scene.entity_has_component(npc_eid, "npc") or\
			not self.scene.entity_has_component(npc_eid, "inventory"):
				logging.error("weapon target must be a npc and must have inventory.")
				return
	
		#get npc entity
		npc_ent		=	self.scene.get_entity(npc_eid)
		#get player entity, eid
		player_ent	=	self.scene.get_entity_from_name("player")
		player_eid :int	=	self.scene.get_eid_from_name("player")

		#check if npc has a weapon in hand
		# and count total damage
		has_weapon :bool
		weapon_eid :int 
		damage :int
		has_weapon, (weapon_eid, damage) = self.get_equipped_weapon_damage(npc_eid)

		#no weapon equipped
		if not has_weapon:
			return
	
		
		#ATTACK
		player_ent['health'].amount -= damage



		#get weapon ent
		if not self.scene.entity_has_component(weapon_eid, "weapon"):
			logging.error("failed to get weapon component.")
			return
		#
		weapon_ent = self.scene.get_entity(weapon_eid)


		#momo form
		# continue	

		#
		npc_name :str			=	npc_ent['npc'].name
		default_field_name :str		=	"DEFAULT_TARGET"
		field_name :str			=	weapon_ent['weapon'].target_momo_field

		#run momo
		self.attack_momo.add_arguments({'name' : npc_name, 'damage' : damage})
		self.attack_momo.run(fields = ["OPTION_CONTINUE",\
								default_field_name,
									field_name])
		#
		#if a given field_name doesn't exist
		# set it to default
		if not self.attack_momo.has_field(field_name):
			field_name = default_field_name


		#continue
		continue_action			=	krcko.create_action("CONTINUE", [], [], [])
		continue_key			=	self.game.controls["MOMO"]["CONTINUE"]
		continue_option_text		=	self.attack_momo.pick("OPTION_CONTINUE")


		#momo form text
		text :str			=	self.attack_momo.pick(field_name)

		#momo action
		momo_action			=	krcko.momo_action(text, [continue_action], [continue_option_text], [continue_key])


		#insert
		self.turn_machine.insert_action(momo_action)	


				



	def do_inspect(self, item_eid :int, amount :int) -> None:
		'''display momo form with weapons info '''
		
		#get item
		item_ent = self.scene.get_entity(item_eid)
		#must have weapon component
		if not self.scene.entity_has_component(item_eid, "item") or\
			not self.scene.entity_has_component(item_eid, "weapon"):
			logging.error("failed to get weapon entity.")
			return

		#weapon stats
		damage		:int	=	item_ent['weapon'].damage	
		durability	:int	=	item_ent['weapon'].durability
		crt_chance	:int	=	item_ent['weapon'].critical_strike_chance


		#momo
		self.inspect_momo.add_arguments({'name' : item_ent['item'].name,\
								'damage' : damage,
									'durability' : durability,
										'crt' : crt_chance})
		#
		self.inspect_momo.run(fields = ["WEAPONS", "OPTION_CONTINUE", "OPTION_EQUIP_WEAPON"])


		#continue option
		continue_action			=	krcko.create_action("CONTINUE", [], [], [])
		continue_option_text :str	=	self.inspect_momo.pick("OPTION_CONTINUE")
		continue_key :str		=	self.game.controls['MOMO']['CONTINUE']



		#equip option 
		equip_action		=	krcko.create_action("EQUIP_ITEM", [krcko.ActionFlag.ENDING],\
										['item_eid','equip_type'],
											[item_eid, 'hands'])
		#
		equip_option_text :str		=	self.inspect_momo.pick("OPTION_EQUIP_WEAPON")
		equip_key :str			=	self.game.controls['MOMO']['EQUIP']
	
		#momo form text
		info_text :str		=	self.inspect_momo.pick("WEAPONS")

		#momo form
		momo_action		=	krcko.momo_action(info_text, [equip_action, continue_action],\
										 [equip_option_text, continue_option_text],\
											 [equip_key, continue_key])
		#insert
		self.turn_machine.insert_action(momo_action)
	
			


sys_instance = Weapons()	
