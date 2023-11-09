from llama_index import StorageContext, load_index_from_storage


storage_context = StorageContext.from_defaults(persist_dir="./storage")
index = load_index_from_storage(storage_context=storage_context)

query_engine = index.as_query_engine()
response = query_engine.query("What is the criteria for selecting patients?")