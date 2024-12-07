from .prompt import *
from .processor import *
import re
import httpx
import json
from utils.config import *
from .processor import Processing
from together import Together

class Model:
    def __init__(self,llm):
        global basic_functions
        global claude_functions
        global system_prompt
        self.llm=llm
        self.call_res=[]
        self.mode={"anthropic.Anthropic":self.claude_cpl,
                  "together.client.Together":self.together_cpl}
        model_type = str(type(self.llm))
        self.model_type = model_type[model_type.find("'")+1:model_type.rfind("'")]
        # print(f"--- {self.model_type} ---")
        # self.processing=Processing(self.model_type)
        
    def __completion__(self,messages):
        model=self.mode[self.model_type]
        normal_completion=model(messages=messages)
        return normal_completion

    def __funccall__(self,messages,functions):
        model=self.mode[self.model_type]
        response=model(messages=messages,functions=functions)
        self.processing=Processing(self.model_type)
        self.processing.postprocessing(messages,response)
        self.call_res=self.processing.call_res
    
    def __instructor__(self,messages,response_model):
        model=self.mode[self.model_type]
        response=model(messages,response_model=response_model)
        return response
    
    def claude_cpl(self,messages,functions=None):
        if functions:
            response = self.llm.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=2048,
                tools=functions,
                messages=[messages[1]]
            )
        else:
            response = self.llm.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=2048,
                # system=messages[0]["content"],
                messages=[messages[1]]
            )
        response_message=response.content
        if functions:
            return response_message
        else: return response_message[0].text

    def together_cpl(self,messages,functions=None,response_model=None):
        if response_model:
            max_retries=25
            for attempt in range(max_retries):
                try:
                    llm_client = Instructor_Definition.together_inst()
                    response = llm_client.chat.completions.create(
                            model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                            response_model=response_model,
                            messages=messages,
                            # max_retries=Retrying(
                            #     stop=stop_after_attempt(2),  
                            #     wait=wait_fixed(1),  
                            # ),
                        )
                    return response
                    
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    else: continue
        elif functions:
            llm = Together(api_key=Together_API_KEY)
            response = llm.chat.completions.create(
                model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                messages=messages,
                temperature=0,
                top_p=0.7,
                top_k=50,
                repetition_penalty=1,
                stop=["<|eot_id|>","<|eom_id|>"],
            )
            response_message = response.choices[0].message
            return response_message
        else:
            llm_client=self.llm
            response = llm_client.chat.completions.create(
                model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                messages=messages,
                # temperature=0,
                # top_p=0.7,
                # top_k=50,
                # repetition_penalty=1,
                # stop=["<|eot_id|>","<|eom_id|>"],
                )

            response_message = response.choices[0].message
            return response_message.content