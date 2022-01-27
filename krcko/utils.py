from typing import Iterator
import os


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
                        yield sdir + file
                for dir in dirs:
                        for file_path in gen_files(sdir+dir+os.sep):
                                yield file_path

