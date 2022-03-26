class InventoryView(krcko.System):
	'''Displays the inventory'''
	
	
	#STELOVANJE
	weight_y_bottom 	:int	=	4
	items_start_y_top	:int	=	3

	def setup(self):
		
		#get player ent
		self.player_ent = self.scene.get_entity_from_name("player")


		self.inspect_momo = krcko.Momo()
		self.inspect_momo.load(defs.MOM_DIR_PATH + "item_inspect.momo")


	_started :bool = False#wait for start action	
	def update(self):
		
		if not self._started:
			if self.turn_machine.action_name == "START":
				self._started = True
			else:
				return
	


		self.update_view()

				#draw view borders
		krcko.draw_window_border(self.view, tl = krcko.AC_DIAMOND,\
					tr = krcko.AC_DIAMOND,\
					bl  = krcko.AC_DIAMOND,\
					br = krcko.AC_DIAMOND)


		#
		self.draw_middle_text("[ prtljag ]", 0)
		#
		self.draw_weight()
		#get equiped items
		self.get_equipped()
		#
		self.get_items()
		self.draw_items()
		#if there are any equipped items draw them
		if len(self.equipped) > 0:
			self.draw_equipped()


		#inspect detection
		key = self.game.get_key()
	

		#only while turn machine is unhalted,
		# detect inspection keys	
		if not self.turn_machine.is_halted and key >= "0" and key <= "9":
			if not self.turn_machine.is_halted:
				self.inspect_item(int(key))

		#inspect item action detection
		if self.turn_machine.action_name == "INSPECT_ITEM":
			self.do_inspect(self.turn_machine.action.item_eid, self.turn_machine.action.amount)


		#equip item action detection 
		if self.turn_machine.action_name == "EQUIP_ITEM":
			self.do_equip(self.turn_machine.action.item_eid, self.turn_machine.action.equip_type)





	def cleanup(self):
		pass


	
	def draw_equipped(self) -> None:
		'''display equipped items'''
	

		#TODO: check for out of bounds y 
	
		#bellow items
		starting_y :int = self.last_item_y + 1

		curr_y :int	=	starting_y
		#draw equipped text
		self.draw_middle_text("-[ upotrebljeni ]-", curr_y)
		curr_y += 2

		#draw equipped 
		# EQUIP_TYPE) ITEM NAME 
		for equip_type in self.equipped.keys():
			#get item
			item_eid :int = self.equipped[equip_type]
			if not self.scene.entity_has_component(item_eid, "item"):
				logging.error("failed to get item")
				continue	
			#get entity
			item_ent = self.scene.get_entity(item_eid)
			#draw
			text :str = equip_type + ") " + item_ent['item'].name
			self.draw_middle_text(text, curr_y)
			curr_y += 1
			
		




	def get_equipped(self) -> None:
		'''get equipped items'''

		#equip_type : item_eid
		self.equipped = {}
		
		#get player inventory
		player_inventory = self.player_ent['inventory']
		
		#one item in hands, in right hand
		if len(player_inventory.hands) == 1:
			self.equipped['DR'] = player_inventory.hands[0]
		
		#two item in hands
		if len(player_inventory.hands) == 2:
			self.equipped['DR'] = player_inventory.hands[0]
			self.equipped['LR'] = player_inventory.hands[1]
			
		#item on head
		if len(player_inventory.head) == 1:
			self.equipped['G'] = player_inventory.heads[0]
	
		#item on chest	
		if len(player_inventory.chest) == 1:
			self.equipped['P'] = player_inventory.chest[0]

		#item on legs
		if len(player_inventory.legs) == 1:
			self.equipped['N'] = player_inventory.legs[0]
	


		

	def do_equip(self, item_eid :int,equip_type :str) -> None:
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
		
		#get player inventory component
		player_inventory = self.player_ent['inventory']

	
		#hands item type
		if equip_type == "hands":
			#max items in hands is 2
			if len(player_inventory.hands) == 2:
				#remove first equiped one 
				#TODO: maybe ask if you're sure about this
				player_inventory.hands.pop(0)
			#add new item
			player_inventory.hands.append(item_eid)
			
			
				


	def do_inspect(self, item_eid :int, amount :int) -> None:
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
								["item_eid", "amount"], [item_eid, amount])
			#insert
			self.turn_machine.insert_action(inspect_weapon_action)
			return		


		#momo
		self.inspect_momo.add_arguments({'name' : item_ent['item'].name,\
							'amount' : amount,\
								'weight' : item_ent['item'].weight * amount})
		#
		self.inspect_momo.run(fields=["DEFAULT", "OPTION_CONTINUE"])


		#continue option
		continue_action			=	krcko.create_action("CONTINUE", [], [], [])
		continue_option_text :str	=	self.inspect_momo.pick("OPTION_CONTINUE")
		continue_key :str		=	self.game.controls['MOMO']['CONTINUE']


		
		#momo form text
		info_text :str		=	self.inspect_momo.pick("DEFAULT")	


		#momo form
		momo_action		=	krcko.momo_action(info_text, [continue_action], [continue_option_text], [continue_key])
		#insert
		self.turn_machine.insert_action(momo_action)
	
			

	def inspect_item(self, item_index :int) -> None:
		'''momo form with item info'''
		
		#novcic komada 10, ukupna tezina je 13
		

		#check
		if not item_index in self.item_ids.keys():
			#no item with that index
			# show momo error		
			continue_action	 	= krcko.create_action("CONTINUE", [], [], [])
			continue_text :str 	= "nista"
			continue_key :str	= self.game.controls['MOMO']['CONTINUE']

			error_text :str = "mesto " + str(item_index) + " u prtljagu je prazno."

			momo_action	= krcko.create_action("MOMO",[krcko.ActionFlag.HALTING, krcko.ActionFlag.INSERTING],\
							['text','actions','action_names','action_keys'],\
							[error_text, [continue_action], ['jasno'], [continue_key]])
			#insert
			self.turn_machine.insert_action(momo_action)
			return	

		#all good, get item_name, item_eid
		item_name :str
		item_eid  :int
		item_name, item_eid = self.item_ids[item_index]
			
		amount :int = self.inventory[item_name]

		#get ent
		item_ent = self.scene.get_entity(item_eid)
	
		#inspect item action
		inspect_action = krcko.create_action("INSPECT_ITEM", [krcko.ActionFlag.INSERTING],\
							["item_eid", "amount"], [item_eid, amount])


		
		#insert
		self.turn_machine.insert_action(inspect_action)


	def draw_items(self) -> None:
		'''display inventory items'''

		#TODO: scrolling down if too many items

		
		curr_y :int	=	self.items_start_y_top
		#go trough items
		for item_name in self.inventory.keys():
			# i) item_name [amount]
			item :str = str(curr_y - self.items_start_y_top) +") " + item_name
			if self.inventory[item_name] > 1:	
				item += " [" + str(self.inventory[item_name]) + "]"
			#draw
			krcko.draw_text(self.view, item, curr_y, 2)
			#
			curr_y += 1


		self.last_item_y = curr_y



	def get_items(self) -> None:
		"get items from player inventory"
		
		#name : amount
		self.inventory :Dict[str:int] = {}
		#item_index : (name, item_eid) 
		self.item_ids :Dict[int:str] = {}
		#name : number_of 
		duplicates :Dict[str:int] = {}	
		
		curr_index 	:int = 0
		itm_eid 	:int
		#go trough items
		for itm_eid in self.player_ent['inventory'].items:
			if self.scene.entity_has_component(itm_eid, "item"):
				#get item ent
				item_ent	=	self.scene.get_entity(itm_eid)
			else:
				#something's wrong
				continue

			#don't add it here if it's equipped 
			if itm_eid in self.equipped.values():
				continue

		
			item_name :str = item_ent['item'].name
			if item_ent['item'].name in self.inventory.keys():
				#stack it
				if item_ent['item'].stackable:
					self.inventory[item_name] += item_ent['item'].amount
				else:
					#add number to the name 
					if item_ent['item'].name in duplicates.keys():
						duplicates[item_name] += 1
					else:
						duplicates[item_name] = 1

					item_name += " " + str(duplicates[item_name])
					#max amount of non-stackable items is 1	
					self.inventory[item_name] = 1
					#add to index table
					self.item_ids[curr_index] = (item_name, itm_eid)
					curr_index += 1
					
			else:
				self.inventory[item_name] =  item_ent['item'].amount
				#add to index table
				self.item_ids[curr_index] = (item_name, itm_eid)
				curr_index += 1 
			



	def draw_weight(self) -> None:
		'''displays inventory wieght'''

		weight :int = self.player_ent['inventory'].weight

		krcko.draw_text(self.view, "tezina:", self.view_rect.height  - self.weight_y_bottom, 2)
		self.draw_middle_text("[ " + str(weight) + " ]", self.view_rect.height - self.weight_y_bottom + 1) 


	
	def draw_middle_text(self, text :str, y :int) -> None:
                
		x : int = int(self.view_rect.width/2) - int(len(text)/2)
		#view too small for text
		if x < 0:
			return
                
		krcko.draw_text(self.view, text, y,x)
	
	def update_view(self):
		''' Update a view''' 
	
		main_window = self.game.main_window

		
		main_rect	:krcko.rectangle = krcko.rectangle(0,0,0,0)
		view_rect	:krcko.rectangle = krcko.rectangle(0,0,0,0)

		main_rect.height, main_rect.width = krcko.get_window_size(main_window)
		
		#inventory view is on the right side of the dungeon view,
		view_rect.y = main_rect.y + int((main_rect.height/100)*20) #20 from the top

		view_rect.x = main_rect.x + int((main_rect.width/100)*20)\
			 + main_rect.width - int((main_rect.width/100)*40) +1#dungeon view x + dungeon view width + 1

		view_rect.height = main_rect.height - int((main_rect.height/100)*23) 	#20 from top, and 3 to bottom
		view_rect.width  = main_rect.right - view_rect.x - 1  

		self.view_rect 	= view_rect
		self.view 	= krcko.create_sub_window(main_window,view_rect.height, view_rect.width, view_rect.y, view_rect.x)
		#clear view
		krcko.curse_clear(self.view)



sys_instance = InventoryView()	
