class MomoView(krcko.System):
	'''Displays momo'''
	
	
	#STELOVANJE
	margin			:int	=	2
	letters_per_second	:float	=	26
	



	text_buffer		=	""

	def setup(self):
		pass	
	

	_started :bool = False#wait for start action	
	def update(self):
		
		if not self._started:
			if self.turn_machine.action_name == "START":
				self._started = True
			else:
				return		


		self.update_view()

		#draw view borders
		krcko.draw_window_border(self.view, tl = krcko.AC_DIAMOND,\
					tr = krcko.AC_DIAMOND,\
					bl  = krcko.AC_DIAMOND,\
					br = krcko.AC_DIAMOND)
		

		#check for momo action
		if self.turn_machine.action_name == "MOMO":
			#get action
			action = self.turn_machine.action
			#draw text and options
			#copy text to buffer
			self.buffer_text(action.text)
			self.momo_display(self.text_buffer, action.action_names, action.action_keys, action.text == self.text_buffer)
			#check if any of the keys is pressed
			key_index = self.check_keys(action.action_keys) 
			#-1 if not pressed, else action_keys index
			if key_index != -1:
				#unhalt the turn machine
				self.turn_machine.unhalt()
				#insert it if has inserting flag
				if krcko.ActionFlag.INSERTING in action.actions[key_index].flags:
					#insert action for the pressed key
					self.turn_machine.insert_action(action.actions[key_index])
				else:	
					#add action for the pressed key
					self.turn_machine.add_action(action.actions[key_index])
				#empty text buffer
				self.text_buffer	=	""



		#update view
		krcko.curse_update(self.view)

				
					
			
		

	def cleanup(self):
		pass

	cs :int =	0
	def buffer_text(self, text :str) -> None:
		'''Add text to buffer'''
		#buffer is full
		if self.text_buffer == text:
			return

		self.cs += 1
		#:
		if self.letters_per_second * self.cs  > self.game.clock.median_fps:
			self.cs = 0 
			self.text_buffer += text[len(self.text_buffer)]


	def check_keys(self, action_keys :List[str]) -> int:
		'''checks if any of the keys is pressed
			returns index of that key if found,
			else return -1
		'''

		for index in range(0, len(action_keys)):
			#check
			if action_keys[index] == self.game.get_key():
				return index 


		return -1
			

	

	def momo_display(self, text : str, option_names :List[str], option_keys :List[str], display_options : bool):
		'''display text and options'''
		
		
	
		#text area rect
		# 
		text_rect	:krcko.rectangle = krcko.rectangle(self.view_rect.height - 3, self.view_rect.width - 2*self.margin, self.view_rect.y + 1, self.view_rect.x + self.margin)
		#options area rect
		options_rect	:krcko.rectangle = krcko.rectangle(3, self.view_rect.width, self.view_rect.bottom - 2, self.view_rect.x)



		#break text up into lines of lenght view_rect.width - 2*margin
		#split text into lines of max_len view_rect.width - 2*margin
		max_len		:int	   = self.view_rect.width - 2*self.margin
		#split
		lines		:List[str] = [text[i: i+max_len] for i in range(0, len(text), max_len)]
		#if there are more lines then height, draw only last ones
		starting_line	:int	=	max(0, len(lines) - text_rect.height)
		


		#display text
		curr_line	:int	=	0
		for line in lines[starting_line:]:
			krcko.draw_text(self.view, line, text_rect.top + curr_line,self.margin)	
			curr_line	+= 1	




		#if there isn't a same amount of names and keys,
		# something's wrong :( 
		if len(option_names) != len(option_keys):
			logging.error("failed to display options")	
			return


		#don't displat options until displaying text is done
		if not display_options:
			return

		#x of the current option
		curr_x	:int 	=	3

		#display options
		for index in range(0, len(option_names)):

			#construct option string
			#	option_name<option_key>
			option :str = option_names[index] + "<" + option_keys[index] + ">"
			#no more space
			if curr_x + len(option) > self.view_rect.width:
				logging.error("out of options space")
				return

			#draw
			krcko.draw_text(self.view, option, options_rect.y, curr_x) 
			#next option x
			curr_x += len(option) + 1	


	def update_view(self):
		''' Update a view''' 
	
		main_window = self.game.main_window
		
		
		
		main_rect	:krcko.rectangle = krcko.rectangle(0,0,0,0)
		view_rect	:krcko.rectangle = krcko.rectangle(0,0,0,0)

		main_rect.height, main_rect.width = krcko.get_window_size(main_window)
		
		#momo view is on top of the dungeon view,
		view_rect.y = 0 
		view_rect.x = 0 

		view_rect.height = int((main_rect.height/100)*20)#20%
		view_rect.width  = main_rect.width

		self.view_rect 	= view_rect
		self.view 	= krcko.create_sub_window(main_window,view_rect.height, view_rect.width, view_rect.y, view_rect.x)

		#clear view
		krcko.curse_clear(self.view)


sys_instance = MomoView()	
