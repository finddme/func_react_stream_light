import json
import openai
from typing import List, Dict, Union
from .model_prep_stream import Model
from utils.config import *
from utils.formats import insturctor_format

class Completion(Model):
    def __init__(self, llm):
        super().__init__(Completion)
        self.llm = llm
        self.model=Model(self.llm) # .model_prep
        self.messages = []

    def __call__(self, message, system_prompt):
        self.messages.append({"role": "system", "content":system_prompt})
        self.messages.append({"role": "user", "content": message})
        
        response = self.execute()
        return response
        
    def execute(self):
        response=self.model.__completion__(self.messages)
        return response

class Completion_instructor():
    def __init__(self, llm):
        self.llm = llm
        self.model=Model(self.llm)
        self.messages = []

    def __call__(self, message, system_prompt):
        self.messages.append({"role": "system", "content":system_prompt})
        self.messages.append({"role": "user", "content": message})
        
        response = self.execute()
        return response
        
    def execute(self):        
        response=self.model.__instructor__([self.messages[1]],response_model=insturctor_format)
        return response
    
class Completion_stream(Model):
    def __init__(self, llm):
        super().__init__(Completion)
        self.llm = llm
        self.model=Model(self.llm)
        self.messages = []

    def __call__(self, message, system_prompt):
        self.messages.append({"role": "system", "content":system_prompt})
        self.messages.append({"role": "user", "content": message})
        
        for chunk in self.execute():
            yield chunk
        
    def execute(self):
        for chunk in self.model.__completion__(self.messages):
            yield chunk