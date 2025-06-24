from typing import Optional, Union , Any
from app.core import get_logger
from app.schemas import JobSourceData
from app.db import JobSourceType

from bs4 import BeautifulSoup
from pypdf import PdfReader
import asyncio
import io
import markdown
import requests
import re


logger = get_logger(__name__)

async def url_to_text(url: str) -> Optional[str]:
    """ 
    Fetches content from a URL and extracts clean text using BeautifulSoup4.
    """
    logger.info(f"Fetching content from URL: {url}")
    try:
        # Use asyncio.to_thread to run requests.get in a separate thread
        response = await asyncio.to_thread(
            requests.get,
            url,
            timeout=10,
        )
        # Check if the request was successful
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove all script and style elements
        for script_or_style  in soup(['script', 'style']):
            script_or_style.decompose()

        # Get text content
        text = soup.get_text(separator='\\n', strip=True)

        # Clean text
        text = await clean_text(text)

        return text
    except Exception as e:
        logger.error(f"Error fetching content from URL: {url}: {e}")
        return None
    
async def pdf_to_text(file_content: bytes) -> Optional[str]:
    """
    Extracts clean text from PDF file content (bytes).
    """
    logger.info("Extracting text from PDF file")
    try:
        # Use asyncio.to_thread to run PdfReader in a separate thread
        reader = await asyncio.to_thread(
            PdfReader,
            io.BytesIO(file_content)
        )
        text = " "

        # Extract text from each page
        for page in reader.pages:
            text += page.extract_text() + "\\n"

        # Clean text
        text = await clean_text(text)

        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF file: {e}")
        return None
          
async def markdown_to_text(markdown_content: str) -> Optional[str]:
    """
    Converts markdown content to clean text using markdown library and BeautifulSoup4.
    """
    logger.info("Converting markdown to text")
    try:
        # Convert markdown to HTML
        html_content = await asyncio.to_thread(markdown.markdown, markdown_content)
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove all script and style elements
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()
        
        # Get text content
        text = soup.get_text(separator='\\n', strip=True)

        # Clean text
        text = await clean_text(text)

        return text
    except Exception as e:
        logger.error(f"Error converting markdown to text: {e}")
        return None

async def source_to_text(
    source_data: JobSourceData,
    file_content_bytes: Optional[bytes] = None,
    ) -> Optional[str]:
    """
    Main dispatcher to get clean text from various job sources.
    The resulting clean text should be stored in JobSourceData.extracted_text_content.
    """
    logger.info("Extracting text from job source")
    extracted_text = ""
    content = source_data.original_value
    # Dispatch based on source type
    if source_data.type == JobSourceType.url.value:
        if content:
            extracted_text = await url_to_text(content)
        else:
            logger.warning("No URL provided for source data")

    # Text/Markdown copied as text
    elif source_data.type == JobSourceType.text.value:
        if content:
            # If it's markdown, convert it to text
            if source_data.mime_type == "text/markdown":
                extracted_text = await markdown_to_text(content)
            # If it's plain text or no MIME type is specified, treat as plain text
            elif source_data.mime_type == "text/plain" or source_data.mime_type is None:
                extracted_text = await clean_text(content)
            else: # This case would now only be hit if mime_type is something else unexpected
                logger.warning(f"Unsupported MIME type for text source data: {source_data.mime_type}")
        else:
            # No original value provided
            logger.warning("No original value provided for text source data")
            extracted_text = None

    # File
    elif source_data.type == JobSourceType.file.value:
        # If no file content provided, return None
        if not file_content_bytes:
            logger.error("No file content provided for file source data")
            return None

        # PDF
        if source_data.mime_type == "application/pdf":
            extracted_text = await pdf_to_text(file_content_bytes)

        # Markdown
        elif source_data.mime_type == "text/markdown":
            try:
                markdown_text = file_content_bytes.decode("utf-8")
                extracted_text = await markdown_to_text(markdown_text)
            except UnicodeDecodeError as e:
                logger.error(f"Error decoding markdown file as utf-8: {e}")
                return None
            except Exception as e:
                logger.error(f"Error processing markdown file: {e}")
                return None

        # Plain Text file
        elif source_data.mime_type == "text/plain":
            try:
                extracted_text = file_content_bytes.decode("utf-8")
                extracted_text = await clean_text(extracted_text)
            except UnicodeDecodeError as e:
                logger.error(f"Error decoding plain text file as utf-8: {e}")
                extracted_text = None

        # Unsupported MIME type
        else:
            logger.warning(f"Unsupported MIME type for file source data: {source_data.mime_type}")
            extracted_text = None

    # Manual
    elif source_data.type == JobSourceType.manual.value:
        if content:
            extracted_text = await clean_text(content)
        else:
            logger.warning("No original value provided for manual source data")
            extracted_text = None
    
    else:
        logger.warning(f"Unsupported source type: {source_data.type}")
        extracted_text = None
    
    return extracted_text
          
async def clean_text(text: str) -> Optional[str]:
    """ Cleans text by removing excessive whitespace and newlines using regex"""
    if not text:
        logger.warning("No text provided for cleaning")
        return None
    try:
        logger.info("Cleaning text")
        # Remove leading/trailing whitespace from the entire text
        text = text.strip()
        # Normalize multiple horizontal spaces and/or tabs to a single space
        text = re.sub(r'[ \t]+', ' ', text)
        # Normalize multiple vertical newlines to a single newline
        text = re.sub(r'\n+', '\n', text)
        # Normalize multiple newlines (optionally surrounded by spaces) to a single newline:
        text = re.sub(r'(\s*\n\s*)+', '\n', text)
        # Normalize multiple newlines (optionally surrounded by spaces) to a single newline:
        text = re.sub(r'(\s*\n\s*)+', '\n', text)
        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        # Filter out empty lines
        lines = [line for line in lines if line]
        # Join the lines back into a single string with a single newline between each line
        cleaned_text = "\n".join(lines)

        await asyncio.sleep(0) # Yield control to allow other tasks to run
        return cleaned_text
    except Exception as e:
        logger.error(f"Error cleaning text: {e}")
        return None
