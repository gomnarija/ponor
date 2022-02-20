import curses
import logging
import locale


from typing import Tuple,Optional,Union,Callable,List,Any



#curses stuff :) 


#needed for ACS
curses.initscr()

AC_BULLET = curses.ACS_BULLET
AC_DIAMOND = curses.ACS_DIAMOND
AC_CKBOARD = curses.ACS_CKBOARD


#color stuff :) 
# color isn't used at the moment
#  maybe remove this :/ 
curses.start_color()


COLOR_RED_BLACK		:int = 1
COLOR_GREEN_BLACK	:int = 2
COLOR_YELLOW_BLACK	:int = 3
COLOR_BLUE_BLACK	:int = 4
COLOR_MAGENTA_BLACK	:int = 5
COLOR_CYAN_BLACK	:int = 6
COLOR_WHITE_BLACK	:int = 7

curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)




def curse_init() -> curses.window:
	'''curses init'''
	#locale.setlocale(locale.LC_ALL, '')
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


def curse_clear(win :curses.window) -> None:
	'''clears window'''
	win.erase()


def curse_update(win :curses.window) -> None:
	win.refresh()


def create_sub_window(win :curses.window, lines :int, cols :int, y :int, x :int) -> curses.window:
	''' Generate new sub window at y,x with size lines,cols '''
	
	try:
		sub = win.subwin(lines,cols,y,x)	
		sub.keypad(True)
		sub.nodelay(True)
		return sub
	except Exception as e:
		logging.error("Sub windowing failed :" + str(e))
		return win#TODO:

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
			win,text
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

def draw_char(win :curses.window,ch: Union[str,bytes,int], y :int=-1,x :int=-1) -> None:
	'''
		Draw character on the given window.
		params:
			win,text
		   optional:
			y,x
	'''
	try:	
		if x == -1:
			y,x = get_cursor_position(win)
		win.addch(y,x,ch)
	except Exception as e:
		logging.error(e)
		logging.debug(y)
		pass


def draw_hline(win :curses.window,ch: Union[str,bytes,int],  n: int, y :int=-1,x :int=-1) -> None:
	'''
		Draw horizontal line on the given window.
		params:
			win,ch,n
		   optional:
			y,x
	'''
	try:	
		if x == -1:
			y,x = get_cursor_position(win)
		win.hline(y,x,ch,n)
	except Exception as e:
		logging.error(e)
		pass

def draw_vline(win :curses.window,ch: Union[str,bytes,int], n: int, y :int=-1,x :int=-1) -> None:
	'''
		Draw vertical line on the given window.
		params:
			win,ch,n
		   optional:
			y,x
	'''
	try:	
		if x == -1:
			y,x = get_cursor_position(win)
		win.vline(y,x,ch,n)
	except Exception as e:
		logging.error(e)
		pass


def draw_rectangle(win :curses.window,ch :str, rect) -> None:
	'''
		Draw a rectangle
	'''

	if rect.height > rect.width:
		x :int 
		for x in range(rect.x, rect.right):
			draw_vline(win, ch, rect.height, rect.y, x)
	else:
		y :int
		for y in range(rect.y, rect.bottom):
			draw_hline(win, ch, rect.width, y, rect.x)



def draw_window_border(win :curses.window,ls :Union[str,bytes,int]=curses.ACS_VLINE,
					   rs :Union[str,bytes,int]=curses.ACS_VLINE,
					    ts :Union[str,bytes,int]=curses.ACS_HLINE,
					     bs :Union[str,bytes,int]=curses.ACS_HLINE,
					      tl :Union[str,bytes,int]=curses.ACS_ULCORNER,
					       tr :Union[str,bytes,int]=curses.ACS_URCORNER,
					        bl :Union[str,bytes,int]=curses.ACS_LLCORNER,
					         br :Union[str,bytes,int]=curses.ACS_LRCORNER
						) -> None:
	'''
		Draw vertical line on the given window.
		params:
			win,left side, right side, top, bottom, upper-left corner,
			upper-right corner, bottom-left corner, bottom-right corner
	'''
	try:	
		win.border(ls,rs,ts,bs,tl,tr,bl,br)
	except Exception as e:
		logging.error(e)
		pass


def color_on(win :curses.window,col_pair :int) -> None:
	''' Turn on color attribute
	 params:
		window, color pair
	'''
		
	try:
		win.attron(curses.color_pair(col_pair))
	except Exception as e:
		logging.error(e)
		pass

def color_off(win :curses.window,col_pair :int) -> None:
	''' Turn off color attribute
	 params:
		window, color pair
	'''
		
	try:
		win.attroff(curses.color_pair(col_pair))
	except Exception as e:
		logging.error(e)
		pass


def do_with_color(win: curses.window,col_pair :int, func :Callable, args: List[Any]) -> None:
	'''
		Turn on color, do stuff, turn off color
	 params:
		window,color pair, function to call, function arguments
	'''

	
	color_on(win,col_pair)	

	try:
		func(*args)
	except Exception as e:
		logging.error(e)

	color_off(win,col_pair)	





def get_key(win :curses.window) -> str:
	'''Check buffer for pressed keys'''
	key :str = "EMPTY"
	try:
		key = win.getkey()
	except Exception as e:
		#no keys  in buffer
		pass
	return key
	
def key_pressed(win :curses.window) -> bool:
	'''Check if key is pressed'''
	key :int = 0
	try:
		key = win.getch()
		#-1 = no input
		if not key == -1:	
			curses.ungetch(key)
			return True

	except Exception as e:
		return False
		pass
	return False


def flush_keys(win :curses.window) -> None:
	'''discard input'''	
	curses.flushinp()



def get_screen_text(win :curses.window) -> List[str]:
	'''returns currently displayed text as List[Tuple(position, ascii)]'''
	

	#result	
	lines				=	[]
	line_height, line_width 	=	get_window_size(win)


	try:
	
		for y in range(0, line_height - 1):
			for x in range(0, line_width - 1):
				lines.append(((y,x), win.inch(y, x)))

		return lines
		
	except Exception as e:
		logging.error(str(e))
		return []





