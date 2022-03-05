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
	
	INSERTING	= 6  #insert this action into current turn


def create_action(name :str, flags :List[ActionFlag], props :List[str], vals :List[Any], entails = None):
	action = recordclass(name, ['flags','entails'] + props)
	return action(flags,entails,*vals)


def momo_action(momo_text :str, actions :List[any], action_names :List[str], action_keys :List[str]) -> Any:
		'''creates momo action'''

		return 	create_action("MOMO",\
						[ActionFlag.HALTING,ActionFlag.INSERTING],\
							['text', 'actions', 'action_names', 'action_keys'],\
								[momo_text, actions, action_names, action_keys])





class TurnMachine:
	'''state machine responsible for turn handling '''


	def __init__(self) -> None:
		
		self.m_turn 		:List[recordclass] 	= [self.empty_action]
		self.m_next_turn 	:List[recordclass] 	= []
		self.m_turn_number	:int		   	= 0
		self.m_halted		:bool			= False

	
	@property
	def empty_action(self) -> recordclass:
		'''returned when there are no actions in a current turn.'''
		return create_action("EMPTY", [ActionFlag.EMPTY], [], [])

	@property
	def ending_action(self) -> recordclass:
		'''action signaling end of the current turn.'''
		return create_action("END", [ActionFlag.ENDING], [],[])

	
	@property
	def action(self) -> recordclass:
		''' get the current action '''
		if len(self.m_turn) > 0:
			return self.m_turn[-1]
		else:
			return self.empty_action

	@property
	def turn_number(self) -> int:
		return self.m_turn_number



	@property
	def is_halted(self) -> bool:
		return self.m_halted


	@property
	def action_name(self) -> str:
		return type(self.action).__name__


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

		
		#if current turn is empty insert empty
		# action that will serve until end of current 
		#  run
		if len(self.m_turn) == 0: 
			self.m_turn.insert(0, self.empty_action)

	
		self.m_turn.insert(0,action)
			
		#entailed action
		if ActionFlag.ENTAILS in action.flags and\
			action.entails is not None:
			#
			self.m_turn.insert(0, action.entails)

			



	def add_action(self, action :recordclass) -> None:
		''' add action to the next turn '''
		
			
		#if action has SINGLE flag,
		# check if same action already exists in next turn
		if ActionFlag.SINGLE in action.flags and\
			any(type(action).__name__ == type(a).__name__ for a in self.m_next_turn):
				#logging.warning("Action of this type with flag SINGLE already in next turn, type: " + str(action.__class__))
				return

	
		self.m_next_turn.insert(0,action)
	
		#entailed action
		if ActionFlag.ENTAILS in action.flags and\
			action.entails is not None:
			#
			self.m_next_turn.insert(0, action.entails)

		



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
		


		
