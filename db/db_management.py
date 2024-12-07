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
from tenacity import retry, stop_after_attempt, wait_exponential
import time

known_class=DB["known_class"]
weaviate_url=DB["weaviate_url"]

def set_db_client():
    client = weaviate.Client(
        url=weaviate_url,
        timeout_config=(5, 60)
    )
    return client

client=set_db_client()

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

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=300))
def save_weaviate(class_name, vectorizing_element, chunks, start_index=0):
    # start_index 지정 가능!!
    global client
    client.batch.configure(batch_size=10, timeout_retries=100, dynamic=False)
    
    # 시작 인덱스 확인 메시지
    total_chunks = len(chunks)
    remaining_chunks = total_chunks - start_index
    print(f"--- Save DB (remaining data size: {remaining_chunks}, starting from index: {start_index}) ---")
    
    # 실패한 청크들을 저장할 리스트
    failed_chunks = []
    
    with client.batch as batch:
        for i in range(start_index, len(chunks)):
            if i % 10 == 0:
                print(f"{i}/{len(chunks)}")
            
            chunk = chunks[i]
            try:
                vector = get_embedding_openai(chunk[vectorizing_element])
                
                # Retry mechanism with exponential backoff
                for attempt in range(1, 4):
                    try:
                        batch.add_data_object(data_object=chunk, class_name=class_name, vector=vector)
                        time.sleep(0.1)
                        break
                    except Exception as e:
                        if attempt < 3:
                            print(f"[ERROR] Batch ReadTimeout Exception occurred! Retrying in {2 ** attempt}s. [{attempt}/3]")
                            time.sleep(2 ** attempt + random.uniform(0, 1))
                        else:
                            print(f"[ERROR] Failed to add chunk at index {i} after 3 retries. Adding to failed chunks list.")
                            failed_chunks.append(i)
                            
            except Exception as e:
                print(f"[ERROR] Failed to process chunk at index {i}: {str(e)}")
                failed_chunks.append(i)
    
    if failed_chunks:
        print(f"--- Save DB PARTIALLY DONE ---")
        print(f"Failed chunks at indices: {failed_chunks}")
        return failed_chunks
    else:
        print("--- Save DB COMPLETED SUCCESSFULLY ---")
        return None

def retry_failed_chunks(class_name, vectorizing_element, chunks, failed_indices):
    """실패한 청크들을 재시도하는 함수"""
    if not failed_indices:
        return
        
    print(f"Retrying {len(failed_indices)} failed chunks...")
    failed_chunks = [chunks[i] for i in failed_indices]
    return save_weaviate(class_name, vectorizing_element, failed_chunks, 0)

# 메인 실행 부분
def main_save_process(class_name, vectorizing_element, chunks):
    # 첫 시도
    failed_indices = save_weaviate(class_name, vectorizing_element, chunks)
    
    # 실패한 청크들이 있다면 재시도
    retry_count = 1
    while failed_indices and retry_count <= 3:
        print(f"\nRetry attempt {retry_count} for failed chunks")
        failed_indices = retry_failed_chunks(class_name, vectorizing_element, chunks, failed_indices)
        retry_count += 1
    
    if failed_indices:
        print(f"\nWARNING: Some chunks still failed after all retries. Failed indices: {failed_indices}")
    else:
        print("\nAll chunks successfully saved!")

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
    main_save_process(class_name,vectorizing_element,chunks)

def ai_db_reload_auto():
    global client
    ai_weaviate_class="b_with_title"
    del_weaviate_class(ai_weaviate_class)
    chunks=crawling_and_processing()
    create_weaviate(ai_weaviate_class)
    vectorizing_element="text"
    main_save_process(ai_weaviate_class, vectorizing_element, chunks)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--class-name', type=str, 
                        choices=["law",
                                "law_consult"], 
                        default='law_consult')
    parser.add_argument('--data-path', type=str, 
                        choices=["/workspace/chat_aws/law_final_data.json", 
                                "/workspace/chat_aws/extract_str_laws_consult.json"], 
                        default="/workspace/chat_aws/extract_str_laws_consult.json")
    parser.add_argument('--vectorizing-element', type=str, 
                        choices=["law_content",
                                "title"],
                        default='title')

    args = parser.parse_args()
    try:
        db_processing(args.class_name,args.data_path,args.vectorizing_element)
    except SystemExit:
        print("Process terminated due to critical errors.")
        raise  
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)
