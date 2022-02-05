from typing import Iterator
import os
import sys
import traceback


def gen_files(dir: str) -> Iterator[str]:
        '''
         Generator for file paths in a dir.
         if path given is file, return it
        '''
	#if dir is file, yield it 
        if os.path.isfile(dir):
                yield dir

	#yield every file, gen_files every dir
        for sdir,dirs,files in os.walk(dir):
                for file in files:
                        yield sdir + os.sep + file
                for dir in dirs:
                        for file_path in gen_files(sdir+dir):
                                yield file_path




def execute(cmd :str, globals=None, locals = None, description='krcko'):
	try:
		exec(cmd, globals, locals)
	except SyntaxError as err:
		error_class = err.__class__.__name__
		detail = err.args[0]
		line_number = err.lineno
		logging.error("Execute failed at " + str(line_number) + " with " + detail)
	except Exception as err:
		error_class = err.__class__.__name__
		detail = err.args[0]
		cl, exc, tb = sys.exc_info()
		line_number = traceback.extract_tb(tb)[-1][1]
		logging.error("Execute failed at " + str(line_number) + " with " + detail)
	else:
		return
	raise InterpreterError("%s at line %d of %s: %s" % (error_class, line_number, description, detail))

