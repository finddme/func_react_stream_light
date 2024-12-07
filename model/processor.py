import re
import httpx
import json

class Processing:
    def __init__(self,model_type):
        self.model_type=model_type
        self.call_res=[]

    def prompt_processing(self,functions,toolprompt,today):
        tool_info_inject=""
        names=""
        for lf in functions:
            if "name" in list(lf.keys()):
                names+=f"""{lf["name"]},"""
            else:
                names+=f"""{lf["function"]["name"]},"""   
        toolprompt=toolprompt.format(names,today,functions)
        return toolprompt
    def postprocessing(self,user_messages,response_message):
        fn_pattern=r'<function=(\w+)>'
        pattern1=r'search_tool.*?:\s*"?([^",\s]+)"?'
        pattern2=r'search_query.*?:\s*"?([^",]+)"?'
        if self.model_type=="anthropic.Anthropic":
            for rm in response_message:
                if rm.type=="tool_use":
                    func_args=list(rm.input.values())
                    if len(func_args)>1:
                        self.call_res.append({"function":func_args[0], "search_query":func_args[1]})
                    else: 
                        if rm.name=="casual_conversation":
                            self.call_res.append({"function":rm.name, "search_query":list(user_messages[1].values())[1]})
                        else:
                            self.call_res.append({"function":rm.name, "search_query":func_args[0]})
            # self.call_res=list({cr['search_query']: cr for cr in self.call_res}.values())
        else:
            function_call= response_message.tool_calls
            if len(function_call)==0:
                print("len(function_call)==0",response_message.model_dump()["content"])
                content= response_message.model_dump()["content"]
                
                name_match=re.search(fn_pattern, content)
                match1 = re.search(pattern1, content)
                match2 = re.search(pattern2, content)
        
                function_name = name_match.group(1)
                search_query=match2.group(1)
        
                if match1:
                    search_tool = match1.group(1)
                    self.call_res.append({"function":search_tool, "search_query":search_query})
                else: self.call_res.append({"function":function_name, "search_query":search_query})
            else:
                for fc_res in function_call:
                    # func_args=list(json.loads(fc_res.function.arguments).values())
                    func_args=json.loads(fc_res.function.arguments)
                    if len(func_args)>1:
                        self.call_res.append({"function":func_args["search_tool"], "search_query":func_args["search_query"]})
                    else:
                        if fc_res.function.name=="casual_conversation":
                            self.call_res.append({"function":fc_res.function.name, "search_query":list(user_messages[1].values())[1]})
                        else:
                            self.call_res.append({"function":fc_res.function.name, "search_query":list(func_args.values())[0]})
                            # self.call_res.append({"function":fc_res.function.name, "search_query":func_args[0]})
        self.call_res=list({cr['search_query']: cr for cr in self.call_res}.values())