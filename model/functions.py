basic_function_list = {"web_search":
                                {
                                    "type": "function",
                                    "function": {
                                        "name": "web_search",
                                        "description": "It provides other information via web search, apart from information related to artificial intelligence.",
                                        "parameters": {
                                            "type": "object",
                                            "properties": {
                                                "search_tool": {
                                                    "type": "string",
                                                    "enum": ["korea_news_search", "global_news_search","financial_market_search"],
                                                    "description": """korea_news_search: It provides information related to the current economy, society, and current affairs of Korea.
                                                    global_news_search: It provides information not related to Korea.
                                                    financial_market_search: It provides information related to the financial market.
                                                    """,
                                                },
                                                "search_query": {
                                                    "type": "string",
                                                    "description": """Rephrase the user's question to be more general and easier to answer, while retaining the key points. 
                                                            Rephrase must be written as a fully complete Korean sentence.""",
                                                }
                                            },
                                            "required": ["search_tool","search_query"],
                                        },
                                    },
                                },
                    "casual_conversation":
                                {
                                    "type": "function",
                                    "function": {
                                        "name": "casual_conversation",
                                        "description": """It provides casual conversation. 
                                        For example, it provides conversations such as greetings or emotional empathy, where clear information is not required
                                        """,
                                        "parameters": {
                                            "type": "object",
                                            "properties": {
                                                "user_query": {
                                                    "type": "string",
                                                    "enum": ["casual_conversation"],
                                                    "description":  """Intent of user qeury.""",
                                                },
                                            },
                                            "required": ["user_query"],
                                        },
                                    },
                                },
                    "ai_related_search":{
                                        "type": "function",
                                        "function": {
                                            "name": "ai_related_search",
                                            "description": "It searches for and provides information related to artificial intelligence from sources like arXiv.",
                                            "parameters": {
                                                "type": "object",
                                                "properties": {
                                                    "search_query": {
                                                        "type": "string",
                                                        "description":  """Rephrase given question into a more general form that is easier to answer.  
                                                        Rephrase should contains the core meaning of the user's question. 
                                                        Rephrase must be written as a fully complete Korean sentence.""",
                                                    }
                                                },
                                                "required": ["search_query"],
                                            },
                                        },
                                    },
                    "legal_related_search":{
                                            "type": "function",
                                            "function": {
                                                "name": "legal_related_search",
                                                "description": "It provides legal knowledge.",
                                                "parameters": {
                                                    "type": "object",
                                                    "properties": {
                                                        "search_query": {
                                                            "type": "string",
                                                            "description":  """Rephrase given question into a more general form that is easier to answer. 
                                                            Rephrase must be written as a fully complete Korean sentence.

                                                            ### Example
                                                            Question: I smoked in the alley in front of the company. Is that illegal? There wasn't a sign saying it was a no-smoking area.
                                                            Rephrase: Is it illegal to smoke on a street that doesn't have a no-smoking sign?
                                                            """,
                                                        }
                                                    },
                                                    "required": ["search_query"],
                                                },
                                            },
                                        },
                                  }

claude_function_list = {"web_search":
                                    {
                                        "name": "web_search",
                                        "description": "It provides other information via web search, apart from information related to artificial intelligence.",
                                        "input_schema": {
                                            "type": "object",
                                            "properties": {
                                                "search_tool": {
                                                    "type": "string",
                                                    "enum": ["korea_news_search", "global_news_search", "financial_market_search"],
                                                    "description": """korea_news_search: It provides information related to the current economy, society, and current affairs of Korea.
                                                    global_news_search: It provides information not related to Korea.
                                                    financial_market_search: It provides information related to the financial market.
                                                    """,
                                                },
                                                "search_query": {
                                                    "type": "string",
                                                            "description": """Rephrase the user's question to be more general and easier to answer, while retaining the key points. 
                                                            Rephrase must be written as a fully complete Korean sentence.""",
                                                }
                                            },
                                            "required": ["search_tool","search_query"]
                                        }
                                    },
                        "casual_conversation":
                                        {
                                            "name": "casual_conversation",
                                            "description": """It provides casual conversation. 
                                            For example, it provides conversations such as greetings or emotional empathy, where clear information is not required
                                            """,
                                            "input_schema": {
                                                "type": "object",
                                                "properties": {
                                                    "user_query": {
                                                        "type": "string",
                                                        "enum": ["casual_conversation"],
                                                        "description":  """Intent of user qeury.""",
                                                    }
                                                },
                                                "required": ["user_query"]
                                            }
                                        },
                        "ai_related_search":
                                            {
                                                "name": "ai_related_search",
                                                "description": "It searches for and provides information related to artificial intelligence from sources like arXiv.",
                                                "input_schema": {
                                                    "type": "object",
                                                    "properties": {
                                                        "search_query": {
                                                            "type": "string",
                                                            "description":  """Rephrase given question into a more general form that is easier to answer.  
                                                            Rephrase should contains the core meaning of the user's question. 
                                                            Rephrase must be written as a fully complete Korean sentence.""",
                                                        }
                                                    },
                                                    "required": ["search_query"]
                                                }
                                            },
                        "legal_related_search":
                                            {
                                                "name": "legal_related_search",
                                                "description": "It provides legal knowledge.",
                                                "input_schema": {
                                                    "type": "object",
                                                    "properties": {
                                                        "search_query": {
                                                            "type": "string",
                                                            "description":  """Rephrase given question into a more general form that is easier to answer. 
                                                            Rephrase must be written as a fully complete Korean sentence.

                                                            ### Example
                                                            Question: I smoked in the alley in front of the company. Is that illegal? There wasn't a sign saying it was a no-smoking area.
                                                            Rephrase: Is it illegal to smoke on a street that doesn't have a no-smoking sign?
                                                            """,
                                                        }
                                                    },
                                                    "required": ["search_query"]
                                                }
                                            }
                        }

llama_function_list = {"web_search":
                                {
                                    "name": "web_search",
                                    "description": "It provides other information via web search, apart from information related to artificial intelligence.",
                                    "parameters": {
                                        "type": "object",
                                        "properties": {
                                            "search_tool": {
                                                "type": "string",
                                                "enum": ["korea_news_search", "global_news_search", "financial_market_search"],
                                                "description": """korea_news_search: It provides information related to the current economy, society, and current affairs of Korea.
                                                    global_news_search: It provides information not related to Korea.
                                                    financial_market_search: It provides information related to the financial market.
                                                    """,
                                            },
                                                "search_query": {
                                                    "type": "string",
                                                            "description": """Rephrase the user's question to be more general and easier to answer, while retaining the key points. 
                                                            Rephrase must be written as a fully complete Korean sentence.""",
                                                }
                                        },
                                        "required": ["search_tool","search_query"]
                                    },
                                },
                    "casual_conversation":
                                    {
                                        "name": "casual_conversation",
                                        "description": """It provides casual conversation. 
                                        For example, it provides conversations such as greetings or emotional empathy, where clear information is not required.
                                        """,
                                        "parameters": {
                                            "type": "object",
                                            "properties": {
                                                "user_query": {
                                                    "type": "string",
                                                    "enum": ["casual_conversation"],
                                                    "description":  """Intent of user qeury.""",
                                                }
                                            },
                                            "required": ["user_query"]
                                        },
                                    },
                    "ai_related_search":
                                        {
                                            "name": "ai_related_search",
                                            "description": "It searches for and provides information related to artificial intelligence from sources like arXiv.",
                                            "parameters": {
                                                "type": "object",
                                                "properties": {
                                                    "search_query": {
                                                        "type": "string",
                                                        "description":  """Rephrase given question into a more general form that is easier to answer.  
                                                        Rephrase should contains the core meaning of the user's question. 
                                                        Rephrase must be written as a fully complete Korean sentence.""",
                                                    }
                                                },
                                                "required": ["search_query"]
                                            },
                                        },
                    "legal_related_search":
                                        {
                                            "name": "legal_related_search",
                                            "description": "It provides legal knowledge.",
                                            "parameters": {
                                                "type": "object",
                                                "properties": {
                                                    "search_query": {
                                                        "type": "string",
                                                                "description":  """Rephrase given question into a more general form that is easier to answer. 
                                                                Rephrase must be written as a fully complete Korean sentence.

                                                                ### Example
                                                                Question: I smoked in the alley in front of the company. Is that illegal? There wasn't a sign saying it was a no-smoking area.
                                                                Rephrase: Is it illegal to smoke on a street that doesn't have a no-smoking sign?
                                                                """,
                                                    }
                                                },
                                                "required": ["search_query"]
                                            },
                                        }
                  }
