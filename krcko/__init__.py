import os
import sys


#importing module from parent dir
curr = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(curr)
sys.path.insert(0, parent)



