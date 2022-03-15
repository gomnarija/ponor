from configparser import ConfigParser
from typing import List, Any, Tuple
import random
import re
import logging

import krcko.core as krcko

def parse_component(comp_str :str) -> Tuple[Any, bool]:
	'''returns tuple(component, should_stop) '''

	#[~component_name : chance]
	#if chance is not given, chance is 100
	#if ~ is given and dice roll fails stop template loading

	#must be inside []
	if comp_str[0] != "[" or comp_str[-1] != "]":
		logging.error("Wrong component syntax, did you forget [] ?")
		return (False, None)

	#strip []
	comp_str = comp_str[1:-1]
	#should halt if dice roll fails
	halting = "~" in comp_str
	comp_str = comp_str.replace("~", "")
	
	#chance, 100 if not given 
	chance :int = 100
	if ":" in comp_str:
		chance = int(comp_str.split(":")[1])
	#
	comp_name	=	comp_str.split(":")[0]
		

	#roll them
	if krcko.dice_roll(chance):
		component, _ = krcko.load_component(krcko.defs.PAT_DIR_PATH + comp_name)
		return (False, component)
	else:
		return (halting, None)
		



m_magic :str	=	'[ \t]*(\[[\w:\d \t._~:]*\]|[a-zA-Z0-9 \t=_^.\"]*)'
def load_template(path :str) -> List[Any]: 
	'''Load template components from template file, and assign their
		values.

		returns list of components
	'''
	
	#components for the new entity
	components = []
	#currently loaded component
	curr_component = None
	try:
		with open(path, "r") as tml_file:
			tokens :List[str] = re.findall(m_magic, tml_file.read())
			for token in tokens:
				#white space,tabs
				token = token.replace(" ", "")	
				token = token.replace("\t", "")	
				if token == "":
					continue
				#component 
				if token[0] == "[":
					#
					if curr_component is not None:
						components.append(curr_component)
						curr_component = None						

					stop, component = parse_component(token)
					#halting component failed, stop further loading
					if stop:
						break
					#component failed, continue
					if component is None:
						continue
					#all good
					curr_component = component
				
				#value
				else:
					#no components currently loaded, continue
					if curr_component is None:
						continue
					
					#value_name = value
					if len(token.split("=")) != 2:
						logging.error("Wrong value syntax. Token: " + token)
						continue
					#
					val_name :str = token.split("=")[0]
					value = token.split("=")[1]
		

					#convert to bool if not inside ""
					if value == "True":
						value = True
					elif value == "False":
						value = False
					#convert to int if not inside "", and not bool
					elif value[0] != '"':
						#min_val^max_val
						if "^" in value:
							min_v = value.split("^")[0]
							max_v = value.split("^")[1]
							value = (min_v, max_v) #calculate later 
						else:
							value = int(value)
					else:
						#strip ""
						value = value[1:-1]
				
					#	
					if val_name not in curr_component._asdict().keys():	
						logging.error(val_name + " not found in " + type(curr_component).__name__)
						continue

					#
					setattr(curr_component, val_name, value)


						
	except Exception as e:
		logging.error("failed to load template from : " + path + " " + str(e))
		return None

	
	#leftovers
	if curr_component is not None:
		components.append(curr_component)
	#	
	return	components 
