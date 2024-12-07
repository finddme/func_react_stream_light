from langgraph.graph import END, StateGraph, START
from .node import Node
from typing_extensions import TypedDict
from typing import List
from pydantic import BaseModel, Field,model_serializer
from pydantic import TypeAdapter
from typing import List
from utils.formats import GraphState
# from db.db_management import ai_db_reload_auto
import asyncio


class RUN:
    def __init__(self,args):
        self.args=args
        self.node=Node(self.args)
        # if args.ai_db_restore=="yes":
        #     ai_db_reload_auto()

    def run(self,user_input):
        action=self.node.function_call_node(user_input)
        observation=self.node.action_node(action)

        action_str=""
        for a in action:
            action_str+=a["function"]
            yield f"**[Action: {action_str}]**\n\n"

        for chunk in self.node.generate_node(user_input,action,observation):
            yield f"{chunk}"

        yield f"\n\n{'='*80}\n\n"

        log=str("\n".join(self.node.log_list[:-2])).replace('\\n','\n')
        yield f"""**Inference LOG**:\n\n ```log\n{log}```
        """
