import json
import openai
from typing import List, Dict, Union
from .model_prep import Model
from .setting import Setting
from .processor import Processing
from utils.config import *

class FunctionCall(Model):
    def __init__(self, llm, today):
        super().__init__(FunctionCall)
        self.llm = llm
        self.model=Model(self.llm)
        
        self.messages = []
        include_action=["web_search","casual_conversation", "ai_related_search"]
        
        setting=Setting(self.model.model_type,include_action)
        processing=Processing(self.model.model_type)
        self.functions,self.toolprompt=setting()
        self.system_prompt=processing.prompt_processing(self.functions,self.toolprompt, today)
    
    def __call__(self, message, cnt: int = 0):
        self.messages.append({"role": "system", "content": self.system_prompt})
        self.messages.append({"role": "user", "content": message})
        
        try:
            function_call = self.execute()
            return function_call
        except AttributeError as err:
            cnt += 1
            if cnt > 2:
                raise Exception("Error getting function name and arguments!")
            return self.__call__(
                message,
                # f"{self.system_prompt}.\nCALL A FUNCTION!.",
                # self.functions,
                # self.model,
            )
    
    def execute(self):
        # self.model=Model(self.llm)
        print()
        self.model.__funccall__(self.messages,self.functions)
        return self.model.call_res