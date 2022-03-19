class Template_Items(krcko.System):
	'''Initialize items from templates to inventory'''	


	import random

	def setup(self):	
		
	
		for ent, eid in self.scene.gen_entities("template_items"):
			#entity with template items must have inventory component
			if not self.scene.entity_has_component(eid, "inventory"):
				#
				self.scene.remove_component(eid, "template_items")
				continue		
		
			#get the component		
			tmp_items	=	ent["template_items"]


			#default
			self.parse(eid, tmp_items.default, self.init_item)
			#weapons
			self.parse(eid, tmp_items.weapons, self.init_weapon)
					



	def update(self):
		pass	

	def cleanup(self):
		pass



	def parse(self, eid :int, input_string :str, init_call ) -> None:
		'''parses items string, calls given init '''
		

		#nothing to do
		if input_string == "":
			return 

		#template_file, template_file : chance
		
		for token in input_string.split(','):
			#template_name : chance
			if ":" in token:
				chance :int
				template_name :str
				#
				try:
					template_name, _chance = token.split(':')		
					chance = int(_chance)
				except Exception as e:
					logging.error("Wrong template_item syntax :" + token + ". " + str(e))
					continue
				
				#good to go,
				# roll them
				if krcko.dice_roll(chance):
					init_call(eid, template_name) 					


			#template_name
			else:
				init_call(eid, token)



	
	def init_item(self, eid :int, item_template :str) -> int:
		'''create an item from template file, and put it in ents inventory.
			ent MUST have inventory and template_items components
			
			returns items eid, or -1 if it fails'''
		

		#ent should have inventory and template_items components
		if not self.scene.entity_has_component(eid, "inventory") or\
			not self.scene.entity_has_component(eid, "template_items"):
			#
			logging.error("failed to get entity")
			return -1  


		#get ent
		ent = self.scene.get_entity(eid)
		#get inventory
		inventory = ent['inventory']
		

		#load up template components 
		components :List[Any] = krcko.load_template(defs.ITM_DIR_PATH + item_template)


		#
		for c in components:
			#random values, tuple with min, max
			for index in range(0,len(c)):
				_field = c[index]
				if type(_field) is tuple:
					_min, _max = _field
					c[index] = self.random.randint(int(_min), int(_max))


		#create entity
		item_eid :int = self.scene.add_entity(*components, ent_name = "ITEM_TEMPLATE: " + item_template)			
		#remove drawable component 
		self.scene.remove_component(item_eid, "drawable")

		
		#put in inventory
		inventory.items.append(item_eid)


		#
		return item_eid

		

	def init_weapon(self, eid :int, item_template :str) -> None:
		'''equip a given weapon to a given carrier'''
 

		#init weapon	
		weapon_eid :int = self.init_item(eid, item_template)
	

		#weapon must have weapon component
		if not self.scene.entity_has_component(weapon_eid, "weapon"):
			logging.error("failed to get weapon ent.")
			return


		#get carrier inventory
		if not self.scene.entity_has_component(eid, "inventory"):
			logging.error("failed ot get carrier ent.")
			return

		inventory = self.scene.get_entity(eid)["inventory"]
	

		#weapon must already be in inventory
		if weapon_eid not in inventory.items:
			logging.error("weapon missing from inventory")
			return	

		#equip weapon
		# if there are already 2 weapons in hands, pop one of them
		if len(inventory.hands) >= 2:
			inventory.hands.pop()

		#equip in hands
		inventory.hands.append(weapon_eid)






sys_instance = Template_Items()
