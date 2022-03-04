class brana(krcko.System):
	comp_inst = None
	x	  = 0
	def setup(self):
		self.x = 0
	def update(self):
		k = self.scene.game.get_key()
		if k == "q":
			self.scene.game.quit()


	def cleanup(self):
		pass



sys_instance = brana()

