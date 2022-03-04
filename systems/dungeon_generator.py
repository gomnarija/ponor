class DungeonGenerator(krcko.System):
	'''System for randomly generating dungeons'''


	from typing import List,Tuple	
	import random
	from operator import mul




	# Stelovanje
	#average size of the rectangle which contains the room
	avrg_rect :krcko.rectangle = krcko.rectangle(35,65,0,0)
	#minimum size of the rectangle which contains the room
	min_rect  :krcko.rectangle = krcko.rectangle(15,25,0,0)
	#minimum size of the rectangle that constructs a room
	min_room_rect :krcko.rectangle = krcko.rectangle(5,10,0,0)
	


	m_hallway_table :Dict[int,List[int]] 	  = {}
	m_room_eids_table :Dict[int,int] 	  = {}

	def setup(self):

		#rectangle containing a whole dungeon
		dungeon_rectangle :krcko.rectangle = krcko.rectangle(200,200,0,0)

		#rectangles containing rooms
		room_rects :List[krcko.rectangle]
		room_rects = self.bsp_generation(dungeon_rectangle)

		#rooms are just lists with rectangles that construct a room
		rooms :List[List[krcko.rectangle]] = []
		room_rect :krcko.rectangle
		#generate rooms 
		for room_rect in room_rects:
			rooms.append(self.generate_room(room_rect))
		
		hallways :List[List[krcko.rectangle]]
		#generate hallways between rooms
		hallways = self.generate_hallways(room_rects,rooms)
		

		self.gen_room_entities(rooms, room_rects, hallways)
		self.gen_hallway_entities(hallways)
	
		

	def update(self):
		pass
	def cleanup(self):
		pass



	def gen_room_entities(self, rooms :List[List[krcko.rectangle]], room_rects :List[krcko.rectangle], hallways :List[List[krcko.rectangle]]) -> None:
		'''Generates room entities
			components:
				floor
				room
		'''
		
		room_eids :List[int] = []
		
		#load patterns
		comp, floor_component_fact = krcko.load_component(defs.PAT_DIR_PATH+"floor.json")
		comp, room_component_fact = krcko.load_component(defs.PAT_DIR_PATH+"room.json")


		room :List[krcko.rectangle] #current room	
		rect :krcko.rectangle #current rect
		
		for room in rooms:

			rects :List[krcko.rectangle] = [] #all the rects in a room
			for rect in room:
				rects.append(rect)
		

			#empty room, shouldn't happen but still	
			if len(rects) == 0:
				continue
	
			#generate walls around a room
			wall_eids :List[int] = self.gen_wall_entities(room, hallways )


			#floor component:
			# ascii 
			# floor_rects
			room_floor_ascii 	:int
			room_floor_ascii	= self.game.get_ascii('ROOM_FLOOR')

	
			floor_component = floor_component_fact(room_floor_ascii, rects)

			#room component:
			room_component = room_component_fact(room_rects[rooms.index(room)], wall_eids, [])	
			
			#create new room entity
			self.m_room_eids_table[rooms.index(room)] = self.scene.add_entity(floor_component,room_component,  ent_name = "room")
			room_eids.append(self.m_room_eids_table[rooms.index(room)])


		#create rooms group
		self.scene.add_group(*room_eids,group_name = "rooms")




	def gen_hallway_entities(self, hallways :List[List[krcko.rectangle]], ) -> None:
		'''Generates hallways
			components:
				floor
				hallway
		'''
		
		hallway_eids :List[int] = []

		#load patterns
		comp, floor_component_fact 	= krcko.load_component(defs.PAT_DIR_PATH+"floor.json")
		comp, hallway_component_fact 	= krcko.load_component(defs.PAT_DIR_PATH+"hallway.json")

		
		#add rects to the hallway component
		hallway :List[krcko.point]

		for hallway in hallways:
			
			rects :List[krcko.rectangle] = []#rectangles constructing a hallway
			for rect in hallway:
				rects.append(rect)

			#empty hallway, shouldn't happen
			if len(rects) == 0:
				continue

			room_eids :List[int] = []
			#find room eids of rooms that this hallway connects
			for room_id in self.m_hallway_table.keys():
				if hallways.index(hallway) in self.m_hallway_table[room_id]:
					room_eids.append(self.m_room_eids_table[room_id]) 


			#floor component
			# ascii
			# floor tiles	

			hallway_floor_ascii 	:int
			hallway_floor_ascii	= self.game.get_ascii('HALLWAY_FLOOR')


			floor_component   = floor_component_fact(hallway_floor_ascii , rects)
		
			#hallway component
			# rooms
			hallway_component = hallway_component_fact(room_eids)

	

			#create hallway entity	
			hallway_eids.append(self.scene.add_entity(floor_component, hallway_component, ent_name = "hallway"))
	
			#add hallway eid to rooms
			room_eid :int
			for room_eid in room_eids:
				room_ent = self.scene.get_entity(room_eid)
				
				#check if entity is really room, probably should do something about this
				# entity checking#TODO
				if not 'room' in room_ent.keys():
					logging.error("failed to get room entity")
					continue

				#append last added hallway
				room_ent['room'].hallways.append(hallway_eids[-1])



		#create hallway group	
		self.scene.add_group(*hallway_eids, group_name="hallways")


	def trim_wall(self, wall :krcko.rectangle, room :List[krcko.rectangle]) ->List[krcko.rectangle]:
		'''Trim a given wall if it overlaps with rect'''
		
		#recursion end
		if len(room) == 0:
			return [wall]

		#finished ones	
		trimmed :List[rectangle] = []

		rect :krcko.rectangle
		rect = room[0]
		
		#check rect overlaps the wall
		they_overlap :bool
		overlap_rect :krcko.rectangle
		they_overlap, overlap_rect  = wall.overlap(rect)

		#if wall and rectangle don't ovelarp, continue
		# with the next rectangle
		if not they_overlap:
			return self.trim_wall(wall, room[1:])


		#if they do overlap 
		# crop the wall
		trimmed_rects :List[krcko.rectangle] = self.do_crop(overlap_rect, wall)
		#trim newly cropped parts
		for t_rect in trimmed_rects:
			trimmed += self.trim_wall(t_rect, room[1:])

		return trimmed


	def gen_wall_entities(self, room :List[krcko.rectangle], hallways :List[List[krcko.rectangle]]) -> List[int]:
		''' Generates walls around a given room,
			returns list of wall eids.
		'''
		
		wall_eids :List[int] = []	
	
		#load patterns
		comp, wall_component_fact 	= krcko.load_component(defs.PAT_DIR_PATH+"wall.json")
		comp, position_component_fact 	= krcko.load_component(defs.PAT_DIR_PATH+"position.json")


		rect 		:krcko.rectangle #current rectangle in the room

		room_and_hallways :List[krcko.rectangle] = [*room] #used when trimming

		#add rectangles from the hallways
		for hallway in hallways:
			room_and_hallways += [*hallway]



		

		for rect in room:

			#get the rect edges
			top_rect :krcko.rectangle 	= krcko.rectangle(1, rect.width, rect.top - 1,rect.left )		
			bottom_rect :krcko.rectangle 	= krcko.rectangle(1, rect.width, rect.bottom,rect.left)		
			left_rect :krcko.rectangle 	= krcko.rectangle(rect.height, 1,  rect.top,rect.left - 1)		
			right_rect :krcko.rectangle 	= krcko.rectangle(rect.height, 1,  rect.top,rect.right)		
			
			sides :List[krcko.rectangle]    = [top_rect, bottom_rect, left_rect, right_rect]
			trimmed_walls	:List[krcko.rectangle] = [] #walls after trimming


			#trim the rectangle edges
			side :krcko.rectangle			
			for side in sides:
				trimmed :List[krcko.rectangle] = self.trim_wall(side, room_and_hallways)
				t :krcko.rectangle
				for t in trimmed:
					trimmed_walls.append(t)
			

			#create wall entity
			trimmed_wall 	:krcko.rectangle					
			for trimmed_wall in trimmed_walls:
			
				#wall component
				# ascii
				# wall height
				# wall width
				wall_ascii 	:int
				wall_ascii	= self.game.get_ascii('WALL')

				wall_component = wall_component_fact(wall_ascii,trimmed_wall.height,trimmed_wall.width)
				
				#position component
				# y
				# x
				position_component = position_component_fact(trimmed_wall.y,trimmed_wall.x)
			
				#create entity	
				wall_eids.append(self.scene.add_entity(wall_component,position_component, ent_name = "wall"))
		

		return wall_eids
				
	#BSP stuff
	
	def split_rectangle(self,rect :krcko.rectangle) ->Tuple[krcko.rectangle,krcko.rectangle]:
		'''
		 Split a given rectangle into 2 random sized parts, horizontally 
		 or vertically. Minimum split ratio is 30:70.
		 params:
			rect
		'''


		a_rect :krcko.rectangle = krcko.rectangle(0,0,0,0)
		b_rect :krcko.rectangle = krcko.rectangle(0,0,0,0)
	
		min :int = 0
		max :int = 0
	
	
		mode :str
	
		if rect.height < self.avrg_rect.height:
			mode = "vertical"
	
		elif rect.width < self.avrg_rect.width:
			mode = "horizontal"
		else:
			mode = self.random.choice(["vertical","horizontal"]) 
	
	
		if mode == "horizontal":
			#min ratio is 30:70
			min	= int(((rect.height)/100)*30)
			max	= int(((rect.height)/100)*70)
			#split at y axis
			y_split :int = self.random.randint(min,max)
			
			#a_rectangle size
			#width stays the same from the original rectangle,
			# and the height becomes the split position
			a_rect.width  = rect.width
			a_rect.height = y_split
				
			#a_rectangle cords
			#equal to original rectangle cords
			a_rect.y = rect.y
			a_rect.x = rect.x
	
			#b_rectangle size
			#width stays the same from the original rectangle,
			# and the height becomes the originals width minus the split position
			b_rect.width  = rect.width
			b_rect.height = rect.height - y_split			
	
			#b_rectangle cords
			# x is the same as originals, and the y is equal to split y
			b_rect.y = rect.y + y_split
			b_rect.x = rect.x		
		
		else:
			#min ratio is 30:70
			min	= int(((rect.width)/100)*30)
			max	= int(((rect.width)/100)*70)
			#split at x axis
			x_split :int = self.random.randint(min,max)
			
			#a_rectangle size
			#height stays the same from the original rectangle,
			# and the width becomes the split position
			a_rect.height = rect.height
			a_rect.width  = x_split
	
			#a_rectangle cords
			#equal to original rectangle cords
			a_rect.y = rect.y
			a_rect.x = rect.x
		
			#b_rectangle size
			#height stays the same from the original rectangle,
			# and the width becomes the originals width minus the split position
			b_rect.height = rect.height
			b_rect.width  = rect.width - x_split
	
			#b_rectangle cords
			# y is the same as originals, and the x is equal to split x
			b_rect.y = rect.y
			b_rect.x = rect.x + x_split
			
		return (a_rect,b_rect)
	
	def bsp_generation(self,rect :krcko.rectangle) -> List[krcko.rectangle]:
		'''
		 Split the rectangle until all of the parts match the aproximate
		 room size.
		 params:
			rect
		'''

		#split the rectangle
		a_rect :krcko.rectangle
		b_rect :krcko.rectangle
	
		a_rect , b_rect = self.split_rectangle(rect)
	
	
		final_rects :List[krcko.rectangle] = [] 
	
		rec :krcko.rectangle
	
		#needs more splitting :)
		if a_rect.area - self.avrg_rect.area > 10:
			for rec in self.bsp_generation(a_rect):
				final_rects.append(rec)
		#it's ready :")
		else:
			final_rects.append(a_rect)
		
		#do the same stuff for the b_rectangle
		#needs more splitting :)
		if b_rect.area - self.avrg_rect.area > 10:
			for rec in self.bsp_generation(b_rect):
				final_rects.append(rec)
		#it's ready :")
		else:
			final_rects.append(b_rect)
		
	
		return final_rects
		
	#Room stuff
	
	def create_room_rectangle(self,start: krcko.point, goal: krcko.point) -> Tuple[int,krcko.rectangle]:
		'''
		 Create a rectangle somewhere between start and goal
		 params:
			start, goal
		'''
	
		#goal.x > start.x
	
		#too close
		if start.distance(goal) < 5:
			return (0,krcko.rectangle(0,0,0,0))	
	
		distance  :int
		room_rect :krcko.rectangle = krcko.rectangle(0,0,0,0)	
	
		dist_rect :krcko.rectangle = krcko.rectangle(abs(start.y-goal.y),abs(start.x-goal.x),0,0)
		
		#min: 10 % dist_rect, max 50% dist_rect
		min_rect :krcko.rectangle = krcko.rectangle(int((dist_rect.height/100)*10),int((dist_rect.width/100)*10),0,0)
		max_rect :krcko.rectangle = krcko.rectangle(int((dist_rect.height/100)*50),int((dist_rect.width/100)*50),0,0)
	
	
		room_rect.height = max(self.min_room_rect.height,self.random.randint(min_rect.height,max_rect.height))
		room_rect.width =  max(self.min_room_rect.width,self.random.randint(min_rect.width,max_rect.width))
		
		#same as start_point
		room_rect.y = start.y
		room_rect.x = start.x
		
		distance = int(room_rect.br.distance(goal))
			
		#too much to the right
		if room_rect.right > goal.x:
			room_rect.x -= room_rect.right - goal.x
		
		#too high
		if room_rect.bottom > goal.y:
			room_rect.y -= room_rect.bottom - goal.y
			
	
		
		return (distance,room_rect)
	
	
	def do_crop(self,crop_rect :krcko.rectangle, rect :krcko.rectangle) -> List[krcko.rectangle]:
		'''Actually does the cropping, returns list with cropped rectangles'''
		
		cropped_rects :List[krcko.rectangle] = []
	
		#crop_rect is somewhere inside rect	
		# that leaves max 4 possible cropped rectangles around crop_rect
		
		#check for first one, cropped top right and rect top left
		if crop_rect.tr.y > rect.tl.y:
			a_rect :krcko.rectangle =\
				 krcko.rectangle(crop_rect.tr.y - rect.tl.y, crop_rect.tr.x - rect.tl.x, rect.tl.y, rect.tl.x)
			cropped_rects.append(a_rect)
		
		#second one, cropped top left and rect bottom left
		if crop_rect.tl.x > rect.bl.x:
			b_rect :krcko.rectangle =\
				 krcko.rectangle(rect.bl.y - crop_rect.tl.y, crop_rect.tl.x - rect.bl.x, crop_rect.tl.y,rect.bl.x)
			cropped_rects.append(b_rect)
		
		#third one, cropped bottom left and rect bottom right
		if crop_rect.bl.y < rect.br.y:
			c_rect :krcko.rectangle =\
				 krcko.rectangle(rect.br.y - crop_rect.bl.y, rect.br.x - crop_rect.bl.x, crop_rect.bl.y, crop_rect.bl.x)
			cropped_rects.append(c_rect)
		
		#second one, cropped bottom right and rect top right
		if crop_rect.br.x < rect.tr.x:
			d_rect :krcko.rectangle =\
				 krcko.rectangle(crop_rect.br.y-rect.tr.y, rect.tr.x - crop_rect.br.x, rect.tr.y, crop_rect.br.x)
			cropped_rects.append(d_rect)
	
	
	
	
		return cropped_rects
	
	
	def crop_rectangle(self,rect :krcko.rectangle,*prev_rects :krcko.rectangle) ->List[krcko.rectangle]:
		'''Crop the rectangle so that it doesn't overlap with previous ones'''
	
		prev :krcko.rectangle = prev_rects[0]
		
		finished_rects :List[krcko.rectangle] = []
			
		#find the overlap area
		overlap :krcko.rectangle = krcko.rectangle(0,0,0,0)
	
		#height = higher bottom - lower top, if bigger than 0, they overlap	
		overlap.height = max(0,min(prev.bottom,rect.bottom)-max(prev.top,rect.top))
		#width = same thing but on the x axis
		overlap.width  = max(0,min(prev.right,rect.right)-max(prev.left,rect.left))
		
		#overlap cords
		overlap.y = max(prev.top,rect.top)
		overlap.x = max(prev.left,rect.left)
		
		#needs cropping
		if overlap.height > 0 and overlap.width > 0:
			cl : List[krcko.rectangle] = self.do_crop(overlap,rect)
			r  : krcko.rectangle
			for r in cl:
				finished_rects.append(r)
		#it doesn't overlap
		else:
			finished_rects.append(rect)
		
		#return crop_rectangle for the next prev_rect or
		# return the cropped rectangles list if there are no
		#  more prev_rects
		if(len(prev_rects) > 1):
			#crop_rectangle for every rectangle
			# in finished_rects
			actual_finished_rects :List[krcko.rectangle] = []#store returned rects
			frect :krcko.rectangle#finished rect
			cropped :krcko.rectangle#cropped rect
			cropped_list :List[krcko.rectangle]#cropped rects list
	
			for frect in finished_rects:
				cropped_list = self.crop_rectangle(frect, *prev_rects[1:])
				for cropped in cropped_list:
					actual_finished_rects.append(cropped)
	
			return actual_finished_rects			
		else:
			return finished_rects
		
	
		
	
	def generate_room(self,room_rect :krcko.rectangle) -> List[krcko.rectangle]:
		'''
		 Generates a room in a given rectangle.
		 params:
			room_rect
		'''
	
	
		#rectangle for the room is too small
		if self.mul(room_rect.y,room_rect.x) < self.mul(self.min_rect.y,self.min_rect.x):
			return []
		
		#list of rectangles that construct a room	
		room_rectangles :List[krcko.rectangle] = []
	
	
		
		#goal and start can't be on the same half
				
		start_point    :krcko.point = krcko.point(room_rect.y+int((room_rect.height/5)),\
				room_rect.x+int(room_rect.width/5))
		
		goal_point     :krcko.point = krcko.point(room_rect.bottom-int((room_rect.height/5)),\
				room_rect.x+int(room_rect.width/1.2))
		
	
		cur_rect :krcko.rectangle =  krcko.rectangle(0,0,start_point.x,start_point.y)
		distance :int       =  26	
	
		#generate rectangles until goal point is reached
		while distance  > 5: 
			
			#create rectangle somewhere between start and goal
			distance,cur_rect = self.create_room_rectangle(start_point,goal_point)
		
			
			if len(room_rectangles) > 0:
				#crop it
				cropped_rects :List[krcko.rectangle]
				cropped_rects = self.crop_rectangle(cur_rect,*room_rectangles)
				for crop_rect in cropped_rects:
					room_rectangles.append(crop_rect)
	
			else:
				room_rectangles.append(cur_rect)
	
			#place starting point somewhere in this new rectangle	
			start_point.y = cur_rect.y + int((cur_rect.height/100)*self.random.randint(30,60))
			start_point.x = cur_rect.x + int((cur_rect.width/100)*self.random.randint(30,60))	
	
	
		return room_rectangles
	
	
	
	
	#Hallway stuff
	
	def connect_points(self,start_point :krcko.point, goal_point :krcko.point,orientation :str, room_rect_edge :int) -> List[krcko.point]:
		'''Connects start and end points of the hallway'''
		
	
		#goal.y < start.y
		#goal.x < start.x
	
		#if on the same axis, theyre good to go :)
		if start_point.x == goal_point.x or\
			start_point.y == goal_point.y:
			return [start_point,goal_point]
	
		points :List[krcko.point] = [start_point]
	
		#connect them by creating 2 more points
		# at half the distance, 
		# or at the room_rect edge if the half goes over it 
		if orientation == "horizontal":
			#half or room_rect edge
			mid_point :int = min(room_rect_edge, int((start_point.x - goal_point.x)/2))

			#start side
			points.append(krcko.point(start_point.y, room_rect_edge))
			#goal  side
			points.append(krcko.point(goal_point.y,room_rect_edge))
		elif orientation == "vertical":
			#half or room_rect edge
			mid_point = min(room_rect_edge ,int((start_point.y - goal_point.y)/2))
			#start side
			points.append(krcko.point(room_rect_edge, start_point.x))
			#goal  side
			points.append(krcko.point(room_rect_edge, goal_point.x))


		points.append(goal_point)
	
		return points
	
	
	def create_hallway(self,a_room :List[krcko.rectangle], b_room :List[krcko.rectangle],direction :str, room_rect_edge :int) -> List[krcko.point]:
		'''Creates a hallway between two rooms'''
		
	
	
		index	   	  :int = 1 #loop stuff
		a_rect		  :krcko.rectangle #connecting rectangle from room a
		b_rect		  :krcko.rectangle #connecting rectangle from room b
		start_point	  :krcko.point     #start point of the hallway, in room b
		goal_point	  :krcko.point     #end point of the hallway, in room a
	
	
		if direction == "right":
			#connect the most right rectangle from the a_room
			# with the the most left rectangle from b_room
	
			#find the the most left rectangle in the second room
			cur_leftest_index :int = 0
		
			for index in range(1,len(b_room)):
				if b_room[index].left < b_room[cur_leftest_index].left:
					cur_leftest_index = index
	
			b_rect = b_room[cur_leftest_index]
			#x is the most left one in the room, y is somewhere random 
			# on the most left rectangle
			start_point = krcko.point(self.random.randint(b_rect.top,b_rect.bottom - 1),b_rect.left)	
		
			#find the most right rectangle in a_room
			cur_rightest_index :int = 0
		
			for index in range(1,len(a_room)):
				if a_room[index].right > a_room[cur_rightest_index].right:
					cur_rightest_index = index
	
			a_rect = a_room[cur_rightest_index]
			#x is the most right in the room, y is somewhere random 
			# on the most right rectangle
			goal_point = krcko.point(self.random.randint(a_rect.top,a_rect.bottom - 1),a_rect.right)	
	
	
			#connect start and goal
			return self.connect_points(start_point,goal_point,"horizontal", room_rect_edge) 
	
	
		elif direction == "bottom":
			#connect the lowest rectangle from the a_room
			# with the highest rectangle from b_room
	
			#find the highest rectangle in the second room
			cur_highest_index :int = 0
		
			for index in range(1,len(b_room)):
				if b_room[index].top < b_room[cur_highest_index].top:
					cur_highest_index = index
	
			b_rect = b_room[cur_highest_index]
			#y is highest in the room, x is somewhere random 
			# on the highest rectangle
			start_point = krcko.point(b_rect.top,self.random.randint(b_rect.left,b_rect.right - 1))	
		 
			#find the lowest rectangle in a_room
			cur_lowest_index :int = 0
		
			for index in range(1,len(a_room)):
				if a_room[index].bottom > a_room[cur_lowest_index].bottom:
					cur_lowest_index = index
	
			a_rect = a_room[cur_lowest_index]
			#y is lowest in the room , x is somewhere random 
			# on the lowest rectangle
			goal_point = krcko.point(a_rect.bottom ,self.random.randint(a_rect.left,a_rect.right - 1))	
		
			#connect start and goal
			return self.connect_points(start_point,goal_point,"vertical", room_rect_edge) 
	
	 
			
		return []
	
	
	def create_hallway_rects(self, hallways :List[List[krcko.point]]) -> List[List[krcko.rectangle]]:
		''' Converts hallway points to rectangles '''
		
		
		hallways_as_rects :List[List[krcko.rectangle]] = []

	
		for hallway in hallways:
			
			hallway_rects :List[krcko.rectangle] = []

			i :int=0
			j :int=1

			while j < len(hallway):
				rect: krcko.rectangle = krcko.rectangle(0,0,0,0)

				rect.x = min(hallway[j].x, hallway[i].x)
				rect.y = min(hallway[j].y, hallway[i].y)

				rect.height = max(1,abs(hallway[i].y - hallway[j].y) + (1 if i==1 else 0))#middle one needs to be a bit longer :/
				rect.width  = max(1,abs(hallway[i].x - hallway[j].x) + (1 if i==1 else 0))# same

				j+= 1
				i+= 1
				
				hallway_rects.append(rect)


			if len(hallway_rects) == 0:
				continue

			hallways_as_rects.append(hallway_rects)	


		return hallways_as_rects



	def add_to_hallway_table(self, room_id :int, hallway_id :int) -> None:
		''' '''
		if room_id in self.m_hallway_table.keys():
			self.m_hallway_table[room_id].append(hallway_id)
		else:
			self.m_hallway_table[room_id] = [hallway_id]
		


	def generate_hallways(self,room_rects :List[krcko.rectangle], rooms :List[List[krcko.rectangle]]) -> List[List[krcko.rectangle]]:
		'''Generate hallways between rooms
		 params:
			room_rects - rectangles containing rooms, rooms
		'''
	
		#room rectangles are generated recursively, first one being top left,
		# and last one bottom right 
		#  go trough room rectangles starting from top left (first one) and search
		#   for it's right and bottom neighbour, and create a hallway between them.
		#    that is all :) 
	
	
		#room for room_rect[n] is at rooms[n]
		
		#hallways per room index table
		self.m_hallway_table :Dict[int, List[int]] = {} #{ room_id, hallways_ids}


		hallways :List[List[krcko.point]] = []
		i :int 
		for i in range(0,len(room_rects)):
			#find it's right and bottom neighbour
			j :int
			for j in range(i,len(room_rects)):
				#if right/bottom neighbour 
				#create hallway
				#right
				if room_rects[i].tr.y == room_rects[j].tl.y and\
					room_rects[i].tr.x == room_rects[j].tl.x:
					hallways.append(self.create_hallway(rooms[i],rooms[j],"right", room_rects[i].right - 1))

					self.add_to_hallway_table(i, len(hallways) - 1)
					self.add_to_hallway_table(j, len(hallways) - 1)

				#bottom
				if room_rects[i].bl.y == room_rects[j].tl.y and\
					room_rects[i].bl.x == room_rects[j].tl.x:
					hallways.append(self.create_hallway(rooms[i],rooms[j],"bottom", room_rects[i].bottom - 1))
	
					self.add_to_hallway_table(i, len(hallways) - 1)
					self.add_to_hallway_table(j, len(hallways) - 1)


	
		return self.create_hallway_rects(hallways)
				
	

sys_instance = DungeonGenerator()
