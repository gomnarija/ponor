class NPCSpawner(krcko.System):
	'''Spawns npcs from npc templates '''


	from configparser import ConfigParser
	import random

	#STELOVANJE
	
	#minimum distance between npc's and other
	# drawable objects
	min_spawn_distance :int		=	3
	#base rect
	base_rect :krcko.rectangle	=	krcko.rectangle(20,20,0,0)
	#number of npc's 
	# per base_rect
	npc_rect_ratio :float		=	0.85	


	def setup(self):
		#get player entity
		self.player_ent = self.scene.get_entity_from_name("player")
			
		#load npc templates
		self.load_npc_classes()
	
		#get avaliable ones
		self.filter_npc_classes()	

		#spawn npc's in rooms 
		self.spawn_npcs()

	def update(self):
		pass

	def cleanup(self):
		pass


	def dice_roll(self, rarity :int) -> bool:
		'''roll the dice'''
		roll : int = self.random.randint(0,100)
		return roll <= rarity


	def spawn_npcs(self) -> None:
		'''Go trough every room and spawn npcs in it '''

		#no avalible npc's 
		if len(self.avaliable_npc_classes.keys()) == 0:
			logging.warning("no avaliable npc classes")
			return

		
		#go trough rooms
		room_eid	:int
		for room_ent in self.scene.gen_entities("room"):
			if "room" not in room_ent.keys():
				logging.error("failed to get room entity : " + str(room_eid))
				continue

		
			#up for creation in this room
			npcs	=	[]

			#get room's room_rect
			room_rect :krcko.rectangle = room_ent['room'].room_rect

			#number of npcs in this room	
				
				# room_rect to base rect ratio
			rect_ratio :float	=	(room_rect.height * room_rect.width) / (self.base_rect.height * self.base_rect.width)
 
			number_of_npcs :int	=	int(self.npc_rect_ratio * rect_ratio)


			#go trough all avaliable npcs
			# until number_of_npcs is reached
	
			# or give up trying :/
			tries	:int =	6969

			while number_of_npcs > 0:
				#go trough all avaliable npcs
				for npc_name in self.avaliable_npc_classes.keys():
					
					#give up
					tries-= 1
					if tries < 0:
						logging.error("out of tries")
						return
					#we're done
					if number_of_npcs < 0:
						break

					npc = self.avaliable_npc_classes[npc_name]
					#jackpot
					if self.dice_roll(int(npc.rarity)):
						#spawn the npc
						npc_eid = self.create_npc(room_ent, npc)
						#something's wrong
						if npc_eid == -1:
							logging.error("spawning npc failed : " + npc.name)
							continue
						else:
							#all good
							number_of_npcs -= 1
							continue


					else:
						# not so lucky
						continue




	def filter_npc_classes(self) -> None:
		''' Goes trough self.npc_classes and checks which ones are
			avaliable
		'''

		self.avaliable_npc_classes = {}

		#go trough npc classes
		for npc_class in self.npc_classes.keys():
			#check depth availability
			npc 		= self.npc_classes[npc_class]
			curr_depth :int = self.player_ent['player'].depth
			# needs to be deeper
			if int(npc.min_depth) > curr_depth:
				continue

			# too deep, if 0
			if int(npc.max_depth) != 0 and\
				int(npc.max_depth) < curr_depth:
				continue

			#good to go :)
			self.avaliable_npc_classes[npc.name] = npc
	

	def load_npc_classes(self) -> None:
		''' Loads all npc templates from templates dir '''
		
		self.npc_classes = {} # class_name : recordclass
		
		#go trough every file in npc template dir
		for npc_file_path in krcko.gen_files(defs.NPC_DIR_PATH):
			#load template from file
			npc, fact = self.load_template(npc_file_path)
			#default value, something's wrong
			if npc.name == "NPC":
				logging.error("failed to load npc template")
				continue

			#template with that name already loaded, continue
			if npc.name in self.npc_classes.keys():
				continue
	
			#add loaded npc template to npc_classes
			self.npc_classes[npc.name] = npc



	def load_template(self, path :str): 
		'''Load npc template into a recordclass
			!!!all values are of type str!!!'''

		#must have default keys of the 
		# npc template		
		cp	=	self.ConfigParser(allow_no_value=True)
		cp['NPC'] =\
		{
			'name'			:	"NPC",		# npc class name
			'ascii'			:	"65",		# ascii code
			'min_depth'		:	"1",		# minimum depth for this npc to spawn
			'max_depth'		:	"0",		# maximum depth for this npc to spawn
			'min_health'		:	"100",		# minimum health
			'max_health'		:	"100",		# maximum health
			'components'		:	"hit.json",	# list of pattern files, located in PAT_DIR_PATH, separated with ','
			'optional_components'	:	 ""		# pattern_file : chance_to_have_this_component_in_%, separated with ','
		}
		#read template file
		try:
			cp.read(path)
		except:
			logging.error("failed to load npc template from : " + defs.NPC_DIR_PATH + path)
			return None

		
		npc	=	recordclass(cp['NPC'].name, cp['NPC'].keys())

		return (npc(*cp['NPC'].values()), npc)
		




	def create_base(self, npc) -> int:
		'''NPC base:
			npc
			position
			health
			drawable

		returns eid
		'''

		#load base components
		npc_component, fact 		= krcko.load_component(defs.PAT_DIR_PATH + "npc.json")
		position_component, fact 	= krcko.load_component(defs.PAT_DIR_PATH + "position.json")
		health_component, fact 		= krcko.load_component(defs.PAT_DIR_PATH + "health.json")
		drawable_component, fact 	= krcko.load_component(defs.PAT_DIR_PATH + "drawable.json")
	

		#assign template values to base components	
		npc_component.class_name	=	npc.name
		drawable_component.ascii	=	int(npc.ascii)	
		health_component.max_health	=	self.random.randint(int(npc.min_health), int(npc.max_health))
		health_component.amount		=	health_component.max_health

		#create npc entity
		return self.scene.add_entity(npc_component,position_component,health_component,drawable_component, ent_name = npc.name)
		


	def create_npc(self, room_ent, npc) -> int:
		'''Creates NPC entity in a room'''


		#create base entity
		npc_eid = self.create_base(npc)
		npc_ent = self.scene.get_entity(npc_eid)
		if "npc" not in npc_ent.keys():
			logging.error("failed to get npc entity : " + str(npc_eid))


		#Can't be too close to other drawables
		tries	:int	=	69
		new_y	:int
		new_x	:int	
		while True:

			#place npc somewhere random in the room
			rect :krcko.rectangle = room_ent['floor'].floor_tiles[self.random.randint(0,len(room_ent['floor'].floor_tiles) - 1)]
			#somewhere on the rect
			new_y		=	rect.y + self.random.randint(0,rect.height-1) 	
			new_x		=	rect.x + self.random.randint(0,rect.width-1)	

			too_close :bool	= False
			#check how close it is to other drawables
			for ent in self.scene.gen_entities("drawable"):
				if "position" not in ent:
					continue
				
				me	:krcko.point	= krcko.point(new_y, new_x)
				if me.distance(krcko.point(ent['position'].y, ent['position'].x)) < self.min_spawn_distance:
					too_close = True
					break


			#good to go
			if not too_close:
				break			

			#give up after a while, delete entity
			tries -= 1
			if tries < 0:
				self.scene.del_entity(npc_eid)
				return -1
			

		#good to go
		# assign position values
		npc_ent['position'].y = new_y
		npc_ent['position'].x = new_x



		
		#add components
		for component_name in npc.components.split(','):
			#no components given
			if component_name == "":
				continue

			#load
			component, fact = krcko.load_component(defs.PAT_DIR_PATH + component_name)
			#something's wrong
			if component is None:
				continue
			#all good
			self.scene.add_component(npc_eid, component)

	

		
	
		#optional components
		for optional in npc.optional_components.split(','):
			#no optional components given
			if optional == "":
				continue

			#optiona_component_name : rarity
			optional_split = optional.split(':')
			if len(optional_split) != 2:		
				logging.error("wrong optional component syntax ")
				continue	
			#
			rarity :int 		= int(optional_split[1])
			component_name :str	= optional_split[0]
			#jackpot
			if self.dice_roll(rarity):
				#add component
				component, fact = krcko.load_component(defs.PAT_DIR_PATH + component_name)
				#something's wrong	
				if component is None:
					continue
				self.scene.add_component(npc_eid, component)

		return npc_eid	





sys_instance = NPCSpawner()
