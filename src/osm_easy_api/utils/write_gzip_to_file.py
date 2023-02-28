import gzip
import shutil
import threading

def write_gzip_to_file(file_from: gzip.GzipFile, file_to: str):
    """Saves gzip to file.

    Args:
        file_from (gzip.GzipFile): Gzip file to write from.
        file_to (str): Path to file to write to.
    """
    with threading.Lock():
        with gzip.open(file_to, 'wb') as f_to:
            shutil.copyfileobj(file_from, f_to)