import os
import zipfile
from pathlib import Path
from django.conf import settings

def preprocess_zip_file(file_path, file_id):
    """
    Preprocess a zip file by extracting it to a folder in media/uncompressed/.
    
    Args:
        file_path (str): Path to the zip file
        file_id (int): ID of the uploaded file
        
    Returns:
        dict: Dictionary containing status and extracted path
    """
    try:
        # Create the base uncompressed directory if it doesn't exist
        uncompressed_dir = Path(settings.MEDIA_ROOT) / 'uncompressed'
        uncompressed_dir.mkdir(parents=True, exist_ok=True)
        
        # Create folder path for this specific file
        extract_dir = uncompressed_dir / str(file_id)
        
        # If directory already exists, return success
        if extract_dir.exists():
            return {
                'status': 'success',
                'message': 'Files already extracted',
                'extracted_path': str(extract_dir)
            }
        
        # Create the directory for this file
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract the zip file
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
            
        return {
            'status': 'success',
            'message': 'Files extracted successfully',
            'extracted_path': str(extract_dir)
        }
        
    except zipfile.BadZipFile:
        return {
            'status': 'error',
            'message': 'Invalid zip file'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error extracting zip file: {str(e)}'
        }
