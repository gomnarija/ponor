class DungeonView(krcko.System):
	'''Draws dungeon stuff'''

	
	camera			 :krcko.rectangle = krcko.rectangle(10,10,0,0)
	camera_speed		 :int		  = 100 #per second
	
	def setup(self):
		
		win_height, _ = krcko.get_window_size(self.scene.game.main_window)

		#place camera above player
		self.player_ent	=	self.scene.get_entity_from_name("player")
		self.camera.x	=	self.player_ent['player'].room_rect.x
		#bound it to starting particles starting y
		self.camera.y	=	max(-100,self.player_ent['position'].y - (3 * win_height))

		self.start_camera_y	=	self.camera.y #used for counting scroll back


	
	cs :int					  =	0#frame counter
	player_found :bool			  =	False#initial camera over player
	camera_over_player :bool		  = 	False
	leftovers				  =	None#particles on screen from previous scene
								# used for smoother transitions
	last_draw :int				  =	-1	#last turn number that dungeon view was drawn
	def update(self):

		#get leftover particles
		if self.leftovers == None:
			self.leftovers :List[(int, int),int]	=	krcko.get_screen_text(self.scene.game.main_window)
			#
			self.leftover_size = krcko.point(0,0)
			self.leftover_size.y,\
				self.leftover_size.x		=	krcko.get_window_size(self.scene.game.main_window)

		#create curses subwindow that represents
		# a dungeon view
		# back view, only while camera is looking for player
		self.update_view()
		if not self.player_found:
			self.update_back_view()
			krcko.curse_clear(self.back_view)


		#get median fps
		m_fps	=	max(10, self.scene.game.clock.median_fps)

	
		self.update_camera()	
		# a camera is used to limit which world objects get to be 
		#  drawn at a current frame. Objects outside the camera rectangle
		#   won't be drawn.
		if self.cs * self.camera_speed >= m_fps or self.player_found:
			self.follow_player_with_camera()
			self.cs	= 0
		else:
			self.cs	+= 1





		#draw back if player still missing
		if not self.player_found:
			self.draw_back()

		#draw only at the end of the turn,
		#	or if window gets resized
		#		or if camera is not over player
		if (krcko.ActionFlag.ENDING in self.scene.game.turn_machine.action.flags and\
			 self.last_turn != self.scene.game.turn_machine.turn_number)	or\
				self.scene.game.window_resized or\
				not self.camera_over_player:


			#only after player has been found
			if self.player_found:
				#clear dungeon view	
				krcko.curse_clear(self.view)

				#draw view borders
				krcko.draw_window_border(self.view, tl = krcko.AC_DIAMOND,\
							tr = krcko.AC_DIAMOND,\
								bl  = krcko.AC_DIAMOND,\
									br = krcko.AC_DIAMOND)



				#view title
				self.display_game_title("[ ponor ]")

				#draw particles inside dungeon view
				self.draw_particles()

			#


			#draw current room where player is
			self.draw_current_room()
		
			#draw drawable objects
			self.draw_drawables()

		
			#
			self.last_turn	=	self.scene.game.turn_machine.turn_number


	
		#draw leftover from previous scene
		if not self.leftovers_done:
			self.draw_leftovers(self.camera.y - self.start_camera_y)


	
	def cleanup(self):
		pass


	def draw_particles(self) -> None:
		'''draw particles'''

		for ent, eid in self.scene.gen_entities("particles"):
			for position in ent['particles'].positions:
				#if particle object is inside camera rect
				if self.camera.contains_point(position):
					#world position to camera position
					camera_pos :krcko.point = self.world_to_camera(position)
					#draw
					krcko.draw_char(self.view, ent['particles'].ascii, camera_pos.y, camera_pos.x)


	def display_game_title(self, title :str) -> None:
		'''displays game title :) '''
		
		#put it in the middle
		title_point :krcko.point
		title_point = krcko.point(0, int(self.camera.width / 2) - int(len(title)/2))

		#draw it 
		krcko.draw_text(self.view, title, title_point.y, title_point.x)


	def world_to_camera(self, world_pos :krcko.point) -> krcko.point:
		'''World position to camera position'''
		
		camera_pos :krcko.point = krcko.point(0,0)
			
		#from world coords to camera coords
		camera_pos.y = world_pos.y - self.camera.y + 1 
		camera_pos.x = world_pos.x - self.camera.x + 1 


		return camera_pos

	def follow_player_with_camera(self):
		''' If player leaves the center area of the camera,
			follow him
		'''
		
		player_ent = self.player_ent

		#somethings wrong
		if 'player' not in player_ent.keys():
			logging.error("failed to get player entity ")
			return


		player_position = player_ent['position']



		#60% of the camera rect
		center_rect :krcko.rectangle = krcko.rectangle(\
				self.camera.height - int(self.camera.height/2.5),\
				self.camera.width  - int(self.camera.width/2.5),\
				self.camera.y + int(self.camera.height/5),\
				self.camera.x + int(self.camera.width/5))
	
		if not self.player_found:
			self.player_found 	=	center_rect.contains_point_full(player_position)
			#done, send start action	
			if self.player_found:
				self.start_action()

		#
		self.camera_over_player 	=	center_rect.contains_point_full(player_position)
	
		#too high
		if center_rect.bottom < player_position.y:
			self.camera.y += 1
		#too low
		if center_rect.top > player_position.y:
			self.camera.y -= 1
		#too right
		if center_rect.right < player_position.x:
			self.camera.x += 1
		#too left
		if center_rect.left > player_position.x:
			self.camera.x -= 1





	def draw_drawables(self) -> None:
		'''Draw entities with drawable component, that are inside current room_rect'''
	

		player_ent = self.player_ent
		room_rect :krcko.rectangle = player_ent['player'].room_rect

		for ent, _ in self.scene.gen_entities('drawable'):
			#entity doesn't have position component, can't be drawn
			if 'position' not in ent.keys():
				continue



			position_component = ent['position'] 
			drawable_component = ent['drawable'] 
			
			#don't draw it if it's not inside current room_rect
			if not room_rect.contains_point_full(krcko.point(position_component.y, position_component.x)):
				continue

			#if drawable object is inside camera rect
			if self.camera.contains_point(krcko.point(position_component.y, position_component.x )):
				#world position to camera position
				camera_pos :krcko.point = self.world_to_camera(position_component)
				krcko.do_with_color(self.view, drawable_component.color, krcko.draw_char, [self.view,drawable_component.ascii, camera_pos.y, camera_pos.x])



		#draw player on top of all other drawables
		player_position :krcko.point = krcko.point(player_ent['position'].y, player_ent['position'].x )
		if self.camera.contains_point(player_position):
				#world position to camera position
				camera_pos :krcko.point = self.world_to_camera(player_position)
				krcko.do_with_color(self.view, player_ent['drawable'].color, krcko.draw_char, [self.view,player_ent['drawable'].ascii, camera_pos.y, camera_pos.x])


		



	def update_camera(self) -> None:
		'''Update a camera'''


		camera_view    = self.view
		world_position :krcko.point = krcko.point(self.camera.y,self.camera.x)


		view_width :int
		view_height :int

		view_height, view_width = krcko.get_window_size(camera_view)
		
		self.camera :krcko.rectangle =\
			krcko.rectangle(view_height-2, view_width-2, world_position.y, world_position.x)



	def update_view(self) -> None:
		'''Update a view'''
		
		main_window = self.scene.game.main_window
		
		main_rect   :krcko.rectangle = krcko.rectangle(0,0,0,0)

		main_rect.height, main_rect.width = krcko.get_window_size(main_window)
	
		
		view_rect   :krcko.rectangle = krcko.rectangle(0,0,0,0)
		#when player is found dungeon view sub-window will be placed at 20% from the top, and 20% from
		# the left. and will span to 80% right and 97% down.


		view_rect.y = main_rect.y + int((main_rect.height/100)*20)
		view_rect.x = main_rect.x + int((main_rect.width/100)*20)

		view_rect.height = main_rect.height - int((main_rect.height/100)*23) #20 from top, and 3 to bottom
		view_rect.width  = main_rect.width  - int((main_rect.width/100)*40) #20 from left, and 20 to right


		self.view = krcko.create_sub_window(main_window,view_rect.height, view_rect.width, view_rect.y, view_rect.x)

		
	def draw_current_room(self) -> None:
		'''Draw current room where player is '''
	
		player_ent = self.player_ent

		player_component = player_ent['player']

		#entity id for the current room is saved in player component
		room_eid = player_component.current_room
		
		#room entity
		room_ent = self.scene.get_entity(room_eid)

		#somethings wrong
		if 'room' not in room_ent.keys():
			#logging.error("failed to get room entity ")
			
			return


		#room component
		room_component = room_ent['room']

		#floor component
		floor_component = room_ent['floor']
			
		floor_rect :krcko.rectangle
		for floor_rect in floor_component.floor_tiles:
			#see if floor rectangle fits in camera view
			fit_rect :krcko.rectangle 
			
			it_fits, fit_rect = self.camera.overlap(floor_rect)


			#from world coords to camera coords
			camera_pos :krcko.point = self.world_to_camera(krcko.point(fit_rect.y, fit_rect.x))
			fit_rect.y = camera_pos.y 
			fit_rect.x = camera_pos.x

			#it fits :)
			if it_fits: 
				krcko.draw_rectangle(self.view, floor_component.ascii, fit_rect)	





		krcko.draw_text(self.view, str(player_ent['position'].y), 2, 1)	
		krcko.draw_text(self.view, str(player_ent['position'].x), 3, 1)	

		in_room = False
		for floor_rect in floor_component.floor_tiles:
			if floor_rect.contains_point(krcko.point(player_ent['position'].y, player_ent['position'].x)):
				in_room = True


		#draw walls
		wall_eid :int
		for wall_eid in room_component.walls:
			self.draw_wall(wall_eid)
		
		#draw hallways
		hallway_eid :int
		for hallway_eid in room_component.hallways:	
			self.draw_hallway(hallway_eid)




	def draw_wall(self, wall_eid :int) -> None:
		'''Draw wall'''
		
	
		#wall entity	
		wall_ent = self.scene.get_entity(wall_eid)
		wall_component = wall_ent['wall']
		position_component = wall_ent['position']
		
		#create a wall rectangle	
		wall_rect :krcko.rectangle = krcko.rectangle(wall_component.height,wall_component.width,position_component.y,position_component.x)


		#see if wall rectangle fits in camera view
		fit_rect :krcko.rectangle 
			
		it_fits, fit_rect = self.camera.overlap(wall_rect)

		#from world coords to camera coords
		camera_pos :krcko.point = self.world_to_camera(krcko.point(fit_rect.y, fit_rect.x))

		
		#it fits :)
		if it_fits:
			if fit_rect.height == 1:
				krcko.draw_hline(self.view, wall_component.ascii, fit_rect.width , camera_pos.y, camera_pos.x)	
			elif fit_rect.width == 1:
				krcko.draw_vline(self.view, wall_component.ascii, fit_rect.height , camera_pos.y, camera_pos.x)	
				pass


	def draw_door(self, floor_component) -> None:
		'''Draw hallway door'''
	

		player_ent  = self.player_ent
		room_rect :krcko.rectangle = player_ent['player'].room_rect

		floor_rects = floor_component.floor_tiles
			
		#they could be the same rect
		start_rect	:krcko.rectangle = floor_rects[0] #from bottom or right
		goal_rect 	:krcko.rectangle = floor_rects[-1] #to top or left


		#check which part of the hallway is inside the current room rect
		if  room_rect.contains_point(goal_rect.tl):
			door :krcko.point = krcko.point(goal_rect.top, goal_rect.left)
		elif  room_rect.contains_point(start_rect.br):
			door :krcko.point = krcko.point(start_rect.bottom - 1,  start_rect.right - 1)

		#check if it fits inside the camera
		if self.camera.contains_point(door):
			camera_pos :krcko.point = self.world_to_camera(door)
			krcko.do_with_color(self.view, krcko.COLOR_WHITE_BLACK, krcko.draw_char, [self.view, floor_component.ascii,  camera_pos.y, camera_pos.x])




	def draw_hallway(self,hallway_eid :int) -> None:
		'''Draw a hallway,
			if player is inside it currently, draw it whole, 
			else, draw the doors only
		'''
		
		
		#floor_componet:
		#	floor_tiles : list of rectangles 
		#
		hallway_ent = self.scene.get_entity(hallway_eid)
		player_ent  = self.player_ent

		if 'hallway' not in hallway_ent.keys():
			logging.error("failed to get hallway entity")
			return

		floor_component = hallway_ent['floor']
		hallway_component = hallway_ent['hallway']


		floor_rect :krcko.rectangle
		is_inside  :bool = False
	
		#check if player is inside the hallway
		for floor_rect in floor_component.floor_tiles:
			if floor_rect.contains_point(krcko.point(\
					player_ent['position'].y, player_ent['position'].x)):
				is_inside = True
				break 


		#if player is not inside the hallway	
		# draw just the door (hallway ending that is inside current room_rect
		if not is_inside:
			self.draw_door(floor_component)
			return


		#player is inside, draw the whole hallway
	
		for floor_rect in floor_component.floor_tiles:

			#see if floor rectangle fits in camera view
			fit_rect :krcko.rectangle 
			
			it_fits, fit_rect = self.camera.overlap(floor_rect)

			#from world coords to camera coords
			fit_rect.y -= self.camera.y - 1 
			fit_rect.x -= self.camera.x - 1

			#it fits :)
			if it_fits: 
				krcko.draw_rectangle(self.view, floor_component.ascii, fit_rect)	


	leftover_view	=	None
	leftovers_done	=	False
	def draw_leftovers(self, scroll_back :int) -> None:
		'''draw leftover particles from previous scene
			for smoother transitions :)

		
		'''
	

		leftover_size = krcko.point(0,0)

		
		#if current window is smaller
		# than leftover one
		leftover_size.y		=	min(self.back_view_rect.height, self.leftover_size.y)
		leftover_size.x		=	min(self.back_view_rect.width, self.leftover_size.x)
	
		#create view if not already
		if self.leftover_view == None:
			self.leftover_view	=	krcko.create_sub_window(self.scene.game.main_window, leftover_size.y, leftover_size.x, 0, 0)

		#
		bottom :int	=	leftover_size.y - scroll_back
		
		#done, terminate view
		if bottom <= 0 or self.player_found:
			self.leftovers_done = True
			#clear window
			krcko.curse_clear(self.leftover_view)
			return	
			
		#
		for position, ascii in self.leftovers:
			# get coords
			y, x = position
			#scroll down
			y    -= scroll_back
			#
			if y >= 0 and y < bottom and\
				x >= 0 and x < leftover_size.x:
				#
				krcko.draw_char(self.leftover_view, ascii, y, x)

		



	def draw_back(self) -> None:
		'''draw particles in the back while camera is 
			looking for the player
		'''
	
		#back_view rect,  camera.y camera.x
		back_rect	=	krcko.rectangle(0,0,0,0)
		back_rect.copy(self.back_view_rect)
		back_rect.y	=	self.camera.y
		back_rect.x	=	self.camera.x


		#	
		for ent, eid in self.scene.gen_entities("particles"):
			for position in ent['particles'].positions:
				#if particle object is inside back_rect
				if position.y > back_rect.y and position.y < back_rect.bottom - 1 and\
					position.x > back_rect.x and position.x < back_rect.right - 1: 
					#draw at a position relative to camera
					krcko.draw_char(self.back_view, ent['particles'].ascii,position.y - self.camera.y, position.x - self.camera.x)
					pass
	
		


	back_view	=	None
	def update_back_view(self) -> None:
		'''back view used to display particles 
			in the back until player is found
		''' 

		main_window = self.scene.game.main_window
		main_rect   :krcko.rectangle = krcko.rectangle(0,0,0,0)

		main_rect.height, main_rect.width = krcko.get_window_size(main_window)
	
		
		back_view_rect   :krcko.rectangle = krcko.rectangle(0,0,0,0)
		#whole main window
		back_view_rect.copy(main_rect)

		self.back_view_rect = back_view_rect
		self.back_view = krcko.create_sub_window(main_window,back_view_rect.height, back_view_rect.width, back_view_rect.y, back_view_rect.x)


		

	def start_action(self) -> None:
		'''view is done loading, send start action '''
	
		start_action = krcko.create_action("START",[krcko.ActionFlag.ENDING], [], [])
		self.scene.game.turn_machine.add_action(start_action)
	
				
sys_instance = DungeonView()
