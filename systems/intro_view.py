class IntroView(krcko.System):
	'''Displays the inventory'''
	
	import pyfiglet
	import random
	
	#STELOVANJE
	figlet_font	:str	=	"epic"
	logo_text	:str	=	"ponor"
	logo_scroll_speed :int	=	40	#per second
	next_scene_time	:int	=	15
	fragments :List[str]	=	[',','.',"'"]
	next_scene	:str	=	"scena"


	def setup(self):
		#generate particles
		density		=	3
		self.particles :List[Tuple[str, krcko.point]]	=	[]
		for index in range(0, int(((500 * 500) / 100) * density)):
			position = krcko.point(self.random.randint(0, 500), self.random.randint(0,500))
			self.particles.append( (self.random.choice(self.fragments), position))


		#play intro song
		#krcko.play_audio(defs.MUS_DIR_PATH + "samo_ti.wav")
		


	logo_time   :int	=	3	#seconds until logo pops up
	scroll_time :int	=	6	#seconds until logo starts scrolling
	cs	  :int  	=	0	#frame counter
	sb	  :int		=	0	#logo scroll_back counter
	sbs	  :int		=	0	#scroll frame counter
	next_scene_loaded :bool =	False
	def update(self):
		self.update_view()

		#update window view
		self.update_view()

		self.draw_particles(self.sb)
		#get median frames per second, it takes some time so it 
		# needs max :)
		m_fps	=	max(self.game.clock.median_fps,10)
		
		#
		self.cs += 1
		if self.cs / self.logo_time <= m_fps:
		
			#draw me before logo apears			
			self.draw_me()
		else:
			#wait for scroll back
			if self.cs / self.scroll_time <= m_fps:
				self.draw_logo(0)
				#setup next scene while waiting
				if not self.next_scene_loaded:
					self.game.scene_setup(self.next_scene)
					self.next_scene_loaded = True


			#scroll back
			else:
				self.sbs += 1
				if self.sbs * self.logo_scroll_speed >= m_fps:
					self.sbs = 0
					self.sb  += 1	
				self.draw_logo(int(self.sb/4))
		

		#clear window, change scenes
		if self.cs / self.next_scene_time >= m_fps:
			#krcko.curse_clear(self.view)
			self.game.change_scene("scena")


		krcko.curse_update(self.view)




	def cleanup(self):
		pass


	def draw_particles(self, scroll_back :int) -> None:
		'''draw particles on the screen'''
		

		for ascii, position in self.particles:
			if position.y - scroll_back < self.view_rect.bottom -1 and\
				position.x < self.view_rect.right -1 and\
					position.y - scroll_back >= 0:
				#
				krcko.draw_char(self.view, ascii, position.y - scroll_back, position.x)


	def draw_me(self) -> None:
		'''draw me :) '''

		me_str	:str	=	"gomnarija"
		
		#center
		y_center :int	=	int(self.view_rect.bottom/2) 
		x_center :int	=	int(self.view_rect.right/2) - int(len(me_str)/2) 
	
		krcko.draw_text(self.view, me_str, y_center, x_center)



	def draw_logo(self, scroll_back :int) -> None:
		'''draws figlet logo'''

		logo_str :str	=	self.pyfiglet.figlet_format(self.logo_text, font = self.figlet_font)

		#split into lines
		logo	:List[str]	=	logo_str.split('\n')
		

		#window too small
		if len(logo[0]) >= self.view_rect.width:
			logging.debug("window too small ")
			return
		#
		#center it 
		center_x :int	=	int(self.view_rect.right/2) - int(len(logo[0])/2) 

		#line by line
		curr_y :int		=	int(self.view_rect.bottom/2) - len(logo) - scroll_back
		logo_line :str
		for logo_line in logo:
			curr_y	+= 1
			#out of bounds
			if curr_y >= self.view_rect.bottom or\
				curr_y < 0:
				#
				
				continue
			#
			krcko.draw_text(self.view, logo_line, curr_y,center_x)
			



	def update_view(self) -> None:
		''' Update a view''' 
	
		main_window = self.game.main_window

		
		main_rect	:krcko.rectangle = krcko.rectangle(0,0,0,0)
		view_rect	:krcko.rectangle = krcko.rectangle(0,0,0,0)

		main_rect.height, main_rect.width = krcko.get_window_size(main_window)
		
		#whole main window
		view_rect.y = main_rect.y
		view_rect.x = main_rect.x
		#
		view_rect.height = main_rect.height
		view_rect.width  = main_rect.right

		self.view_rect 	= view_rect
		self.view 	= krcko.create_sub_window(main_window,view_rect.height, view_rect.width, view_rect.y, view_rect.x)

		#clear view
		krcko.curse_clear(self.view)




sys_instance = IntroView()	
