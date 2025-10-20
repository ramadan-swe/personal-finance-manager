import os
import tempfile

def atomic_write(file_path, data, mode='w'):
    """
    Atomically writes data to a file.

    This function writes data to a temporary file and then atomically
    renames it to the final destination. This ensures that the original
    file is not corrupted if the write operation is interrupted.

    Args:
        file_path (str): The path to the final file.
        data (str): The data to write to the file.
        mode (str, optional): The file opening mode. Defaults to 'w'.
    """
    temp_dir = os.path.dirname(file_path)
    with tempfile.NamedTemporaryFile(mode=mode, delete=False, dir=temp_dir) as temp_file:
        temp_file.write(data)
        temp_file_path = temp_file.name

    try:
        os.rename(temp_file_path, file_path)
    except Exception as e:
        os.remove(temp_file_path)
        raise e
