import re
from typing import List, Dict, Any, Tuple
import random
import logging
import sys


class Momo():

	def __init__(self):
	
		self.m_magic 		:str = '[\s]*(#|>{1,2}|"(?:\\.|[^\\"])*"?|\[[\w:\d,-^]*\]|[a-zA-Z:_, ]+|\+)'
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


	def parse_field_name(self, token :str) -> Tuple[str, List[str]]:
		'''parses field name token, returns field name and dependencies'''

		#FIELD_NAME : var, var
		field_name :str
		deps :List[str] = []
	
		#clear white space
		token = token.replace(" ","")	
	
		token_split :List[str]	=	token.split(':')
			
		#field name
		field_name = token_split[0]
		#must be all letters
		if not field_name.replace("_","").isalpha():
			logging.error("Wrong field syntax")
			return None, None

		#check if there are dependencies
		if len(token_split) > 1:
			deps = token_split[1].split(',')


		#
		return 	field_name, deps	



	def parse_line(self, tokens :List[str], deps :List[str]) -> Tuple[str, str]:
		'''parses line, returns text and condition'''



		dep :str
		#check dependencies
		for dep in deps:
			if dep not in self.m_arguments.keys():
				logging.error("Missing dependency: " + dep)
				return "", ""

	
		#final line text
		text :str 	= ""
		#condition token
		condition :str = ""
		
		token :str
		is_condition :bool 	= False
		for token in tokens:
		#string literal
			if token[0] == '"' and token[-1] == '"':
				#strip the "" and add it to final text 
				text += token[1:-1]
				continue
			else:
				#remove white space
				token = token.replace(" ", "")

			#decor :)
			if token == "+":
				continue	
	
			#condition
			if token == ":":
				#next token is condition string
				is_condition = True	
				continue
			#get condition and break
			if is_condition:
				condition = token
				break	
			#variable
			if token not in self.m_arguments.keys():
				logging.error("missing argument: " + token)	
				continue
			#all good
			text += str(self.m_arguments[token])
			

		return text, condition
	
	def read(self, input :str, fields :List[str]) -> None:
		'''read input string'''
		
		tokens :List[str] = re.findall(self.m_magic, input)
	

		#required variables
		dependencies :List[str] = []
		
	
		#parse tokens
		index 	:int		=	0
		curr_field :str 	=	"DEFAULT"
		line :List[str]		=	[]
		is_comment :bool	=	False
		while index < len(tokens):
			#
			token :str	=	tokens[index]
			#EOF and not a comment
			if index == len(tokens)-1 and not is_comment:
				#add current token
				line.append(token)
				
			#> or >> or (EOF and not a comment)
			if token[0] == ">" or (index == len(tokens)-1 and not is_comment):
				#not a comment 
				is_comment = False
				#current field must be in fields
				if not curr_field in fields and len(fields) > 0:
					#empty line 
					line = []
				
				#if there is a line, parse it 
				elif len(line) > 0:
					#parse line
					text :str
					condition :str
					text, condition = self.parse_line(line, dependencies)
					#if condition is met or no condition given, the text is avaliable
					if condition == "" or self.check_condition(condition):
						#check if field already exists
						if curr_field in self.m_avaliable.keys():
							self.m_avaliable[curr_field].append(text)
						#if not create it
						else:
							self.m_avaliable[curr_field] = [text]				

					#clear line 
					line = []


				#new field
				if token == ">>":
					#clear previous dependencies
					dependencies = []
					#go for the next token
					index+=1
					#out of bounds
					if index >= len(tokens):
						logging.error("Missing field name")
						break

					token = tokens[index]
		
					field_name :str
					deps	:List[str]
					#parse field name
					field_name, deps = self.parse_field_name(token)
					#something's wrong
					if field_name is None or\
						deps is None:
						#
						return
					
					#all good
					curr_field = field_name
					dep :str
					#add dependencies
					for dep in deps:
						if dep not in dependencies:
							dependencies.append(dep)


			#start of the comment
			elif token[0] == "#":
				is_comment = True

			elif not is_comment:		
				#fill line
				line.append(token)
		
			#
			index+=1



	def load(self, path :str) -> None:
		'''load from a file into m_input'''
		
		try:
			with open(path, "r") as momo_file:
				self.m_input = momo_file.read()
		except IOError as e:
			logging.error("IO error : " + str(e))


	def run(self, fields = []) -> None:
		'''read saved input, only given fields will be read, or all if fields not given'''

		#clear fields
		self.m_avaliable = {}

		#nothing loaded
		if self.m_input == "":
			logging.warning("nothing loaded")
			return

		self.read(self.m_input, fields)	

	def clear(self) -> None:
		'''clear arguments and avaliables'''

		self.m_arguments = {}
		self.m_avaliable = {}


	def add_arguments(self, args :Dict[str, int]) -> None:
		'''add arguments'''
	
		#remove previous ones
		self.m_arguments = {}
		for arg in args.keys():
			self.m_arguments[arg] = args[arg]




	def pick(self, field :str) -> str:
		'''pick a random text from field'''
		#field not avaliable
		if field not in self.m_avaliable.keys():
			return ""

		return random.choice(self.m_avaliable[field])
