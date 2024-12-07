from utils.config import *
from utils.map import *
from model.prompt import *
from model.function_calling import FunctionCall
from model.completion import Completion_stream
from utils.logging_wrapper import LoggingWrapper
from datetime import datetime

logger = LoggingWrapper('ayaan_logger')
logger.add_file_handler("info")
logger.add_stream_handler("error")

class Node:
    def __init__(self,args):
        global action_map
        global system_prompt
        global normal_completion_prompt
        global llm_map
        global log_system

        self.args=args

        self.llm=llm_map[self.args.llm]
        # llm=llm_map["together"]
        # self.fc = FunctionCall(self.llm)
        
        model_type = str(type(self.llm))
        self.model_type = model_type[model_type.find("'")+1:model_type.rfind("'")]

        self.final_generate=""

    def function_call_node(self,query):
        today = datetime.today().strftime('%d %B %Y')

        self.fc = FunctionCall(self.llm, today)
        fc_res=self.fc(query)

        logger.info(f"Model Type: {self.model_type}")
        
        self.log_list=[]
        logger.add_list_handler(self.log_list,"info")

        logger.info(f"User Query: {query}")
        logger.info(f"Funtion Call result: {fc_res}")

        return fc_res

    def action_node(self,action):
        action_res=[]
        actions = list(map(lambda x: x['function'], action))
        for a in action:
            if a["function"] !="casual_conversation":
                act_function=action_map[a["function"]]
                action_res.append(act_function(a["search_query"]))
        
        return action_res

    def generate_node(self,query,action,observation):
        self.completion=Completion_stream(self.llm)
        
        try:
            for a in action:
                if a != "casual_conversation":
                    prompt=system_prompt.format(observation)
                    # prompt=reflection_prompt.format(query,observation)
                else:
                    if self.model_type=="anthropic.Anthropic":
                        query=f"User's question: {query} \n{normal_completion_prompt}"
                    prompt=normal_completion_prompt

            # response=self.completion(query,prompt)
            for chunk in self.completion(query,prompt):
                self.final_generate+=chunk
                yield f"{chunk}"

            # response+=additional_phrase[a]             
        
            logger.info(f"Observation: {observation}")
            logger.info(f"Response: {self.final_generate}")

        except Exception  as e:
            for chunk in self.completion(query,normal_completion_prompt):
                self.final_generate+=chunk
                yield f"{chunk}"
            # response=self.completion(query,normal_completion_prompt)

            logger.info(f"////////////\n")
            logger.info(f"Exception: {e}")
            logger.info(f"Response: {self.final_generate}")
            logger.info(f"////////////\n")
        
        logger.info(f"==============================================================\n")

        # return response, self.log_list