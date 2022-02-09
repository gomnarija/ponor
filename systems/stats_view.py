class StatsView(krcko.System):
	'''Displays some stats'''
	
	
	#STELOVANJE
	health_y_top		:int	= 5
	name_y_top		:int	= 2
	turn_number_y_bottom	:int	= 4
	depth_y_bottom		:int	= 6

	def setup(self):
		pass
	
	def update(self):
	
		self.update_view()

		#draw view borders
		krcko.draw_window_border(self.view, tl = krcko.AC_DIAMOND,\
					tr = krcko.AC_DIAMOND,\
					bl  = krcko.AC_DIAMOND,\
					br = krcko.AC_DIAMOND)


		self.display_player_name()
		self.display_health()
		self.display_turn_number()
		self.display_depth()

	def cleanup(self):
		pass

	


	def draw_middle_text(self, text :str, y :int) -> None:
	

		x : int = int(self.view_rect.width/2) - int(len(text)/2)
		#view too small for text
		if x < 0:
			return

		krcko.draw_text(self.view, text, y,x) 
	

	def display_player_name(self):
		''' displays player name '''
	
		player_ent = self.scene.get_entity_from_name("player")

		player = player_ent['player']
		
		self.draw_middle_text("[" + player.name + "]", self.name_y_top)	




	def display_health(self):
		'''displays player health '''
		
		player_ent = self.scene.get_entity_from_name("player")

		player_health = player_ent['health']
		
		krcko.draw_text(self.view,"zivot:", self.health_y_top, 2)	
		self.draw_middle_text(str(player_health.amount)+"/"+str(player_health.max_health), self.health_y_top+1)	

	def display_turn_number(self):
		'''displays current turn number '''
		
		game = self.scene.game
		
		

		y = self.view_rect.height - self.turn_number_y_bottom

		krcko.draw_text(self.view,"potez:", y, 2)	
		self.draw_middle_text(" [ " + str(game.turn_machine.turn_number) + " ] ", y+1)	

	def display_depth(self):
		'''displays current depth '''
			
		
		player_ent = self.scene.get_entity_from_name("player")

		y = self.view_rect.height - self.depth_y_bottom

		krcko.draw_text(self.view,"dubina:", y, 2)	
		
		self.draw_middle_text(" [ "+ str(player_ent['player'].depth) + " ] ", y + 1)	




	def update_view(self):
		''' Update a view''' 
	
		main_window = self.scene.game.main_window

		
		main_rect	:krcko.rectangle = krcko.rectangle(0,0,0,0)
		view_rect	:krcko.rectangle = krcko.rectangle(0,0,0,0)

		main_rect.height, main_rect.width = krcko.get_window_size(main_window)
		
		#stats view is on the left side of the dungeon view,
		view_rect.y = main_rect.y + int((main_rect.height/100)*20) #20 from the top
		view_rect.x = main_rect.x + 1

		view_rect.height = main_rect.height - int((main_rect.height/100)*23) #20 from top, and 3 to bottom
		view_rect.width  = int((main_rect.width/100)*15) #15 from the left

		self.view_rect 	= view_rect
		self.view 	= krcko.create_sub_window(main_window,view_rect.height, view_rect.width, view_rect.y, view_rect.x)





sys_instance = StatsView()	
