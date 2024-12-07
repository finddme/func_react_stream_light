import json
import openai
from typing import List, Dict, Union
from .model_prep import Model
from utils.config import *
from utils.map import fc_mode
from .functions import *

class Setting:
    def __init__(self, model_type, defined_action):
        global fc_mode
        global basic_function_list
        global claude_function_list
        global llama_function_list
        self.defined_action=defined_action
        self.function_list,self.toolprompt=fc_mode[model_type]
        self.functions=[]
    def __call__(self):
        self.set_functions()
        return self.functions, self.toolprompt
    def set_functions(self):
        for ac in self.defined_action:
            self.functions.append(self.function_list[ac])