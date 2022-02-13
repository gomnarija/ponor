class ItemController(krcko.System):
	

	import random

	def setup(self):
		self.item_setup()

	def update(self):
		self.check_pickup()
		self.check_pickup()

	def cleanup(self):
		pass





	def item_setup(self):

		for itm_ent, _ in self.scene.gen_entities("item"):
			if "item" not in itm_ent.keys():
				continue
		
			# if item is drawable, asign it's ascii
			if "drawable" in itm_ent.keys():
				itm_ent['drawable'].ascii = int(itm_ent['item'].ascii)

			# item amount
			itm_ent['item'].amount = self.random.randint(int(itm_ent['item'].min_amount), int(itm_ent['item'].max_amount))




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
		continue_action, _	= krcko.create_action("CONTINUE", [], [], [])
		#pickup the item
		pickup_action, _ 	= krcko.create_action("ITEM_PICKUP", [krcko.ActionFlag.ENDING], ['item_eid'], [itm_eid])

		
		#pickup form text
		form_text :str		=	"Nekakva stvar" 
		
		#control keys
		controls 		= self.scene.game.controls
		
		continue_key :str	= controls['MOMO']['CONTINUE']
		pickup_key :str		= controls['MOMO']['PICKUP']

		#momo form
		momo_action, _		= krcko.create_action("MOMO",\
						[krcko.ActionFlag.HALTING],\
						['text','actions','action_names','action_keys'],\
						[form_text, [pickup_action, continue_action], ["pokupi", "ostavi"], [pickup_key, continue_key]])


		#insert 
		self.scene.game.turn_machine.insert_action(momo_action)



sys_instance = ItemController()