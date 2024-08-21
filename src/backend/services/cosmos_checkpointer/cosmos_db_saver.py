from contextlib import contextmanager
from typing import Any, Dict, Iterator, Optional, Sequence, Tuple

from langchain_core.runnables import RunnableConfig
from azure.cosmos import CosmosClient, exceptions
from typing import Optional, Dict, Any, Iterator, Sequence, Tuple
import json

from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    ChannelVersions,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
    get_checkpoint_id,
)


class CosmosDBSaver(BaseCheckpointSaver):
    """A checkpoint saver that stores checkpoints in a CosmosDB SQL database."""

    client: CosmosClient

    def __init__(
        self,
        client: CosmosClient,
        db_name: str,
        container_name: str,
        write_container_name: str,
    ) -> None:
        super().__init__()
        self.client = client
        self.db = self.client.get_database_client(db_name)
        self.container = self.db.get_container_client(container_name)
        self.write_container = self.db.get_container_client(write_container_name)

    @classmethod
    @contextmanager
    def from_conn_info(
        cls, *, url: str, key: str, db_name: str, container_name: str, write_container_name: str
    ) -> Iterator["CosmosDBSaver"]:
        client = None
        try:
            client = CosmosClient(url=url, credential=key)
            yield CosmosDBSaver(client, db_name, container_name, write_container_name)
        finally:
            if client:
                client = None

    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        """Get a checkpoint tuple from the database.

        This method retrieves a checkpoint tuple from the CosmosDB database based on the
        provided config. If the config contains a "checkpoint_id" key, the checkpoint with
        the matching thread ID and checkpoint ID is retrieved. Otherwise, the latest checkpoint
        for the given thread ID is retrieved.

        Args:
            config (RunnableConfig): The config to use for retrieving the checkpoint.

        Returns:
            Optional[CheckpointTuple]: The retrieved checkpoint tuple, or None if no matching checkpoint was found.
        """
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
       
        if checkpoint_id := get_checkpoint_id(config):
           query = f"SELECT * FROM c WHERE c.thread_id = '{thread_id}' AND c.checkpoint_ns = '{checkpoint_ns}' AND c.id = '{checkpoint_id}'"
        else:
            query = f"SELECT * FROM c WHERE c.thread_id = '{thread_id}' AND c.checkpoint_ns = '{checkpoint_ns}' ORDER BY c.id DESC"

        try:
            result = list(self.container.query_items(query=query, enable_cross_partition_query=True))
            if result:
                doc = result[0]
                config_values = {
                    "thread_id": thread_id,
                    "checkpoint_ns": checkpoint_ns,
                    "checkpoint_id": doc["checkpoint_id"],
                }
                checkpoint = self.serde.loads_typed((doc["type"], doc["checkpoint"]))
                serialized_writes_query = f"SELECT * FROM c WHERE c.thread_id = '{thread_id}' AND c.checkpoint_ns = '{checkpoint_ns}' AND c.id = '{doc['checkpoint_id']}'"
                serialized_writes = list(self.write_container.query_items(query=serialized_writes_query, enable_cross_partition_query=True))
                pending_writes = [
                    (
                        write_doc["task_id"],
                        write_doc["channel"],
                        self.serde.loads_typed((write_doc["type"], write_doc["value"])),
                    )
                    for write_doc in serialized_writes
                ]
                return CheckpointTuple(
                    {"configurable": config_values},
                    checkpoint,
                    self.serde.loads(doc["metadata"]),
                    (
                        {
                            "configurable": {
                                "thread_id": thread_id,
                                "checkpoint_ns": checkpoint_ns,
                                "checkpoint_id": doc["parent_checkpoint_id"],
                            }
                        }
                        if doc.get("parent_checkpoint_id")
                        else None
                    ),
                    pending_writes,
                )
        except exceptions.CosmosHttpResponseError as e:
            print(f"An error occurred: {e}")
            return None



    def list(
        self,
        config: Optional[RunnableConfig],
        *,
        filter: Optional[Dict[str, Any]] = None,
        before: Optional[RunnableConfig] = None,
        limit: Optional[int] = None,
    ) -> Iterator[CheckpointTuple]:
        """List checkpoints from the database.

        This method retrieves a list of checkpoint tuples from the CosmosDB database based
        on the provided config. The checkpoints are ordered by checkpoint ID in descending order (newest first).

        Args:
            config (RunnableConfig): The config to use for listing the checkpoints.
            filter (Optional[Dict[str, Any]]): Additional filtering criteria for metadata. Defaults to None.
            before (Optional[RunnableConfig]): If provided, only checkpoints before the specified checkpoint ID are returned. Defaults to None.
            limit (Optional[int]): The maximum number of checkpoints to return. Defaults to None.

        Yields:
            Iterator[CheckpointTuple]: An iterator of checkpoint tuples.
        """
        query = "SELECT * FROM c WHERE 1=1"
        if config is not None:
            thread_id = config["configurable"]["thread_id"]
            checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
            query += f" AND c.thread_id = '{thread_id}' AND c.checkpoint_ns = '{checkpoint_ns}'"

        if filter:
            for key, value in filter.items():
                query += f" AND c.metadata.{key} = '{value}'"

        if before is not None:
            before_checkpoint_id = before["configurable"]["checkpoint_id"]
            query += f" AND c.id < '{before_checkpoint_id}'"

        query += " ORDER BY c.id DESC"

        if limit is not None:
            query += f" OFFSET 0 LIMIT {limit}"

        try:
            result = list(self.container.query_items(query=query, enable_cross_partition_query=True))
            for doc in result:
                checkpoint = self.serde.loads_typed((doc["type"], doc["checkpoint"]))
                yield CheckpointTuple(
                    {
                        "configurable": {
                            "thread_id": doc["thread_id"],
                            "checkpoint_ns": doc["checkpoint_ns"],
                            "checkpoint_id": doc["checkpoint_id"],
                        }
                    },
                    checkpoint,
                    self.serde.loads(doc["metadata"]),
                    (
                        {
                            "configurable": {
                                "thread_id": doc["thread_id"],
                                "checkpoint_ns": doc["checkpoint_ns"],
                                "checkpoint_id": doc["parent_checkpoint_id"],
                            }
                        }
                        if doc.get("parent_checkpoint_id")
                        else None
                    ),
                )
        except exceptions.CosmosHttpResponseError as e:
            print(f"An error occurred: {e}")


    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        """Save a checkpoint to the database.

        This method saves a checkpoint to the CosmosDB database. The checkpoint is associated
        with the provided config and its parent config (if any).

        Args:
            config (RunnableConfig): The config to associate with the checkpoint.
            checkpoint (Checkpoint): The checkpoint to save.
            metadata (CheckpointMetadata): Additional metadata to save with the checkpoint.
            new_versions (ChannelVersions): New channel versions as of this write.

        Returns:
            RunnableConfig: Updated configuration after storing the checkpoint.
        """
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"]["checkpoint_ns"]
        checkpoint_id = checkpoint["id"]
        type_, serialized_checkpoint = self.serde.dumps_typed(checkpoint)
        decoded_string = serialized_checkpoint.decode('utf-8')
        checkpoint_json = json.loads(decoded_string)
        serialized_metadata = self.serde.dumps(metadata)
        decoded_string = serialized_metadata.decode('utf-8')
        metadata_json = json.loads(decoded_string)

        doc = {
            "id":checkpoint_id,
            "thread_id": thread_id,
            "checkpoint_ns": checkpoint_ns,
            "checkpoint_id": checkpoint_id,
            "parent_checkpoint_id": config["configurable"].get("checkpoint_id"),
            "type": type_,
            "checkpoint": json.dumps(checkpoint_json),
            "metadata":json.dumps(metadata_json) 
        }

        try:
            
            self.container.upsert_item(doc)
            return {
                "configurable": {
                    "thread_id": thread_id,
                    "checkpoint_ns": checkpoint_ns,
                    "checkpoint_id": checkpoint_id,
                }
            }
        except exceptions.CosmosHttpResponseError as e:
            print(f"An error occurred: {e}")
            return config 

    def put_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[Tuple[str, Any]],
        task_id: str,
    ) -> None:
        """Store intermediate writes linked to a checkpoint.

        This method saves intermediate writes associated with a checkpoint to the CosmosDB database.

        Args:
            config (RunnableConfig): Configuration of the related checkpoint.
            writes (Sequence[Tuple[str, Any]]): List of writes to store, each as (channel, value) pair.
            task_id (str): Identifier for the task creating the writes.
        """
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"]["checkpoint_ns"]
        checkpoint_id = config["configurable"]["checkpoint_id"]
        operations = []
        for idx, (channel, value) in enumerate(writes):
            type_, serialized_value = self.serde.dumps_typed(value)
            decoded_string = serialized_value.decode('utf-8')
            value_json = json.loads(decoded_string)
        
            doc = {
                "id":checkpoint_id,
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": checkpoint_id,
                "task_id": task_id,
                "idx": idx,
                "channel": channel,
                "type": type_,
                "value": json.dumps(value_json),
            }
            operations.append(doc)

        try:
            for operation in operations:
                self.write_container.upsert_item(operation)
        except exceptions.CosmosHttpResponseError as e:
            print(f"An error occurred: {e}")


