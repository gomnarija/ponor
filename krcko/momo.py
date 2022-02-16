import re
from typing import List,Dict, Any
import random
import logging
import sys


class Momo():

	def __init__(self):
	
		self.m_magic 		:str = '[\s]*(:{1,2}|"(?:\\.|[^\\"])*"?|\[[\w:\d,-^]*\]|[a-zA-Z]+)'
		self.m_input		:str = ""
		
		self.m_avaliable :Dict[str,List[str]]	= {} #avaliable fields
		self.m_arguments :Dict[str, int]	= {} #arguments 



	def check_condition(self, condition :str) -> bool:
		'''checks if the condition is met'''

		#[var:min_val^max_val,var:val]
		
		#must start and end with []
		if condition[0] != '[' or\
			condition[-1] != ']':
			#
			logging.error("Invalid condition syntax. Did you forget to close the brackets ? ")
			return False

		#strip brackets
		condition = condition[1:-1]


		#no conditions given, return True
		if condition == "":
			return True

		
		#conditions are separated with ,
		#
		condition_list :List[str]	=	condition.split(',')

		#go trough them
		cc :str
		for cc in condition_list:
			#variable:value
			#variable:min_value^max_value
			cc_split :List[str] = cc.split(':')
			#something's off
			if len(cc_split) != 2:
				logging.error("Invalid condition syntax.")
				return False
			#get var name
			variable_name :str = cc_split[0]
			#check if variable is given in arguments
			if not variable_name in self.m_arguments.keys():
				logging.error("Argument " + variable_name + " not given.")
				return False

			#get arg value
			arg_value :int	=	self.m_arguments[variable_name]
			
			#get required value
			req_value :str  =	cc_split[1]
			#two possible cases
			#min_value^max_value
			if '^' in req_value:
				#
				min_value :int 
				max_value :int
				#
				val_split :List[str] = req_value.split('^')
				#must be 2 values
				if len(val_split) != 2:
					logging.error("Invalid min^max syntax.")	
					return False
				#must be numbers
				if not val_split[0].isnumeric() or\
					not val_split[1].isnumeric():
					#
					logging.error("Values must be numbers.")
					return False

				#
				min_value	=	int(val_split[0])
				max_value	=	int(val_split[1])
							
				return min_value <= arg_value <= max_value
	

			#value given
			else:
				#must be a number
				if not req_value.isnumeric():
					logging.error("Values must be numbers.")
					return False	
				return int(req_value) == arg_value
 

		return False


	def read(self, input :str) -> None:
		'''read input string'''
		
		tokens :List[str] = re.findall(self.m_magic, input)
		
		#parse tokens
		index 	:int	=	0
		curr_field :str =	"DEFAULT"
		for index in range(0,len(tokens)):
			#
			token :str	=	tokens[index]
			#new field
			if token == "::":
				#go for the next token
				index+=1
				#out of bounds
				if index >= len(tokens):
					logging.error("Missing field name")
					break

				token = tokens[index]
				#must be all letters
				if not token.isalpha():
					logging.error("Wrong field syntax.")
					continue
				#all good
				curr_field = token
				continue

			#text : condition
			elif token == ":":
				#go for the previous one, text
				index-=1
				token = tokens[index]
				#must start with "	
				if token[0] != '"':
					index+=1
					logging.error('Text must be inside ""')
					continue
				#get text
				text :str = token
				
				#go for the condition
				index+=2
				token = tokens[index]
				#out of bounds
				if index >= len(tokens):
					logging.error("Wrong syntax")
					break

				#must start with [
				if token[0] != '[':
					index -= 1
					logging.error("Conditions must be inside []")
					continue

				#get condition
				condition :str = token
						
				#if condition is met, the text is avaliable
				if self.check_condition(condition):
					#check if field already exists
					if curr_field in self.m_avaliable.keys():
						self.m_avaliable[curr_field].append(text[1:-1])
					#if not create it
					else:
						self.m_avaliable[curr_field] = [text[1:-1]]				

			else:

				continue	



	def load(self, path :str) -> None:
		'''load from a file into m_input'''
		
		try:
			with open(path, "r") as momo_file:
				self.m_input = momo_file.read()
		except IOError as e:
			logging.error("IO error : " + str(e))


	def run(self) -> None:
		'''read saved input'''

		#nothing loaded
		if self.m_input == "":
			logging.warning("nothing loaded")
			return

		self.read(self.m_input)	

	def clear(self) -> None:
		'''clear arguments and avaliables'''

		self.m_arguments = {}
		self.m_avaliable = {}


	def add_arguments(self, args :Dict[str, int]) -> None:
		'''add arguments'''
		
		for arg in args.keys():
			self.m_arguments[arg] = args[arg]


	def pick(self, field :str) -> str:
		'''pick a random text from field'''
		#field not avaliable
		if field not in self.m_avaliable.keys():
			return ""

		return random.choice(self.m_avaliable[field])
