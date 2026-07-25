"""The core data processing module.

This module is responsible for taking raw data sources (files, URLs, text)
and converting them into a standardized, clean Markdown format using robust
third-party libraries like LangChain and Unstructured.
"""

import asyncio
import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Union

from langchain_community.document_loaders import (UnstructuredFileLoader,
                                                  UnstructuredURLLoader)
from starlette.datastructures import UploadFile

from app.schemas.source import ProcessedSource

logger = logging.getLogger(__name__)


async def process_source_to_markdown(source: Union[UploadFile, str]) -> ProcessedSource:
    """Processes a given source and converts it to clean Markdown.

    This function uses Unstructured loaders to handle various document types,
    extracts the content and metadata, and returns it in a standardized format.

    Args:
        source: The data source, which can be a FastAPI UploadFile object or a string
                (representing a URL or raw text).

    Returns:
        A ProcessedSource object containing the content in Markdown format and
        associated metadata.
    """
    logger.info(f"Processing source of type: {type(source)}")
    documents = []

    try:
        if isinstance(source, UploadFile):
            temp_dir = tempfile.mkdtemp()
            temp_path = os.path.join(temp_dir, source.filename)
            try:
                # Asynchronously read the file content to handle the upload stream correctly.
                content = await source.read()
                logger.info(
                    f"Processing uploaded file: {source.filename}, size: {len(content)} bytes."
                )

                if not content:
                    logger.warning(f"Uploaded file '{source.filename}' is empty.")
                    documents = []
                else:
                    with open(temp_path, "wb") as buffer:
                        buffer.write(content)
                    # Now, use the path with the loader
                    loader = UnstructuredFileLoader(
                        file_path=temp_path, mode="elements"
                    )
                    documents = await asyncio.to_thread(loader.load)

                logger.info(
                    f"Unstructured loader returned {len(documents)} documents for uploaded file."
                )
            finally:
                shutil.rmtree(temp_dir)  # Clean up the directory and its contents

        elif isinstance(source, str):
            if source.strip().startswith(("http://", "https://")):
                loader = UnstructuredURLLoader(urls=[source.strip()], mode="elements")
                documents = await asyncio.to_thread(loader.load)
            else:
                # For raw text, we also write to a temp file for Unstructured to process.
                tmp_file_path = ""
                try:
                    with tempfile.NamedTemporaryFile(
                        delete=False, mode="w", suffix=".txt", encoding="utf-8"
                    ) as tmp_file:
                        tmp_file.write(source)
                        tmp_file_path = tmp_file.name

                    loader = UnstructuredFileLoader(
                        file_path=tmp_file_path, mode="elements"
                    )
                    documents = await asyncio.to_thread(loader.load)
                finally:
                    if tmp_file_path and Path(tmp_file_path).exists():
                        Path(tmp_file_path).unlink()  # Ensure cleanup

        if not documents:
            raise ValueError("Failed to load any documents from the source.")

        # Combine content and metadata from all loaded documents
        full_content = "\n\n".join(doc.page_content for doc in documents)
        combined_metadata = {
            "source_type": (
                documents[0].metadata.get("source") if documents else "unknown"
            )
        }
        for doc in documents:
            combined_metadata.update(doc.metadata)

        return ProcessedSource(
            markdown_content=full_content,  # Unstructured provides clean text/markdown
            metadata=combined_metadata,
        )

    except Exception as e:
        logger.error(f"Failed to process source: {e}", exc_info=True)
        return ProcessedSource(markdown_content="", metadata={"error": str(e)})
