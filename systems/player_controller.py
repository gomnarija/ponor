class PlayerControler(krcko.System):
	'''player controller'''

	import random
	

	def setup(self):
		self.player_ent = self.scene.get_entity_from_name("player")
		self.player_position = self.player_ent['position']
		self.spawn_player()



	_started :bool	=	False#wait for start action
	def update(self):
		if not self._started:
			if self.turn_machine.action_name == "START":
				self._started = True
			else:
				return

		self.do_move() #detects action, moves player
		self.move_detection() #detects input, sends action 

		#if player goes outside current room_rect,
		# find another one
		if not self.player_ent['player'].room_rect.contains_point_full(krcko.point(self.player_position.y , self.player_position.x )):
			self.find_room_rect()

		#check for item pickup
		self.pickup_detection()

	def cleanup(self):
		pass




	def move_detection(self):
	

		#can't move if turn machine is halted :( 
		if self.turn_machine.is_halted:
			return
		

		new_y :int = self.player_position.y
		new_x :int = self.player_position.x
		
		controls 	= self.game.controls


		key = self.game.get_key()

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
			move_action = krcko.create_action("MOVE_PLAYER",[krcko.ActionFlag.SINGLE, krcko.ActionFlag.ENTAILS],\
									['new_y', 'new_x'],[new_y, new_x],\
									 entails = self.turn_machine.ending_action)		
			#add action to next turn
			self.turn_machine.add_action(move_action)

		

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
			if room_ent['room'].room_rect.contains_point_full(position):
				self.player_ent['player'].room_rect = room_ent['room'].room_rect
				#assign current room
				self.player_ent['player'].current_room = room_eid	
				return




	def do_move(self):
		'''moves the player, if action is detected'''

		
		game = self.game

		#check current action
		if game.turn_machine.action_name != "MOVE_PLAYER":
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
		

		self.player_position.y = new_y
		self.player_position.x = new_x



	def pickup_detection(self) -> None:
		'''look for pickup action '''

		if self.turn_machine.action_name == "ITEM_PICKUP":
			#get eid 
			itm_eid :int = self.turn_machine.action.item_eid
			#pickup item
			self.pickup_item(itm_eid)



	def pickup_item(self, itm_eid :int) -> None:
		'''item pickup:
			remove position, drawable from item ent,
			add item_eid to inventory
			momo notification
		'''
		
		#something's wrong
		if not self.scene.entity_has_component(itm_eid, "item") or\
			not self.scene.entity_has_component(itm_eid, "position") or\
				not self.scene.entity_has_component(itm_eid, "drawable"):
			#
			return
	
		#get item entity
		item_ent = self.scene.get_entity(itm_eid)
	

		#remove position and drawable components
		self.scene.remove_component(itm_eid, "position")
		self.scene.remove_component(itm_eid, "drawable")

	
		#add to inventory
		self.player_ent['inventory'].items.append(itm_eid)
		self.player_ent['inventory'].weight += int(item_ent['item'].weight) * int(item_ent['item'].amount)	

	

		not_text	:str	=	"pokupljeno"
		cont_key	:str	=	self.game.controls['MOMO']['CONTINUE']

		#momo notification
		continue_action = krcko.create_action("CONTINUE", [], [], []) 
		momo_not_action = krcko.create_action("MOMO",\
					[krcko.ActionFlag.HALTING],\
					['text','actions','action_names','action_keys'],\
					[not_text, [continue_action], ['jasno'], [cont_key]])
		
					
		#insert
		self.turn_machine.insert_action(momo_not_action)
	


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
		self.player_ent['drawable'].ascii = self.game.get_ascii('PLAYER')



sys_instance = PlayerControler()	
