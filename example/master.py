import os
from subalive import SubAliveMaster

current_folder = os.path.dirname(__file__)

# start subprocess with alive keeping
SubAliveMaster(os.path.join(current_folder, 'slave.py'))

# do our stuff.
# ...
