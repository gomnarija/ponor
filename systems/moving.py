class Moving(krcko.System):
	


	import random

	def setup(self):	
		#get player
		self.player_ent = self.scene.get_entity_from_name("player")

	
		for npc_ent, npc_eid in self.scene.gen_entities("movable"):
			#must have position 
			if not self.scene.entity_has_component(npc_eid, "position"):
				continue 

			npc_ent['movable'].goal = krcko.point(npc_ent['position'].y, npc_ent['position'].x)


	def update(self):
		
		#get current room rect
		self.room_rect	= 	self.player_ent['player'].room_rect

		#get current action
		action = self.turn_machine.action
		
		#check if npc should move
		if self.turn_machine.action_name == "MOVE_NPC":
			self.do_move(action.npc_eid, action.new_y, action.new_x)


		#at the end of the turn
		if krcko.ActionFlag.ENDING in action.flags:
			#move npcs in this room that have movable component
			for npc_ent, npc_eid in self.scene.gen_entities("movable"):
				#if npc is interacting with player
				# don't move it 
				if self.scene.entity_has_component(npc_eid, "npc") and\
					npc_ent['npc'].is_interacting:
					#
					continue
				#move the ones that are inside current
				# room_rect
				if self.room_rect.contains_point(npc_ent['position']):
					self.move_npc(npc_eid)
	

	def cleanup(self):
		pass




	def assign_goal(self, npc_eid) -> None:
		'''assign new goal to an entity'''

		npc_ent = self.scene.get_entity(npc_eid)
		if not self.scene.entity_has_component(npc_eid, "movable") or\
			not self.scene.entity_has_component(npc_eid, "position"):
			#
			logging.error("Failed to get movable entity.")
			return

		#assign new goal
		#
		# get room
		room_ent = self.scene.get_entity(self.player_ent['player'].current_room)
		if not self.scene.entity_has_component(self.player_ent['player'].current_room, "room"):
			logging.error("failed to get current room")
			return
		#
		#pick a random floor rect inside current room
		random_rect :krcko.rectangle = self.random.choice(room_ent['floor'].floor_tiles)
		#put the new goal somewhere random on this floor rect
		npc_ent['movable'].goal = krcko.point(self.random.randint(random_rect.top, random_rect.bottom - 1),\
							self.random.randint(random_rect.left, random_rect.right - 1))





	def do_move(self, npc_eid :int, new_y :int, new_x :int) -> None:
		'''move entity to the new location'''

		npc_ent = self.scene.get_entity(npc_eid)
		if not self.scene.entity_has_component(npc_eid, "movable") or\
			not self.scene.entity_has_component(npc_eid, "position"):
			#
			logging.error("Failed to get movable entity. ")
			return


		#
		#check if some drawable npc, or player is already at that position
		for n_ent, n_eid in self.scene.gen_entities("npc"):
			#
			if self.scene.entity_has_component(n_eid, "npc") and\
				self.scene.entity_has_component(n_eid, "drawable") and\
					self.scene.entity_has_component(n_eid, "position"):
				#
				if n_eid == npc_eid:
					continue
				#check if they're at the same position
				if new_y == n_ent['position'].y and\
					new_x == n_ent['position'].x:
					#change goal
					self.assign_goal(npc_eid)
					return

		#or player
		if new_y == self.player_ent['position'].y and\
			new_x == self.player_ent['position'].x:
			#change goal
			self.assign_goal(npc_eid)
			return

		
		#all good
		npc_ent['position'].y	=	new_y
		npc_ent['position'].x	=	new_x

		
	def move_npc(self,npc_eid :int) -> None:
		'''move entity towards it's goal point'''


		npc_ent = self.scene.get_entity(npc_eid)
		if not self.scene.entity_has_component(npc_eid, "movable") or\
			not self.scene.entity_has_component(npc_eid, "position"):
			#
			logging.error("Failed to get movable entity .")
			return

		#get goal point
		goal_point :krcko.point = npc_ent['movable'].goal
		#current position
		curr_position :krcko.point = krcko.point(npc_ent['position'].y, npc_ent['position'].x)

		#if current npc position is the same as it's goal
		if curr_position.y == goal_point.y and\
			curr_position.x == goal_point.x:
			#assign a new goal to it
			self.assign_goal(npc_eid)
			#and return
			return
		
		#4 possible moves
		move_up 	:krcko.point	=	krcko.point(curr_position.y - 1, curr_position.x)
		move_down 	:krcko.point	=	krcko.point(curr_position.y + 1, curr_position.x)
		move_left 	:krcko.point	=	krcko.point(curr_position.y, curr_position.x - 1)
		move_right 	:krcko.point	=	krcko.point(curr_position.y, curr_position.x + 1)

		possible :List[krcko.point]	=	[move_up, move_down, move_left, move_right]
		#avaliable moves
		avaliable :List[krcko.point]	=	[]
		


		#get room
		room_ent = self.scene.get_entity(self.player_ent['player'].current_room)
		if not self.scene.entity_has_component(self.player_ent['player'].current_room, "room"):
			logging.error("failed to get current room")
			return


		#check if possible moves are inside 
		#	room floor rects
		for move in possible:
			for floor_rect in room_ent['floor'].floor_tiles:
				if floor_rect.contains_point(move):
					avaliable.append(move)
					break


		min_distance 	:float 		=	2607.02 #:)
		closest_move	:krcko.point	=	None
		#find the avaliable goal that is closest
		# to the goal point
		for a_move in avaliable:
			
			if a_move.distance(goal_point) < min_distance:
				min_distance	= a_move.distance(goal_point)
				closest_move 	= a_move
			

		#no moves avaliable,
		# probably shouldn't happen
		if not closest_move:
			return

		#create move action
		npc_move_action		 = krcko.create_action("MOVE_NPC", [], ['npc_eid', 'new_y', 'new_x'], [npc_eid, closest_move.y, closest_move.x])
		#add action to next turn
		self.turn_machine.add_action(npc_move_action)	





sys_instance = Moving()
