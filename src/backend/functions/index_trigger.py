
import azure.functions as func
import logging

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from langchain_openai import AzureOpenAIEmbeddings
from helper.azure_config import AzureConfig
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_text_splitters import CharacterTextSplitter

indexTriggerBp = func.Blueprint()


# can container be retrieved from the environment variable?
@indexTriggerBp.blob_trigger(arg_name="myblob", path="%AZURE_BLOB_STORAGE_INPUT_CONTAINER%",
                               connection="AZURE_BLOB_CONN_STR") 
def runIndexTrigger(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob"
                f"Name: {myblob.name}"
                f"Blob Size: {myblob.length} bytes")
    
    config = AzureConfig()
    credential = DefaultAzureCredential()
        
    embeddings: AzureOpenAIEmbeddings = AzureOpenAIEmbeddings(
        azure_deployment=config.azure_emdedding_deployment,
        openai_api_version=config.azure_openai_api_version,
        azure_endpoint=config.azure_endpoint,
        api_key=config.azure_openai_api_key,
    )

    vector_store: AzureSearch = AzureSearch(
        azure_search_endpoint=config.vector_store_address,
        azure_search_key=config.vector_store_password,
        index_name=config.index_name,
        embedding_function=embeddings.embed_query,
    )
    blob_name = myblob.name
    filename = blob_name.split('/') 
    
    blob_service_client = BlobServiceClient(account_url=config.blob_storage_url, credential=credential)
    blob_client = blob_service_client.get_blob_client(container=filename[0], blob=filename[1])
    downloader = blob_client.download_blob(max_concurrency=1, encoding='UTF-8')
    blob_text = downloader.readall()

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    splits = text_splitter.split_text(blob_text)
    docs =  text_splitter.create_documents(splits)
    vector_store.add_documents(documents=docs)

    # Get the destination blob client
    destination_blob_client = blob_service_client.get_blob_client(container=config.output_container_name, blob=filename[1])

    # Copy the blob to the new location
    destination_blob_client.start_copy_from_url(myblob.uri)

    # Delete the source blob
    blob_client.delete_blob()

