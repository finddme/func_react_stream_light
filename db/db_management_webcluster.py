import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.models import get_embedding_openai
from utils.config import *
import weaviate
import openai
import os
import argparse
import json
from db.data_processing import crawling_and_processing

known_class=DB["known_class"]
weaviate_url_webcluster=DB["weaviate_url_webcluster"]
weaviate_auth=DB["weaviate_auth"]

def set_db_client_webcluster():
    client = weaviate.Client(
        url=weaviate_url_webcluster,
        auth_client_secret=weaviate.auth.AuthApiKey(api_key=weaviate_auth),
    )
    return client

client=set_db_client_webcluster()

def db_class_sync_check():
    global client
    global known_class
    print("--- Synchronizing vecotr DB ---")
    db_classes=list(map(lambda x : x["class"].lower(), client.schema.get()["classes"]))
    for dc in db_classes:
        if dc not in known_class:
            print(f"--- delte db class {dc} ---")
            client.schema.delete_class(dc)
            
def db_class_check():
    global client
    print("--- DB class check ---")
    db_classes=list(map(lambda x : x["class"].lower(), client.schema.get()["classes"]))
    return db_classes

def del_weaviate_class(class_name):
    global client
    print(f"--- delte db class {class_name} ---")
    client.schema.delete_class(class_name)
        
def create_weaviate(class_name):
    global client
    print("--- Create DB ---")
    class_obj = {
        "class": class_name,
        "vectorizer": "none",
    }
    client.schema.create_class(class_obj)

def save_weaviate(class_name,vectorizing_element,chunks):
    global client
    client.batch.configure(batch_size=100)
    print(f"--- Save DB (data size: {len(chunks)}) ---")
    with client.batch as batch:
        for i, chunk in enumerate(chunks):
            if i%10==0:print(f"{i}/{len(chunks)}")
            vector = get_embedding_openai(chunk[vectorizing_element])
            batch.add_data_object(data_object=chunk, class_name=class_name, vector=vector)
    print("--- Save DB DONE ---")

def load_json(data_path):
    print("--- Load Data ---")
    with open(data_path) as f:
        data = json.load(f)
    return data

def db_processing(class_name,data_path,vectorizing_element):
    db_class_sync_check()
    db_class_list=db_class_check()
    if class_name in db_class_list: del_weaviate_class(class_name)
    create_weaviate(class_name)
    chunks=load_json(data_path)
    save_weaviate(class_name,vectorizing_element,chunks)

def ai_db_reload_auto():
    global client
    ai_weaviate_class="b_with_title"
    del_weaviate_class(ai_weaviate_class)
    chunks=crawling_and_processing()
    create_weaviate(ai_weaviate_class)
    vectorizing_element="text"
    save_weaviate(ai_weaviate_class, vectorizing_element, chunks)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--class-name', type=str, 
                        choices=["law",
                                "law_consult"], 
                        default='law_consult')
    parser.add_argument('--data-path', type=str, 
                        choices=["/workspace/.gen/Crawler/Law/law_final_data.json", 
                                "/workspace/.gen/Crawler/Law/law_consult_crawling/extract_str_laws_consult.json"], 
                        default="/workspace/.gen/Crawler/Law/law_consult_crawling/extract_str_laws_consult.json")
    parser.add_argument('--vectorizing-element', type=str, 
                        choices=["law_content",
                                "title"],
                        default='title')

    args = parser.parse_args()
    db_processing(args.class_name,args.data_path,args.vectorizing_element)
    db_processing("law",
                    "/workspace/.gen/Crawler/Law/law_final_data.json",
                    "law_content")
    ai_db_reload_auto()
