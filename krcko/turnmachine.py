from enum import Enum, Flag
from typing import List, Any
from recordclass import recordclass
import logging



#action flags
class ActionFlag(Flag):
	SINGLE		= 1  #only one action of a given type 
			     #	can be done during a single turn

	ENTAILS		= 2  #actions with this flag necessary entail other actions

	ENDING		= 3  #end the turn after this action

	EMPTY		= 4  #no actions in this turn

	HALTING		= 5  #halt next actions, until 



def create_action(name :str, flags :List[ActionFlag], props :List[str], vals :List[Any]):
	action = recordclass(name, ['flags'] + props)
	a = action(flags,*vals)
	return a,action


class TurnMachine:
	'''state machine responsible for turn handling '''


	def __init__(self) -> None:

		#returned when there are no actions in a current turn
		self.m_empty_action	:recordclass
		self.m_empty_action, fact = create_action("empty", [ActionFlag.EMPTY], [], [])

		self.m_turn 		:List[recordclass] 	= [self.m_empty_action]
		self.m_next_turn 	:List[recordclass] 	= []
		self.m_turn_number	:int		   	= 0
		self.m_halted		:bool			= False
	
	@property
	def action(self) -> recordclass:
		''' get the current action '''
		if len(self.m_turn) > 0:
			return self.m_turn[-1]
		else:
			return self.m_empty_action

	@property
	def turn_number(self) -> int:
		return self.m_turn_number



	@property
	def is_halted(self) -> bool:
		return self.m_halted



	def halt(self) -> None:
		self.m_halted = True


	def unhalt(self) -> None:
		self.m_halted = False

	def insert_action(self, action :recordclass) -> None:
		'''add action to the beggining of the current turn'''



		#if action has SINGLE flag,
		# check if same action already exists in next turn
		if ActionFlag.SINGLE in action.flags and\
			any(type(action).__name__ == type(a).__name__ for a in self.m_turn):
				#logging.warning("Action of this type with flag SINGLE already in this turn, type: " + str(action.__class__))
				return

	
		self.m_turn.insert(0,action)


		



	def add_action(self, action :recordclass) -> None:
		''' add action to the next turn '''
		
			
		#if action has SINGLE flag,
		# check if same action already exists in next turn
		if ActionFlag.SINGLE in action.flags and\
			any(type(action).__name__ == type(a).__name__ for a in self.m_next_turn):
				#logging.warning("Action of this type with flag SINGLE already in next turn, type: " + str(action.__class__))
				return

	
		self.m_next_turn.insert(0,action)



	def next(self) -> None:
		''' go to the next action '''
	


		#unless it's halted
		if self.is_halted:
			return

	
		#go to the next action,
		# if there are any
		if len(self.m_turn) > 0:
			self.m_turn.pop()
		#if no more actions in the current turn, and 
		# next turn has ENDING flag in some of it's actions, the next
		#  turn is ready. 
		elif any(ActionFlag.ENDING in a.flags for a in self.m_next_turn):
			#
			self.end_turn()
			
		
		#check for halting		
		if ActionFlag.HALTING in self.action.flags:
			self.halt()


		#if action has ENDING flags, end turn
		if ActionFlag.ENDING in self.action.flags:
			self.end_turn
	

	def end_turn(self):
		''' end turn, and load up next one '''
		
		self.m_turn_number	+= 1
		self.m_turn 		= self.m_next_turn
		self.m_next_turn 	= [] 
		


		
