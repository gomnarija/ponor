class InventoryView(krcko.System):
	'''Displays the inventory'''
	
	
	#STELOVANJE
	weight_y_bottom 	:int	=	4
	items_start_y_top	:int	=	3

	def setup(self):
		pass


	_started :bool = False#wait for start action	
	def update(self):
		
		if not self._started:
			if self.scene.game.turn_machine.action_name == "START":
				self._started = True
			else:
				return
	


		self.update_view()

		#get player ent
		self.player_ent = self.scene.get_entity_from_name("player")


		#draw view borders
		krcko.draw_window_border(self.view, tl = krcko.AC_DIAMOND,\
					tr = krcko.AC_DIAMOND,\
					bl  = krcko.AC_DIAMOND,\
					br = krcko.AC_DIAMOND)


		#
		self.draw_middle_text("[ prtljag ]", 0)
		#
		self.draw_weight()
		#
		self.get_items()
		self.draw_items()


	def cleanup(self):
		pass





	def draw_items(self) -> None:
		'''display inventory items'''

		#TODO: scrolling down if too many items

		
		curr_y :int	=	self.items_start_y_top
		#go trough items
		for item_name in self.inventory.keys():
			# i) item_name [amount]
			item :str = str(self.items_start_y_top-curr_y) +") " + item_name + " [ " + str(self.inventory[item_name]) + " ]"
			#draw
			self.draw_middle_text(item, curr_y)
			#
			curr_y += 1



	def get_items(self) -> None:
		"get items from player inventory"
		
		#name : amount
		self.inventory :Dict[str:int] = {}
	
		
		itm_eid :int
		#go trough items
		for itm_eid in self.player_ent['inventory'].items:
			if self.scene.entity_has_component(itm_eid, "item"):
				#get item ent
				item_ent	=	self.scene.get_entity(itm_eid)
			else:
				#something's wrong
				continue

			if item_ent['item'].name in self.inventory.keys():
				self.inventory[item_ent['item'].name] += item_ent['item'].amount
			else:
				self.inventory[item_ent['item'].name] =  item_ent['item'].amount
			
	

	

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
	
		main_window = self.scene.game.main_window

		
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
