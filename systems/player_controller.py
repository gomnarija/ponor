class PlayerControler(krcko.System):
	'''player controller'''

	import random
	

	def setup(self):
		self.player_ent = self.scene.get_entity_from_name("player")
		self.player_position = self.player_ent['position']
		self.spawn_player()

	def update(self):
		self.move_detection() #detects input, sends action 
		self.do_move() #detects action, moves player

		#if player goes outside current room_rect,
		# find another one
		if not self.player_ent['player'].room_rect.contains_point_full(krcko.point(self.player_position.y , self.player_position.x )):
			self.find_room_rect()

	def cleanup(self):
		pass




	def move_detection(self):
	

		new_y :int = self.player_position.y
		new_x :int = self.player_position.x
		
		controls 	= self.scene.game.controls


		key = self.scene.game.get_key()

		if key == controls['PLAYER']['MOVE_UP']:
			new_y -= 1
		if key == controls['PLAYER']['MOVE_DOWN']:
			new_y += 1
		if key == controls['PLAYER']['MOVE_LEFT']:
			new_x -= 1
		if key == controls['PLAYER']['MOVE_RIGHT']:
			new_x += 1


		#if move was detected
		if new_y != self.player_position.y or\
			new_x != self.player_position.x:
			#create new move action
			move_action, fact = krcko.create_action("MOVE_PLAYER",[krcko.ActionFlag.SINGLE, krcko.ActionFlag.ENDING], ['new_y', 'new_x'],[new_y, new_x])		
			#add action to next turn
			self.scene.game.turn_machine.add_action(move_action)

		

	def is_floor(self, position :krcko.point) -> bool:
		'''check if point is on floor'''

	
		#go trough every entity which has floor component
		for ent, _ in self.scene.gen_entities("floor"):
			#get floor rects
			floor_component = ent["floor"]
			floor_rects	= floor_component.floor_tiles
			#check if it contains it
			floor_rect  :krcko.rectangle
			for floor_rect in floor_rects:
				if floor_rect.contains_point(position):
					return True 


		return False
		

	def find_room_rect(self) -> None:
		''' finds a room rect that contains players '''
		
		rooms_group = self.scene.get_group_from_name("rooms")	
		#go trough rooms
		for room_eid in rooms_group:
			room_ent = self.scene.get_entity(room_eid)
			#check if room rect contains player
			position :krcko.point = krcko.point(self.player_position.y, self.player_position.x)
			#it does, assign it
			if room_ent['room'].room_rect.contains_point(position):
				self.player_ent['player'].room_rect = room_ent['room'].room_rect
				#assign current room
				self.player_ent['player'].current_room = room_eid	
				return




	def do_move(self):
		'''moves the player, if action is detected'''

		
		game = self.scene.game

		#check current action
		if type(game.turn_machine.action).__name__ != "MOVE_PLAYER":
			return
		
		#get the action
		args = game.turn_machine.action

	
		#new position
		new_y :int = args.new_y
		new_x :int = args.new_x
			


		#check if new position is on the floor
		# if not, don't move
		if not self.is_floor(krcko.point(new_y, new_x)):
			return

		#TODO:
		#	check if there's something there :I

		

		self.player_position.y = new_y
		self.player_position.x = new_x






	def spawn_player(self) -> None:
		'''Spawns player in a random room '''

		#get room eids
		rooms_group = self.scene.get_group_from_name("rooms")	


		#choose random from set :/
		random_eid :int = self.random.randint(0, len(rooms_group)-1)
		curr_eid :int   = 0

		room_ent :Dict = {}


		for room_eid in rooms_group:
			if curr_eid == random_eid:
				room_ent = self.scene.get_entity(room_eid) 
				break
			curr_eid += 1

		#place player somewhere in the room
		rect :krcko.rectangle = room_ent['floor'].floor_tiles[self.random.randint(0,len(room_ent['floor'].floor_tiles) - 1)]
		#at the center of the rect
		self.player_ent['position'].y = rect.y + int(rect.height/2)
		self.player_ent['position'].x = rect.x + int(rect.width/2)
		
			
		#asign room eid
		self.player_ent['player'].current_room = room_eid
			
		
		#asign room_rect
		self.player_ent['player'].room_rect = room_ent['room'].room_rect		


		#set ascii
		self.player_ent['drawable'].ascii = self.scene.game.ascii_table.getint('DEFAULT','PLAYER')



sys_instance = PlayerControler()	
