import re

def clean_job_data(text: str) -> str:
    """Basic cleaning: remove excessive whitespace and newlines."""
    # Replace multiple spaces/tabs with a single space
    text = re.sub(r'[ \t]+', ' ', text)
    # Replace multiple newlines with a single newline
    text = re.sub(r'\n+', '\n', text)
    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    # Filter out empty lines
    lines = [line for line in lines if line]
    return "\n".join(lines).strip()

def preserve_markdown_structure(text: str) -> str:
    """Placeholder for logic to preserve markdown like lists, headers."""
    # Example: Naive approach - replace common markdown list indicators temporarily,
    # clean, then restore. More robust parsing might be needed.
    replacements = {
        '__MD_BULLET__': re.compile(r'^\s*[-*+]\s+', re.MULTILINE),
        '__MD_NUMBER__': re.compile(r'^\s*\d+\.\s+', re.MULTILINE)
    }
    
    # Temporarily replace markdown structures
    for placeholder, pattern in replacements.items():
        text = pattern.sub(placeholder, text)
        
    # Perform basic cleaning
    text = clean_job_data(text)
    
    # Restore markdown structures (simplified example)
    text = text.replace('__MD_BULLET__', '* ')
    text = text.replace('__MD_NUMBER__', '1. ') # Note: this loses original numbering
    
    # TODO: Implement more sophisticated markdown parsing if needed
    return text

def process_job_data(text: str) -> str:
    """Process raw job data: clean and attempt to preserve markdown."""
    if not text:
        return ""
    # Step 1: Basic cleaning (whitespace, newlines)
    cleaned_text = clean_job_data(text)
    # Step 2: Attempt to preserve basic markdown structures (can be enhanced)
    processed_text = preserve_markdown_structure(cleaned_text)
    return processed_text
