import curses
import logging

from typing import Tuple

#curses stuff :) 


def curse_init() -> curses.window:
	'''curses init'''
	stdscr = curses.initscr()
	curses.noecho()
	curses.cbreak()
	stdscr.keypad(True)
	stdscr.nodelay(True)
	curses.curs_set(0)
		

	return stdscr


def curse_terminate(win :curses.window) -> None:
	'''curses terminate'''
	curses.nocbreak()	
	win.keypad(False)
	win.nodelay(False)
	win.keypad(False)
	curses.echo()
	curses.curs_set(1)
	
	curses.endwin()


def curse_update(win :curses.window) -> None:
	'''refresh window'''
	win.refresh()
	win.clear()

def get_window_size(win :curses.window) -> Tuple[int,int]:
	'''
	 Return Tuple containing max y and max x
	'''
	try:
		return win.getmaxyx()
	except Exception as e:
		logging.error(e)
		return (0,0)

def get_cursor_position(win :curses.window) -> Tuple[int,int]:
	'''Return Tuple containing curr y and curr x'''
	try:
		return win.getyx()
	except Exception as e:
		logging.error(e)
		pass
		return (0,0)
	

def draw_text(win :curses.window,text: str, y :int=-1,x :int=-1) -> None:
	'''
		Draw text on the given window.
		params:
			stdscr,text
		   optional:
			y,x
	'''
	try:	
		if x == -1:
			y,x = get_cursor_position(win)
		win.addstr(y,x,text)
	except Exception as e:
		logging.error(e)
		pass



def get_key(win :curses.window) -> str:
	'''Check buffer for pressed keys'''
	key = "KEY"
	try:
		key = win.getkey()
	except Exception as e:
		#no keys  in buffer
		pass
	return key
	
		
