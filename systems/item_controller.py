class ItemController(krcko.System):
	

	import random

	def setup(self):
		
		self.pickup_momo = krcko.Momo()
		self.pickup_momo.load(defs.MOM_DIR_PATH + "item_pickup.momo")

		self.item_setup()

	def update(self):
		self.check_pickup()

	def cleanup(self):
		pass





	def item_setup(self):

		for itm_ent, _ in self.scene.gen_entities("item"):
			if "item" not in itm_ent.keys():
				continue
			
			pass
			#TODO



	last_position	=	krcko.point(0,0)
	def check_pickup(self) -> None:
		'''Check if player is standing on the item'''
	

		
		#get player ent
		player_ent = self.scene.get_entity_from_name("player")


		#only if player moved
		if self.last_position.y == player_ent['position'].y and\
			self.last_position.x == player_ent['position'].x:
			#
			return

		self.last_position.y	=	player_ent['position'].y
		self.last_position.x	=	player_ent['position'].x


		#go trough items
		for itm_ent, itm_eid in self.scene.gen_entities("item"):
			if "item" not in itm_ent.keys():
				continue

			#only drawable and with position
			if (not "drawable" in itm_ent.keys()) or\
				(not "position" in itm_ent.keys()):
				#no good
				continue

			if player_ent['position'].y == itm_ent['position'].y and\
				player_ent['position'].x == itm_ent['position'].x:
				#	
				self.pickup_item(itm_eid)

	def pickup_item(self, itm_eid :int) -> None:
		'''Momo form'''


		#continue without picking up the item
		continue_action	= krcko.create_action("CONTINUE", [], [], [])
		#pickup the item
		pickup_action 	= krcko.create_action("ITEM_PICKUP", [krcko.ActionFlag.ENDING, krcko.ActionFlag.ENTAILS],\
									['item_eid'], [itm_eid],\
									entails = self.turn_machine.ending_action)

		#get item ent
		itm_ent		= self.scene.get_entity(itm_eid)
				

		amount  = itm_ent['item'].amount
		name	= itm_ent['item'].name
		#clear momo
		self.pickup_momo.clear()
		#momo arguments
		#pickup form text
		#plu - plurality, 1 sing, 2 mult
		self.pickup_momo.add_arguments({'name' : name,'amount' : amount,  'plu' : (1 if amount == 1 else 2)})
		self.pickup_momo.run(fields=["DETECT","OPTION_CONTINUE", "OPTION_PICKUP"])



		#pickup_momo[DETECT] + item_name [item_amount] . 
		form_text :str		=	self.pickup_momo.pick("DETECT")
		
		#control keys
		controls 		= self.game.controls
		continue_key :str	= controls['MOMO']['CONTINUE']
		pickup_key :str		= controls['MOMO']['PICKUP']

		
		#option texts
		continue_option_text :str	= self.pickup_momo.pick('OPTION_CONTINUE') 
		pickup_option_text :str		= self.pickup_momo.pick('OPTION_PICKUP') 


		#momo form
		momo_action		= krcko.create_action("MOMO",\
						[krcko.ActionFlag.HALTING, krcko.ActionFlag.INSERTING],\
						['text','actions','action_names','action_keys'],\
						[form_text, [pickup_action, continue_action], [pickup_option_text, continue_option_text], [pickup_key, continue_key]])


		#insert 
		self.turn_machine.insert_action(momo_action)



sys_instance = ItemController()
