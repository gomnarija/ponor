import json
from recordclass import recordclass
import os
import sys
import traceback
import inspect
from typing import Any,Dict,Iterator,List,Generator
import logging

import krcko.core as krcko
import definitions as defs

SYSTEMS_PATH = defs.ROOT_DIR_PATH + "/systems/"



class Scene:
	
	'''
	 Scene object holds entities/components/systems.
	
	 Scene is responsible for:
	 -creating/destroying entities.
	 -adding components to entities.
	 -executing systems.	

	'''


	def __init__(self,name :str):
		self.name :str	    		 	 = name #scene name
		self.m_entities :Dict[int,Dict[str,Any]] = {} #dict for storing entities, entity_id : {component_type : {component},  ... } 
		self.m_groups	:Dict[int,set[int]]	 = {} #dict for storing entity groups, group_id : set[entity_id,entity_id...]
		self.m_components :Dict[str,set]  	 = {} #dict for keeping track of components, component_type : (eid,eid,eid)
		self.m_entity_names :Dict[str,int]	 = {} #dict for keeping track of entity names, entity_name : eid 
		self.m_same_ent_names :Dict[str, int]    = {} #dict keeping track of indexing names
		self.m_group_names :Dict[str,int]	 = {} #dict for keeping track of group names, group_name : gid 
		self.m_purgatory :set   		 = set() #set for keeping track of entities that are waiting to be deleted
		self.m_next_eid :int 			 = 0 #next avaliable entity_id
		self.m_next_gid :int 			 = 0 #next avaliable group_id
		self.m_systems :Dict[str,krcko.System]	 = {} #dict for storing systems, {system_type : system }
		self.game				 = None #parent game object
	

	def add_game(self, game) -> None:
		'''add game'''
		self.game = game

	def add_entities_to_group(self, gid: int, *eids: int) -> None:
		'''Add entities to group 
		 params:
			*eids, gid
		'''
		if not self.has_group(gid):
			logging.error("Scene doesn't have group with id : " + str(gid))
			return
		
		#add eids to group
		for eid in eids:
			if not self.has_entity(eid):
				logging.error("Scene doesn't have entity with id : " + str(eid))
				return
			self.m_groups[gid].add(eid)
			

	def add_group(self, *eids :int, group_name :str = "group") -> int:
		'''Create group, add entities
		 params:
			*eids
		   optional:
			group_name
		'''
		#create new group
		#and add entites to it
		self.m_groups[self.m_next_gid] = set()
		self.add_entities_to_group(self.m_next_gid,*eids)

		#group with that name already exists, add index at
		# the end of the name
		index :int = 1
		o_group_name = group_name
		while group_name in self.m_group_names:
			group_name = o_group_name + " " + str(index)
			index += 1
		
		self.m_group_names[group_name] = self.m_next_gid


		self.m_next_gid += 1
		return self.m_next_gid-1 



		  
	def add_entity(self, *comps, ent_name :str ="entity") -> int:
		'''
		  Add entity to Scene
	 
		  params:
	   		comps : components 
                    optional:
	   		ent_name : name of the newly created entity

		'''
		#create new entity
		#and add components to it
		self.m_entities[self.m_next_eid] = {}
		self.add_component(self.m_next_eid,*comps)


		#entity with that name already exists, add index at
		# the end of the name
		if ent_name in self.m_same_ent_names.keys():
			self.m_same_ent_names[ent_name] += 1
			ent_name += " " + str(self.m_same_ent_names[ent_name])
		else:
			self.m_same_ent_names[ent_name] = 0

		
		self.m_entity_names[ent_name] = self.m_next_eid



		self.m_next_eid += 1
		return self.m_next_eid-1 

	def add_component(self,eid: int, *comps) -> None:
		'''
		 Add components to entity
	
		 params:
	 		eid : entity id
			*comps : components 
		'''
	
		if not self.has_entity(eid):
			logging.error("Couldn't add component to : " + str(eid))
			return
		
		for comp in comps:
			#comp_type will be set to component value from pattern file
			comp_type = type(comp).__name__
			self.m_entities[eid][comp_type] = comp
			if comp_type not in self.m_components:#no components of this type previosly
				self.m_components[comp_type] = set()
			
			self.m_components[comp_type].add(eid)

	def remove_component(self,eid: int, comp_type: str) -> None:
		'''
		Remove component from entity
		
		params:
			eif: entity id
			comp_type : component type
		'''

		if not self.entity_has_component(eid,comp_type):
			logging.error("Couldn't remove component: " + comp_type + " from " + str(eid))
			return 

		del self.m_entities[eid][comp_type]
		self.m_components[comp_type].remove(eid)

	
	
	 
	def get_component(self,eid: int,comp_type: str) -> recordclass:
		'''
		Get component from entity
		
		params:
			eid : entity id
			comp_type : component type
		'''
	
		if not self.entity_has_component(eid,comp_type):
			logging.error("Couldn't get component: " + comp_type + " from " + str(eid))
			return 
		
		return self.m_entities[eid][comp_type]
		

	def gen_group(self,gid :int) -> Generator[int,None,None]:
		'''Generator for group members
		 params:
			gid
		'''
		if not self.has_group(gid):
			logging.error("Scene doesn't have group with id : " + str(gid))
			raise StopIteration

		for eid in self.m_groups[gid]:
			yield eid

	def gen_entities(self,comp_type: str) -> Generator[Dict,None,None]:
		'''
		Generator for entities that have component type.
	 
		params:
			comp_type: Component type
	 
		'''

		if not comp_type in self.m_components.keys():
			#logging.error("No components of type: " + comp_type)
			raise StopIteration
		
		for eid in self.m_components[comp_type]:
			yield self.m_entities[eid]


	def gen_components(self,comp_type: str) -> Generator[recordclass,None,None]:
		'''
		Generator for components of given type.
		
		params: 
			comp_type : Component type
	
		'''

		if not comp_type in self.m_components.keys():
			logging.error("No components of type: " + comp_type)
			raise StopIteration
	
		for ent in self.m_components[comp_type]:
			yield self.m_entities[ent][comp_type]


	def get_eid_from_name(self,ent_name : str) -> int:

		'''
		Get entity id from name
	
		params:
	  		ent_name : entity name
		'''		

		if ent_name in self.m_entity_names:
			return self.m_entity_names[ent_name]
		else:
			logging.warning("No entity with name: " + ent_name)
			return -1


	def get_entity_name(self, eid :int) -> str:
		
		'''
			Get entity name from eid
		'''
		
		if eid in self.m_entity_names.values():
			return list(self.m_entity_names.keys())[list(self.m_entity_names.values()).index(eid)]
		else:
			logging.warning("No entity name for eid : " + str(eid))
			return ""
			


	def get_entity_from_name(self,ent_name : str) -> dict:

		'''
		Get entity  from name
	
		params:
 			ent_name : entity name
		'''		

		if ent_name in self.m_entity_names:
			return self.get_entity(self.m_entity_names[ent_name])
		else:
			logging.error("No entity with name: " + ent_name)
			return dict()

	def get_entity(self,eid : int) -> dict:
		'''
		Get entity  from entity id
	
	 	 params:
	 		eid : entity id
		'''	
	
		if not self.has_entity(eid):
			logging.error("Couldn't get entity: " + str(eid))
			return dict()	

		return self.m_entities[eid]
	
	def get_group(self, gid :int) -> str:
		''' Get group'''
		
		if not self.has_group(gid):
			logging.warning("No group with group id" + str(gid))
			return {}

		return self.m_groups[gid]


	def get_group_from_name(self, group_name :str) -> dict:
		'''Get group'''
		
		if not group_name in self.m_group_names.keys():
			logging.warning("No group with name :" + group_name)
			return {}

		return self.get_group(self.m_group_names[group_name]) 


	def has_entity(self, eid: int) -> bool:

		'''
		 Check if scene has entity
	
		 params:
		 	eid: entity id
		'''
		return eid in self.m_entities.keys()

	
	def has_group(self, gid: int) -> bool:
		'''Check if scene has group'''
		return gid in self.m_groups.keys()

		
	def entity_has_component(self, eid: int, comp_type: str) -> bool:
		'''
		Check if entity has component
	
		params:
			eid: entity id
	 		comp_type: component type
		'''	
	
		return self.has_entity(eid) and comp_type in self.m_entities[eid].keys()
	

		
	def del_entity(self,eid :int) -> None:
		'''
		 Place entity up for deletion
	
		params:
			eid: entity id
		'''	

		if not self.has_entity(eid):
			logging.error("No entity with eid: " + str(eid))
			return 

		self.m_purgatory.add(eid)

	def purge(self) -> None:
		'''
		Purge from purgatory
		'''	
		
		for eid in self.m_purgatory:
			for comp_type in self.m_entities[eid]:
				self.m_components[comp_type].remove(eid)	

			del self.m_entities[eid]
		
		self.m_purgatory.clear()


	def add_system(self,system :krcko.System) -> None:
		'''	
		 Add system to the scnene
		 params:
			system:
		'''
		self.m_systems[type(system).__name__] = system
		self.m_systems[type(system).__name__].add_scene(self)
	

	def load_systems(self,path :str =None) -> None:
		'''
		 Load systems from path, if path isn't given, load from default systems path
		 params:
			path
		'''
		
		if path is None:
			path = SYSTEMS_PATH

		#go trough all files and dirs in path	
		for sys_file_path in krcko.gen_files(path):
			if ".py" not in sys_file_path:#ignore non python files
				continue
			try:
				with open(sys_file_path,"r") as sys_file:
					ret : Dict[str,krcko.System] = {}
					try:
						krcko.execute(sys_file.read(),globals=globals(),locals=ret)#exec system class
					except Exception as e:
						logging.error("Failed to execute system: " + sys_file_path + " : "+ str(e))
						return			

					if 'sys_instance' not in ret:
						logging.error("System file doesn't have sys_instance")
						pass
					else:
						self.add_system(ret['sys_instance'])
			except IOError as e:
				logging.error(str(e))
				pass
	
	
	def load_entity(self,path :str) -> None:
		'''
		 Load entity components from dir.
		 
		 params:
			path - path to dir with components 
		'''

		comps : List = []

		#go trough all files and dirs in path	
		for comp_file_path in krcko.gen_files(path):
			if ".json" not in comp_file_path:#ignore non json files
				continue
			ret = krcko.load_component(comp_file_path)
			if ret is None:
				logging.error("failed to load component")
				return
			comp,fact = ret
			if not comp is None:
				comps.append(comp)

		#dir name 		
		ent_name = os.path.basename(path)
		#create new entity
		if len(comps) > 0:
			eid = self.add_entity(*comps,ent_name = ent_name)
		
		


	def setup(self) -> None:
		'''	
		Systems setup 
		'''
		try:
			for sys_type in self.m_systems.keys():
				self.m_systems[sys_type].setup()
		except Exception as e:
			cl, exc, tb = sys.exc_info()
			line_number = traceback.extract_tb(tb)[-1][1]
			logging.error(sys_type + ": startup failed at line " + str(line_number) + ": " +str(e))


	def update(self) -> None:
		'''	
		Systems update
		'''
		sys_type : str

		try:
			for sys_type in self.m_systems.keys():
				self.m_systems[sys_type].update()
		except Exception as e:
			cl, exc, tb = sys.exc_info()
			line_number = traceback.extract_tb(tb)[-1][1]
			logging.error(sys_type + ": update failed at line " + str(line_number) + ": " +str(e))

	def cleanup(self) -> None:
		'''	
		Systems cleanup
		'''
		try:
			for sys_type in self.m_systems.keys():
				self.m_systems[sys_type].cleanup()
		except Exception as e:
			cl, exc, tb = sys.exc_info()
			line_number = traceback.extract_tb(tb)[-1][1]
			logging.error(sys_type + ": cleanup failed at line " + str(line_number) + ": " +str(e))






def load_scene(path :str, name :str =None) -> Scene:
	'''
	 Load entities, components and systems into a Scene
	 Scene file structure:
		[ENTITY]
		 ent_dir_path/
		[SYSTEM]
		 sys_file_path

	 params:
		path
		name
	'''
	
	if name is None:
		name = "scene"


	scene :Scene = Scene(name)
	state :str = ""	

	try:
		with open(path,"r") as scene_file:
			for line in scene_file:
				
				line = line.rstrip()
				if line[0] == "[":
					state = line
					continue
				if state == "[SYSTEM]":
					scene.load_systems(line)	
				if state == "[ENTITY]":
					scene.load_entity(line)

	except IOError as e:
		logging.error(str(e))
		pass

	return scene
