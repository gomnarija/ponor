from abc import ABCMeta, abstractmethod
from typing import Any

class System(metaclass=ABCMeta):
	'''
	 Systems abstract base class
	'''

	scene = None

	def add_scene(self,scene: Any) -> None:
		'''
		 Add scene, called by scene when loading systems.
		params:
			scene: parent scene
		'''
		self.scene = scene

	def add_game(self, game: Any) -> None:
		'''.'''

		self.game = game
	
	def add_turn_machine(self, turn_machine :Any) -> None:
		'''.'''

		self.turn_machine = turn_machine


	@abstractmethod
	def setup(self) -> None:
		'''
		 Called once on start.
		'''
		pass

	@abstractmethod
	def update(self) ->  None:
		'''
		 Called every frame.
		'''
		pass
	
	@abstractmethod
	def cleanup(self) -> None:
		'''
		 Called once on exit.
		'''
		pass
