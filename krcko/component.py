from recordclass import recordclass
import json 
from typing import Dict,Any
import logging
import sys

import definitions as defs

PATTERNS_PATH = defs.ROOT_DIR_PATH + "/res/patterns/"



def gen_pattern(comp_name : str, comp_fields : dict, patterns_path :str = None) -> None:
        '''
         Generates new component pattern dict, and saves it into a JSON file.
         If json file with same component name already exists, it will be replaced.

         params:
                comp_name : component pattern name, multiple patterns with same name aren't allowed
                comp_fields : dictionary containing component pattern fields
            optional:
                patterns_pat : path to dir where patterns are stored

	 returns:
		(instance,factory)
        '''

        if not patterns_path:
                patterns_path = PATTERNS_PATH

	#fill up the pattern dict
        pat: Dict[str,Any] = {}
        pat['component'] = comp_name
        pat['fields']    = comp_fields

	#parse dict to json and save it into a file
        try:
                with open(patterns_path+comp_name+".json","w") as pat_file:
                      pat_file.write(json.dumps(pat))
        except IOError as e:
                logging.error("IOerror : " + str(e))
                pass


def hook_component(d : dict) -> Any:
        '''
         Function passed to json.loads to convert decoded dict to recordclass.

         params:
                dict : decoded dictionary from json.loads()
        '''

        if 'fields' in d.keys() and 'component' in d.keys():
                fields: dict   = d['fields']
                component: str = d['component']
        else:
                logging.error("Invalid pattern format: "+ str(d))
                return d
        rc = recordclass(component, fields.keys())
        return (rc(*fields.values()),rc)



def load_component(path :str) -> recordclass:
        '''
         Loads JSON component/pattern file into recordclass.

         params:
                path

        '''

        try:

                # object_hook is an optional function that will be called with the result
                # of any object literal decoded (a dict).
                # The return value of object_hook will be used instead of the dict.
                # Because object_hook gets called every time a dict gets decoded in JSON
                # file, starting from the innermost and going up, check if decoded dict contains
                # 'component' key.
                with open(path,"r") as pat_file:
                        return json.loads(pat_file.read(),\
                        object_hook= lambda d : hook_component(d) if "component" in d  else d)

        except IOError as e:
                logging.error("IO error : "+ str(e))
                return None



def create_component(comp_name :str, fields :Dict[str,Any]) -> recordclass:
        '''
         Creates new recordclass instance

         params:
                comp_name
                fields
                values
        '''

        comp = recordclass(comp_name,fields.keys())
        return (comp(*fields.values()),comp)

def define_component(comp_name :str, fields :list) -> recordclass:
        '''
         Defines new recordclass

         params:
                comp_name
                fields
        '''

        return recordclass(comp_name,fields)




