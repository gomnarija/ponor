class DungeonView(krcko.System):
	'''Draws dungeon stuff'''

	
	camera			 :krcko.rectangle = krcko.rectangle(10,10,10,10)


	def setup(self):
		pass
		
	def update(self):
	
		#create curses subwindow that represents
		# a dungeon view
		self.update_view()


		# a camera is used to limit which world objects get to be 
		#  drawn at a current frame. Objects outside the camera rectangle
		#   won't be drawn.
		self.follow_player_with_camera()	
		self.update_camera()	
	

		#draw view borders
		krcko.draw_window_border(self.view, tl = krcko.AC_DIAMOND,\
							tr = krcko.AC_DIAMOND,\
								bl  = krcko.AC_DIAMOND,\
									br = krcko.AC_DIAMOND)


		#draw current room where player is
		self.draw_current_room()
		
		#draw drawable objects
		self.draw_drawables()
	
	def cleanup(self):
		pass


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
		
		player_ent = self.scene.get_entity_from_name("player")

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
	

		player_ent = self.scene.get_entity_from_name("player")
		room_rect :krcko.rectangle = player_ent['player'].room_rect

		for ent in self.scene.gen_entities('drawable'):
			#entity doesn't have position component, can't be drawn
			if 'position' not in ent.keys():
				continue



			position_component = ent['position'] 
			drawable_component = ent['drawable'] 
			
			#don't draw it if it's not inside current room_rect
			if not room_rect.contains_point(krcko.point(position_component.y, position_component.x)):
				continue


			#if drawable object is inside camera rect
			if self.camera.contains_point(krcko.point(position_component.y, position_component.x )):
				#world position to camera position
				camera_pos :krcko.point = self.world_to_camera(position_component)
				krcko.do_with_color(self.view, drawable_component.color, krcko.draw_char, [self.view,drawable_component.ascii, camera_pos.y, camera_pos.x])




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
		

		#dungeon view sub-window will be placed at 15% from the top, and 10% from
		# the left. and will span to 90% right and 97% down.

		view_rect   :krcko.rectangle = krcko.rectangle(0,0,0,0)

		view_rect.y = main_rect.y + int((main_rect.height/100)*15)
		view_rect.x = main_rect.x + int((main_rect.width/100)*10)

		view_rect.height = main_rect.height - int((main_rect.height/100)*18) #20 from top, and 3 to bottom
		view_rect.width  = main_rect.width  - int((main_rect.width/100)*20) #10 from left, and 10 to right


		self.view = krcko.create_sub_window(main_window,view_rect.height, view_rect.width, view_rect.y, view_rect.x)

	
	def draw_current_room(self) -> None:
		'''Draw current room where player is '''
	
		player_ent = self.scene.get_entity_from_name("player")

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
	

		player_ent  = self.scene.get_entity_from_name("player")
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
			krcko.do_with_color(self.view, krcko.COLOR_YELLOW_BLACK, krcko.draw_char, [self.view, floor_component.ascii,  camera_pos.y, camera_pos.x])



		




	def draw_hallway(self,hallway_eid :int) -> None:
		'''Draw a hallway,
			if player is inside it currently, draw it whole, 
			else, draw only door
		'''
		
		
		#floor_componet:
		#	floor_tiles : list of rectangles 
		#
		hallway_ent = self.scene.get_entity(hallway_eid)
		player_ent  = self.scene.get_entity_from_name("player")

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






	
				
sys_instance = DungeonView()
