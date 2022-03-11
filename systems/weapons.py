class Weapons(krcko.System):
	'''weapon stuff :)'''
	

	import random

	
	def setup(self):
		self.inspect_momo = krcko.Momo()
		self.inspect_momo.load(defs.MOM_DIR_PATH + "item_inspect.momo")


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





	def dice_roll(self, chance :int) -> bool:
		'''role them dice'''
		return self.random.randint(0,100) <= chance 

	def do_attack(self, attacker_eid :int, target_eid :int) -> None:
		'''attack target if attacker has an equipped weapon'''
	
	
		#attacker must have an inventory component
		# and a weapon in hand	

		#get attacker entity
		attacker_ent = self.scene.get_entity(attacker_eid)
	
		#check if attacker has inventory
		if not self.scene.entity_has_component(attacker_eid, "inventory"):
			return

		#check if attacker has a weapon in hand
		has_weapon :bool = False
		damage :int = 0
		for eq_eid in attacker_ent['inventory'].hands:
			#item, weapon
			if self.scene.entity_has_component(eq_eid, "item") and\
				self.scene.entity_has_component(eq_eid, "weapon"):
				#
				has_weapon = True
			
				#get weapon entity
				weapon_ent = self.scene.get_entity(eq_eid)
				
				#calculate damage
				base_damage :int = weapon_ent['weapon'].damage
				crt_chance :int = weapon_ent['weapon'].critical_strike_chance
				#try crit, else base 
				damage += base_damage * 2 if self.dice_roll(crt_chance) else base_damage

		#no weapon, no attacking :(
		if not has_weapon:
			return
		


		#target must have health component
		if not self.scene.entity_has_component(target_eid, "health"):
			return
		
		#get target entity
		target_ent = self.scene.get_entity(target_eid)
		#get target health
		target_health = target_ent['health']



		#ATTACKKK
		target_health.amount -= damage



		#momo form
		# attack, continue	


		#attack
		attack_action 		= krcko.create_action("ATTACK", [krcko.ActionFlag.ENDING],\
								['attacker_eid', 'target_eid'],\
									[attacker_eid, target_eid])
		attack_key :str		= self.game.controls['MOMO']['ATTACK']
		attack_text :str	= "napadni"



		#continue
		continue_action		=	krcko.create_action("CONTINUE", [], [], [])
		continue_key		=	self.game.controls["MOMO"]["CONTINUE"]
		continue_text		=	"nastavi"




		#TODO: momo file with attack description
		text :str		=	"napao si gi"

		#momo action
		momo_action		=	krcko.momo_action(text, [attack_action, continue_action], [attack_text, continue_text], [attack_key, continue_key])



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


		#continue
		continue_action		=	krcko.create_action("CONTINUE", [], [], [])
		continue_text :str	=	"dobro"
		continue_key :str	=	self.game.controls['MOMO']['CONTINUE']



		#equip this weapon
		equip_action		=	krcko.create_action("EQUIP_ITEM", [krcko.ActionFlag.ENDING],\
										['item_eid','equip_type'],
											[item_eid, 'hands'])
		equip_text :str		=	"uzmi u ruke"
		equip_key :str		=	self.game.controls['MOMO']['EQUIP']

		#weapon stats
		damage		:int	=	item_ent['weapon'].damage	
		durability	:int	=	item_ent['weapon'].durability
		crt_chance	:int	=	item_ent['weapon'].critical_strike_chance
	
		#form text
		#momo
		self.inspect_momo.add_arguments({'name' : item_ent['item'].name,\
								'damage' : damage,
									'durability' : durability,
										'crt' : crt_chance})


		#run momo
		self.inspect_momo.run(fields = ["WEAPONS"])
		info_text :str		=	self.inspect_momo.pick("WEAPONS")

		#momo form
		momo_action		=	krcko.momo_action(info_text, [equip_action, continue_action],\
										 [equip_text, continue_text],\
											 [equip_key, continue_key])
		#insert
		self.turn_machine.insert_action(momo_action)
	
			


sys_instance = Weapons()	
