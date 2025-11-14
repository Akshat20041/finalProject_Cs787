from typing import Optional

def read_file(file_path: str) -> Optional[str]:
    """
    Reads the content of a file.

    Args:
        file_path: The path to the file.

    Returns:
        The content of the file as a string, or None if the file is not found.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None

def write_file(file_path: str, content: str) -> None:
    """
    Writes content to a file.

    Args:
        file_path: The path to the file to write to.
        content: The content to write.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully wrote to {file_path}")
    except IOError as e:
        print(f"Error writing to file {file_path}: {e}")

