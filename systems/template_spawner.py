class TemplateSpawner(krcko.System):
	'''Spawn entities from templates somewhere in rooms'''


	from configparser import ConfigParser
	import random
	import re
	import copy

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

					tml_component 	= [comp for comp in self.templates[template_name] if type(comp).__name__ == "template"][0]
					#jackpot
					if self.dice_roll(int(tml_component.rarity)):
						#spawn the entity 
						tmp_eid = self.create_entity(room_ent, self.templates[template_name], template_name)
						ent = self.scene.get_entity(tmp_eid)
						
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
			avaliable at a current depth
		'''

		self.avaliable_templates = {}

		#go trough templates
		for template_name in self.templates.keys():
			#check depth availability
			tml_component 	= [comp for comp in self.templates[template_name] if type(comp).__name__ == "template"][0]
			curr_depth :int = self.player_ent['player'].depth
			# needs to be deeper
			if int(tml_component.min_depth) > curr_depth:
				continue

			# too deep, if 0 it's good  for all depths
			if int(tml_component.max_depth) != 0 and\
				int(tml_component.max_depth) < curr_depth:
				continue

			#good to go :)
			self.avaliable_templates[template_name] = self.templates[template_name]
	

	def load_templates(self, templates_dir :str) -> None:
		''' Loads all templates from templates dir'''
		
		#go trough every file in template dir
		for file_path in krcko.gen_files(templates_dir):
			#load template from file
			tml_components = krcko.load_template(file_path)
			if tml_components == []:
				continue


			#templates must have template component
			tmls = [comp for comp in tml_components if type(comp).__name__ == "template"]
			if len(tmls) == 0:
				logging.error("templates must have template component: " + file_path)
				continue

			tml_component = tmls[0]
			tml_name :str = tml_component.name 

			#template with that name already loaded, continue
			if tml_name in self.templates.keys():
				continue
	
			#add loaded template to templates
			self.templates[tml_name] = tml_components




	def create_entity(self, room_ent, tmp, tmp_name :str) -> int:
		'''Creates template entity in a room'''



		#copy
		components = []
		for t in tmp:
			#copy component
			component_factory 	= t.__class__
			component_values	= list(t._asdict().values())
			#
			components.append(component_factory(*self.copy.deepcopy(component_values)))
			#random values, tuple with min, max
			for index in range(0, len(components[-1])):
				_field = components[-1][index]
				if type(_field) is tuple:
					_min, _max = _field
					components[-1][index] = self.random.randint(int(_min), int(_max))
		
		#create base entity
		eid = self.scene.add_entity(*components, ent_name = tmp_name)
		ent = self.scene.get_entity(eid)

		#no position or drawable component given,
		#	skip
		if "position" not in ent.keys() or\
			"drawable" not in ent.keys(): 
			return eid


		#get ascii from table
		ent['drawable'].ascii = self.game.get_ascii(ent['drawable'].ascii_id)


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
			for d_ent, _ in self.scene.gen_entities("drawable"):
				if "position" not in d_ent.keys():
					continue
				
				me	:krcko.point	= krcko.point(new_y, new_x)
				if me.distance(krcko.point(d_ent['position'].y, d_ent['position'].x)) < self.min_spawn_distance:
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
		#	assign position values
		ent['position'].y = new_y
		ent['position'].x = new_x

		return eid	





sys_instance = TemplateSpawner()
