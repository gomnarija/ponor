class NPCSpawner(krcko.System):
	'''Spawn entities from templates somewhere in rooms'''


	from configparser import ConfigParser
	import random

	#STELOVANJE
	
	#minimum distance between spawned entities and other
	# drawable objects
	min_spawn_distance :int		=	3
	#base rect
	base_rect :krcko.rectangle	=	krcko.rectangle(10,10,0,0)
	#number of spawned entities 
	# per base_rect
	template_rect_ratio :float	=	0.5	


	#loaded templates
	templates			=	{}


	def setup(self):
		#get player entity
		self.player_ent = self.scene.get_entity_from_name("player")
			
		#load npc templates
		self.load_templates(defs.NPC_DIR_PATH)
		
		#load item templates
		self.load_templates(defs.ITM_DIR_PATH)
	
		#get avaliable ones
		self.filter_templates()	

		#spawn templates in rooms 
		self.spawn_templates()

	def update(self):
		pass

	def cleanup(self):
		pass


	def dice_roll(self, rarity :int) -> bool:
		'''roll the dice'''
		roll : int = self.random.randint(0,100)
		return roll <= rarity


	def spawn_templates(self) -> None:
		'''Go trough every room and spawn templates in it '''

		#no avalible templates 
		if len(self.avaliable_templates.keys()) == 0:
			logging.warning("no avaliable templates")
			return

		
		#go trough rooms
		room_eid	:int
		for room_ent, _ in self.scene.gen_entities("room"):
			if "room" not in room_ent.keys():
				logging.error("failed to get room entity : " + str(room_eid))
				continue

		
			#up for creation in this room
			to_spawn	=	[]

			#get room's room_rect
			room_rect :krcko.rectangle = room_ent['room'].room_rect

			#number of templates in this room	
				# room_rect to base rect ratio
			rect_ratio :float		=	(room_rect.height * room_rect.width) / (self.base_rect.height * self.base_rect.width)
			number_of_templates :int	=	int(self.template_rect_ratio * rect_ratio)


			#go trough all avaliable templates
			# until number_of_templates is reached
	
			# or give up trying :/
			tries	:int =	6969

			while number_of_templates > 0:
				#go trough all avaliable templates 
				for template_name in self.avaliable_templates.keys():
					
					#give up
					tries-= 1
					if tries < 0:
						logging.error("out of tries")
						return
					#we're done
					if number_of_templates < 0:
						break

					tmp = self.avaliable_templates[template_name]
					#jackpot
					if self.dice_roll(int(tmp.rarity)):
						#spawn the entity 
						tmp_eid = self.create_entity(room_ent, tmp)
						#something's wrong
						if tmp_eid == -1:
							logging.error("spawning failed : " + tmp.name)
							continue
						else:
							#all good
							number_of_templates -= 1
							continue


					else:
						# not so lucky
						continue




	def filter_templates(self) -> None:
		''' Goes trough self.templates and checks which ones are
			avaliable
		'''

		self.avaliable_templates = {}

		#go trough templates
		for template in self.templates.keys():
			#check depth availability
			tmp 		= self.templates[template]
			curr_depth :int = self.player_ent['player'].depth
			# needs to be deeper
			if int(tmp.min_depth) > curr_depth:
				continue

			# too deep, if 0
			if int(tmp.max_depth) != 0 and\
				int(tmp.max_depth) < curr_depth:
				continue

			#good to go :)
			self.avaliable_templates[tmp.name] = tmp
	

	def load_templates(self, templates_dir :str) -> None:
		''' Loads all templates from templates dir '''
		
		#go trough every file in template dir
		for file_path in krcko.gen_files(templates_dir):
			#load template from file
			tmp, fact = self.load_template(file_path)
			#default value, something's wrong
			if tmp.name == "TEMPLATE":
				logging.error("failed to load template")
				continue

			#template with that name already loaded, continue
			if tmp.name in self.templates.keys():
				continue
	
			#add loaded template to templates
			self.templates[tmp.name] = tmp



	def load_template(self, path :str): 
		'''Load template into a recordclass
			!!!all values are of type str!!!'''

		#default
		cp	=	self.ConfigParser(allow_no_value=True)
		cp['TEMPLATE'] =\
		{
			'name'			:	"TEMPLATE",	# 
			'type'			:	"TEMPLATE",	#
			'ascii'			:	"65",		# ascii code
			'min_depth'		:	"1",		# minimum depth for this to spawn
			'max_depth'		:	"0",		# maximum depth for this to spawn
			'components'		:	"",		# pattern_file_name : chance to have, separated with ','
			'rarity'		:	"70"		# chance to spawn
		}
		#read template file
		try:
			cp.read(path)
		except:
			logging.error("failed to load template from : " + path)
			return None

		
		tmp	=	recordclass(cp['TEMPLATE']['type'], cp['TEMPLATE'].keys())
		

		return (tmp(*cp['TEMPLATE'].values()), tmp)
		


	def create_entity(self, room_ent, tmp) -> int:
		'''Creates template entity in a room'''




		#create base entity
		eid = self.scene.add_entity(tmp, ent_name = tmp.name)
		ent = self.scene.get_entity(eid)

	
		#load components
		for optional in tmp.components.split(','):
			#no optional components given
			if optional == "":
				continue

			#optiona_component_name : rarity
			optional_split = optional.split(':')
			if len(optional_split) != 2:		
				logging.error("wrong optional component syntax ")
				continue	
			#
			rarity :int 		= int(optional_split[1].strip())
			component_name :str	= optional_split[0].strip()
			#jackpot
			if self.dice_roll(rarity):
				#add component
				component, fact = krcko.load_component(defs.PAT_DIR_PATH + component_name)
				#something's wrong	
				if component is None:
					continue
				self.scene.add_component(eid, component)



		#no position component given
		if "position" not in ent.keys(): 
			return eid


		#Can't be too close to other drawables
		tries	:int	=	69
		new_y	:int
		new_x	:int	
		while True:

			#place somewhere random in the room
			rect :krcko.rectangle = room_ent['floor'].floor_tiles[self.random.randint(0,len(room_ent['floor'].floor_tiles) - 1)]
			#somewhere on the rect
			new_y		=	rect.y + self.random.randint(0,rect.height-1) 	
			new_x		=	rect.x + self.random.randint(0,rect.width-1)	

			too_close :bool	= False
			#check how close it is to other drawables
			for ent, _ in self.scene.gen_entities("drawable"):
				if "position" not in ent.keys():
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
				self.scene.del_entity(eid)
				return -1
			

		#good to go
		# assign position values
		ent['position'].y = new_y
		ent['position'].x = new_x

		return eid	





sys_instance = NPCSpawner()
