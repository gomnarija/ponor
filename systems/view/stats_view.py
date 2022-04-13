class StatsView(krcko.System):
	'''Displays some stats'''
	
	
	#STELOVANJE
	name_y_top		:int	= 0
	health_y_top		:int	= 2
	hunger_y_top		:int	= 6
	turn_number_y_bottom	:int	= 4
	depth_y_bottom		:int	= 6

	def setup(self):
		
		#momo 
		self.stats_momo = krcko.Momo()
		self.stats_momo.load(defs.MOM_DIR_PATH + "stats_view.momo")	



		#run it 
		self.stats_momo.run()

	_started :bool	= False#wait for start action	
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


		self.display_player_name()
		self.display_health()
		self.display_hunger()
		self.display_turn_number()
		self.display_depth()

	def cleanup(self):
		pass

	

	def bar(self, amount :int, max :int, bar_width :int) -> List[int]:
		'''fills the bar'''
	
		
		#amount/max * bar_width
		bars :int = min(int((amount/max) * bar_width), bar_width)

		#load up ascii characters
		bar_full 	:str = self.game.get_ascii("BAR_FULL")
		bar_empty 	:str = self.game.get_ascii("BAR_EMPTY")


		#
		return ([bar_full] * bars) + ([bar_empty] * (bar_width - bars))


	def draw_middle_text(self, text :str, y :int) -> None:
	

		x : int = int(self.view_rect.width/2) - int(len(text)/2)
		#view too small for text
		if x < 0:
			return

		krcko.draw_text(self.view, text, y,x) 
	

	def display_player_name(self) -> None:
		''' displays player name '''
	
		player_ent = self.scene.get_entity_from_name("player")
		player = player_ent['player']
		self.draw_middle_text("[ " + player.name + " ]", self.name_y_top)	




	def display_health(self) -> None:
		'''displays player health '''
	

		#get health tag text from momo file
		health_tag :str = self.stats_momo.pick("HEALTH") + ":"
			
		#get player health
		player_ent = self.scene.get_entity_from_name("player")
		player_health = player_ent['health']

		#make health bar
		bar :str = self.bar(player_health.amount, player_health.max_health, self.bar_width)
		
		#draw
		krcko.draw_text(self.view,health_tag, self.health_y_top, 2)	
		self.draw_middle_text(bar, self.health_y_top+2)	

	def display_hunger(self) -> None:
		'''displays player hunger '''
	

		#get hunger tag text from momo file
		hunger_tag :str = self.stats_momo.pick("HUNGER") + ":"
			
		#get player hunger
		player_ent 	= self.scene.get_entity_from_name("player")
		player_hunger 	= player_ent['hunger']

		#make hunger bar
		bar :str = self.bar(player_hunger.amount, player_hunger.max_hunger, self.bar_width)
		
		#draw
		krcko.draw_text(self.view,hunger_tag, self.hunger_y_top, 2)	
		self.draw_middle_text(bar, self.hunger_y_top+2)

	
	def display_turn_number(self) -> None:
		'''displays current turn number '''
		
		#
		turn_tag :str	= self.stats_momo.pick("TURN") + ":"
		y :int 		= self.view_rect.height - self.turn_number_y_bottom

		krcko.draw_text(self.view,turn_tag, y, 2)	
		self.draw_middle_text(" [ " + str(self.turn_machine.turn_number) + " ] ", y+1)	



	def display_depth(self):
		'''displays current depth '''
			
		
		player_ent 	= self.scene.get_entity_from_name("player")
		depth_tag :str 	= self.stats_momo.pick("DEPTH") + ":"
		y :int		= self.view_rect.height - self.depth_y_bottom

		krcko.draw_text(self.view,depth_tag, y, 2)	
		self.draw_middle_text(" [ "+ str(player_ent['player'].depth) + " ] ", y + 1)	




	def update_view(self):
		''' Update a view''' 
	
		main_window = self.game.main_window

		
		main_rect	:krcko.rectangle = krcko.rectangle(0,0,0,0)
		view_rect	:krcko.rectangle = krcko.rectangle(0,0,0,0)

		main_rect.height, main_rect.width = krcko.get_window_size(main_window)
		
		#stats view is on the left side of the dungeon view,
		view_rect.y = main_rect.y + int((main_rect.height/100)*20) #20 from the top
		view_rect.x = main_rect.x + 1

		view_rect.height = main_rect.height - int((main_rect.height/100)*23) #20 from top, and 3 to bottom
		view_rect.width  = int((main_rect.width/100)*20) - 2 #20 from the left - 2

		self.view_rect 	= view_rect
		self.view 	= krcko.create_sub_window(main_window,view_rect.height, view_rect.width, view_rect.y, view_rect.x)


		#bar width, view_width - 6
		self.bar_width = self.view_rect.width - 6


		#clear view
		krcko.curse_clear(self.view)





sys_instance = StatsView()	
