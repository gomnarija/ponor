class InventoryController(krcko.System):
	''''''
	
	

	def setup(self):
		
		#get player ent
		self.player_ent = self.scene.get_entity_from_name("player")

		#
		self.inspect_momo = krcko.Momo()
		self.inspect_momo.load(defs.MOM_DIR_PATH + "item_inspect.momo")


		#ui stuff
		self.inventory_momo = krcko.Momo()
		self.inventory_momo.load(defs.MOM_DIR_PATH + "inventory_view.momo")
		self.inventory_momo.run()
	

	def update(self):
		


		#inspect item action detection
		if self.turn_machine.action_name == "INSPECT_ITEM":
			inspection_action = self.turn_machine.action
			self.do_inspect(inspection_action.item_eid, inspection_action.amount, inspection_action.is_equipped)


		#equip item action detection 
		if self.turn_machine.action_name == "EQUIP_ITEM":
			equip_action = self.turn_machine.action	
			self.do_equip(equip_action.carrier_eid, equip_action.item_eid, equip_action.equip_type)

		#unequip item action detection 
		if self.turn_machine.action_name == "UNEQUIP_ITEM":
			unequip_action = self.turn_machine.action	
			self.do_unequip(unequip_action.carrier_eid, unequip_action.item_eid, unequip_action.equip_type)


		#drop item action detection
		if self.turn_machine.action_name == "DROP_ITEM":
			drop_action = self.turn_machine.action
			self.do_drop(drop_action.carrier_eid, drop_action.item_eid)
			





	def cleanup(self):
		pass


	def do_drop(self, carrier_eid :int, item_eid :int) -> None:
		'''drop item from inventory'''


		#get inventory
		if not self.scene.entity_has_component(carrier_eid, "inventory"):
			logging.error("carrier doesn't have inventory compoent.")
			return

		carrier_ent 	= self.scene.get_entity(carrier_eid)
		inventory 	= carrier_ent['inventory']

		#if inside
		if item_eid in inventory.items:
			#drop it 
			inventory.items.remove(item_eid) 


	

	def do_unequip(self, carrier_eid :int, item_eid :int, equip_type :str) -> None:
		'''unequip a given item.
			types:
				hands
				head
				chest
				legs'''

			
		#get item entity
		item_ent = self.scene.get_entity(item_eid)
		if not self.scene.entity_has_component(item_eid, "item"):
			logging.error("failed to get item entity.")
			return
		
		#get carrier inventory component
		if not self.scene.entity_has_component(carrier_eid, "inventory"):
			logging.error("carrier doesn't have inventory component.")
			return
		
		carrier_ent 	= self.scene.get_entity(carrier_eid)
		inventory 	= carrier_ent['inventory']
		
		
		#hands item type
		if equip_type == "hands":
			#must actually be in hands
			if item_eid in inventory.hands:
				inventory.hands.remove(item_eid)				

	
		#TODO: other item types		
		



	def do_equip(self, carrier_eid :int, item_eid :int,equip_type :str) -> None:
		'''equip a given item of given equip type.
			types:
				hands
				head
				chest
				legs		'''

		#get item entity
		item_ent = self.scene.get_entity(item_eid)
		if not self.scene.entity_has_component(item_eid, "item"):
			logging.error("failed to get item entity.")
			return
		
		#get carrier inventory component
		if not self.scene.entity_has_component(carrier_eid, "inventory"):
			logging.error("carrier doesn't have inventory component.")
			return
		
		carrier_ent 	= self.scene.get_entity(carrier_eid)
		inventory 	= carrier_ent['inventory']

		
		#hands item type
		if equip_type == "hands":
			#max items in hands is 1
			if len(inventory.hands) == 1:
				#remove equiped one 
				inventory.hands.pop(0)
			#add new item
			inventory.hands.append(item_eid)
			
			
		#TODO: other item types		


	def do_inspect(self,item_eid :int, amount :int, is_equipped :bool) -> None:
		'''display momo form with item info '''
		
		#get item
		item_ent = self.scene.get_entity(item_eid)
		if not self.scene.entity_has_component(item_eid, "item"):
			logging.error("failed to get item entity")
			return


		#if weapon, send it away
		if self.scene.entity_has_component(item_eid, "weapon"):
			#inspect weapon action
			inspect_weapon_action = krcko.create_action("INSPECT_WEAPON", [krcko.ActionFlag.INSERTING],\
								["item_eid", "amount", "is_equipped"], [item_eid, amount, is_equipped])
			#insert
			self.turn_machine.insert_action(inspect_weapon_action)
			return		




		#momo
		self.inspect_momo.add_arguments({'name' : item_ent['item'].name,\
							'amount' : amount,\
								'weight' : item_ent['item'].weight * amount})
		#
		self.inspect_momo.run(fields=["DEFAULT", "OPTION_CONTINUE", "OPTION_DROP_ITEM"])


		#continue option
		continue_action			=	krcko.create_action("CONTINUE", [], [], [])
		continue_option_text :str	=	self.inspect_momo.pick("OPTION_CONTINUE")
		continue_key :str		=	self.game.controls['MOMO']['CONTINUE']



		#player is carrier
		carrier_eid :int		=	self.scene.get_eid_from_name("player")	
		#drop option	
		drop_action			=	krcko.create_action("DROP_ITEM", [krcko.ActionFlag.ENDING], ['carrier_eid', 'item_eid'], [carrier_eid, item_eid])
		drop_option_text :str		=	self.inspect_momo.pick("OPTION_DROP_ITEM")
		drop_key :str			=	self.game.controls['MOMO']['DROP_ITEM']
		

	
		#momo form text
		info_text :str		=	self.inspect_momo.pick("DEFAULT")	


		#momo form
		momo_action		=	krcko.momo_action(info_text, [continue_action, drop_action], [continue_option_text, drop_option_text], [continue_key, drop_key])
		#insert
		self.turn_machine.insert_action(momo_action)
	
			

sys_instance = InventoryController()	
