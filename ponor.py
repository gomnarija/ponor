import krcko.core as krcko
import definitions as defs
import time
import sys
import logging
import os

import definitions as defs


#TODO: main file structure


logging.basicConfig(filename='logs'+os.sep+'ponor.log',
			encoding='utf-8', 
			format='%(levelname)s %(filename)s:%(lineno)s - %(funcName)20s():%(message)s',
			level=logging.DEBUG)





ponor = krcko.Game("ponor")
intro = krcko.load_scene("scenes/intro.scene","intro")
scena = krcko.load_scene("scenes/test_scene.scene","scena")
ponor.add_scene(intro)
ponor.add_scene(scena)



#configs 
ponor.load_controls(defs.RES_DIR_PATH+"controls.ini")
ponor.load_ascii_table(defs.RES_DIR_PATH+"ascii_table.ini")


ponor.setup()

while not ponor.should_quit:
	ponor.update()

ponor.cleanup()


print(ponor.clock.mean_fps)
