from krcko.system import *
from krcko.component import *
from krcko.utils import *
from krcko.curse import *
from krcko.scene import *
from krcko.math import *
from krcko.turnmachine import *
from krcko.momo	import *
from krcko.audio import *
from krcko.template import *

from typing import Dict,Tuple,Deque,Optional
from collections import deque
import logging
import time
import statistics
from configparser import ConfigParser
import random




class Clock:
    """
	Framerate measurements and fps syncing
    """

    def __init__(self) -> None:
        self.last_time = time.perf_counter()
        self.time_samples: Deque[float] = deque()  # Delta time samples.
        self.max_samples = 64  # Number of fps samples to log.
        self.extra_time = 0.0  # Tracks how much the last frame was overshot.



    def sync(self, fps: Optional[float] = None) -> float:
        """Sync to a given framerate and return the delta time.
           params:
		fps - if None, just measure
	"""

        if fps is not None:
            # Wait until a target time based on the last time and framerate.
            desired_frame_time = 1 / fps
            target_time = self.last_time + desired_frame_time - self.extra_time
            # Sleep might take longer than asked.
            sleep_time = target_time - self.last_time - 0.001
            if sleep_time > 0:
                time.sleep(sleep_time)
            # Busy wait until the target_time is reached.
            while (extra_time := time.perf_counter() - target_time) < 0:
                pass
            self.extra_time = min(extra_time, desired_frame_time)

        # Get the delta time.
        current_time = time.perf_counter()
        delta_time = max(0, current_time - self.last_time)
        self.last_time = current_time

        # Record the performance of the current frame.
        self.time_samples.append(delta_time)
        while len(self.time_samples) > self.max_samples:
            self.time_samples.popleft()

        return delta_time

    @property
    def min_fps(self) -> float:
        """The FPS of the slowest frame."""
        try:
            return 1 / max(self.time_samples)
        except (ValueError, ZeroDivisionError):
            return 0

    @property
    def max_fps(self) -> float:
        """The FPS of the fastest frame."""
        try:
            return 1 / min(self.time_samples)
        except (ValueError, ZeroDivisionError):
            return 0

    @property
    def mean_fps(self) -> float:
        """The FPS of the sampled frames overall."""
        if not self.time_samples:
            return 0
        try:
            return 1 / statistics.fmean(self.time_samples)
        except ZeroDivisionError:
            return 0

    @property
    def median_fps(self) -> float:
        """The FPS of the median frame."""
        if not self.time_samples:
            return 0
        try:
            return 1 / statistics.median(self.time_samples)
        except ZeroDivisionError:
            return 0

    @property
    def last_fps(self) -> float:
        """The FPS of the most recent frame."""
        if not self.time_samples or self.time_samples[-1] == 0:
            return 0
        return 1 / self.time_samples[-1]



class Game:
	'''
		Game class
	'''
	def __init__(self,name):
		self.name :str    	     = name #name of the game
		self.scenes :Dict[str,Scene] = {} #dict containing loaded scenes
		self.main_window	     = None #main window object (curses)
		self.clock :Clock	     = Clock() #clock object
		self.current_scene :str	     = "" #name of the current scene
		self.should_quit   :bool     = False #
		self.max_fps :int  	     = 60#
		self.min_window_size	     = rectangle(35, 35, 0,0)
		self.max_window_size	     = rectangle(250, 250, 0,0)
		self.m_keys 		     = [] #key buffer
		self.m_prev_size	     = krcko.point(0,0)
		self.window_resized :bool    = False	
		self.key_dps		     = 7 #how many times to check for input, in a second
		self.turn_machine	     = TurnMachine() #turn machine object
		self.controls		     = ConfigParser()
		self.ascii_table	     = ConfigParser()

		self.control_defaults()
		self.ascii_defaults()


	def control_defaults(self):
		'''set default controls'''

		#player controls
		self.controls['PLAYER'] =\
			{
				'MOVE_UP' 	: 'KEY_UP',
				'MOVE_DOWN' 	: 'KEY_DOWN',
				'MOVE_LEFT' 	: 'KEY_LEFT',
				'MOVE_RIGHT' 	: 'KEY_RIGHT',
			}
		#momo 	
		self.controls['MOMO'] =\
			{
				'CONTINUE'	: 'KEY_SPACE',
				'PICKUP'	: 'p',
				'ATTACK'	: 'n',
				'EQUIP'		: 'u',
				'UNEQUIP'	: 'y'
			}


	def ascii_defaults(self):
		'''set default ascii characters'''
		
		self.ascii_table['ASCII'] =\
			{
				'PLAYER'	:	64,
				'WALL'		:	35,
				'ROOM_FLOOR'	:	4194430,
				'HALLWAY_FLOOR'	:	4194401,
				'RAVEN'		:	71,
				'MONEY'		:	42,
				'SWORD'		:	33,
				'BAR_FULL'	:	4194352,
				'BAR_EMPTY'	:	34
			}


	def load_ascii_table(self, path :str) -> None:
		'''load ascii table from a file'''
		try:
			self.ascii_table.read(path)
		except:
			logging.error("failed to load ascii table")


	def load_controls(self, path :str) -> None:
		'''load controls from a file '''
		try:
			self.controls.read(path)
		except:
			logging.error("failed to load controls")


	def get_ascii(self, key :str) -> int:
		'''ascii table lookup'''

		if key not in self.ascii_table['ASCII']:
			logging.warning("key " + key + " found in ascii table.")
			return ord('X')

		return int(self.ascii_table['ASCII'][key])


	def add_scene(self,scene: Scene) -> None:
		'''Add scene to game'''
		if scene.name in self.scenes.keys():
			logging.warning("Scene: " + scene.name + " already added.")
			return

		self.scenes[scene.name] = scene
		

	def  change_scene(self, scene_name :str) -> None:
		'''Change current scene'''
		
		if not scene_name in self.scenes.keys():
			logging.error("Scene " + scene_name + " not loaded.")
			return
		else:
			self.current_scene = scene_name
			#self.setup()
			


	def quit(self) -> None:
		'''Game should quit'''
		self.should_quit = True


	def detect_keys(self) -> None:

		#
		if not krcko.key_pressed(self.main_window):
			return
		#	
		key = krcko.get_key(self.main_window)
		self.m_keys.append(key)
		krcko.flush_keys(self.main_window)


	def get_key(self) -> str:
		
		if len(self.m_keys) > 0:
			return self.m_keys[-1]
		else:
			return "EMPTY"

	def scene_setup(self, scene_name :str) -> None:
		'''setup given scene'''
		if scene_name not in self.scenes.keys():
			logging.debug("Scene " + scene_name + " not loaded")
			return

		self.scenes[scene_name].add_game(self)
		self.scenes[scene_name].setup()
			


	def setup(self) -> None:
		'''Game setup:
			setup current scene, or asign the first as the current one.
			setup curses window
		'''
		if self.current_scene == "":
			if len(self.scenes) == 0:
				logging.error("Game: "+self.name+" doesn't have any scenes.")
				return
			else:
				self.current_scene = list(self.scenes.keys())[0]
		#
		self.scene_setup(self.current_scene)
		
		#init main window
		if self.main_window is None:
			self.main_window = curse_init()

	key_detection_timer = 0
	def update(self) -> None:
		'''
			Game update:
				check for window resize
				detect_keys
				update current scene.
				pop keys
				next turn.
				purge from scene
				update main window.
				sync the clock.
		'''
		#check if window has been resized
		curr_size	= krcko.point(0,0)
		curr_size.y, curr_size.x = krcko.get_window_size(self.main_window)
	
		if curr_size.y != self.m_prev_size.y or\
			curr_size.x != self.m_prev_size.x:
			#clear main window
			krcko.curse_clear(self.main_window)
			#
			self.window_resized = True
			#
			self.m_prev_size.y = curr_size.y
			self.m_prev_size.x = curr_size.x

		else:
			self.window_resized = False	
		
		#check window size
		#too small
		if curr_size.y < self.min_window_size.height or\
			curr_size.x < self.min_window_size.width:
			#
			krcko.curse_clear(self.main_window)
			krcko.draw_text(self.main_window,"window too small :(",1, 1)
			curse_update(self.main_window)
			return
		#too big
		if curr_size.y > self.max_window_size.height or\
			curr_size.x > self.max_window_size.width:
			#
			krcko.curse_clear(self.main_window)
			krcko.draw_text(self.main_window,"window too big :(", 1, 1)
			curse_update(self.main_window)
			return



		self.key_detection_timer += 1
		#input handling, key_dps per second
		if self.key_detection_timer * self.key_dps >= self.clock.median_fps:
			self.detect_keys()
			self.key_detection_timer = 0	

		#update current scene
		if self.current_scene == "":
			logging.error("Game: "+self.name+" current scene missing.")
			return
		#
		self.scenes[self.current_scene].update()

		if len(self.m_keys) > 0:
			self.m_keys.pop()


		#next turn action
		self.turn_machine.next()

		#remove deleted entities
		self.scenes[self.current_scene].purge()

		#update main window
		if not self.main_window is None:
			curse_update(self.main_window)
		#sync the clock
		self.clock.sync(self.max_fps)	


	def cleanup(self) -> None:
		'''
			Game cleanup:	
				scene cleanup.
				terminate main window.
		'''
		if not self.current_scene == "":
			self.scenes[self.current_scene].cleanup()	

		if not self.main_window is None:
			curse_terminate(self.main_window)

