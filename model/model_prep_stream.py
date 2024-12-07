from .prompt import *
from .processor import *
import re
import httpx
import json
from utils.config import *
from .processor import Processing

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
            return response.content
        else:
            with self.llm.messages.stream(
                max_tokens=1024,
                messages=[messages[1]],
                model="claude-3-5-sonnet-20241022",
            ) as stream:
                    for text in stream.text_stream:
                        if text is not None:
                            yield text

    def together_cpl(self,messages,functions=None,response_model=None):
        print("together_cpl")
        print(messages,functions,response_model)
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
            print("functions!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            response = self.llm.chat.completions.create(
                model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                messages=messages,
                temperature=0,
                top_p=0.7,
                top_k=50,
                repetition_penalty=1,
                stop=["<|eot_id|>","<|eom_id|>"],
            )
            
            return response.choices[0].message
        else:
            stream = self.llm.chat.completions.create(
                model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                messages=messages,
                # max_tokens=512,
                temperature=0.7,
                top_p=0.7,
                top_k=50,
                repetition_penalty=1,
                stop=["<|eot_id|>","<|eom_id|>"],
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
