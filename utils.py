import re
import os
import pandas as pd
import multiprocessing
from time import time as timer
from tqdm import tqdm
import numpy as np
from pathlib import Path
from functools import partial
import requests
import urllib.request

def download_image(image_data, savefolder):
    """
    Download image with sample_id mapping
    image_data: tuple of (sample_id, image_link)
    """
    if isinstance(image_data, tuple) and len(image_data) == 2:
        sample_id, image_link = image_data
        if isinstance(image_link, str):
            # Get file extension from URL
            original_filename = Path(image_link).name
            file_ext = Path(original_filename).suffix or '.jpg'
            
            # Create filename with sample_id
            filename = f"{sample_id}{file_ext}"
            image_save_path = os.path.join(savefolder, filename)
            
            if not os.path.exists(image_save_path):
                try:
                    urllib.request.urlretrieve(image_link, image_save_path)
                    return (sample_id, image_save_path, 'success')
                except Exception as ex:
                    print('Warning: Not able to download - {} for sample_id {}\n{}'.format(image_link, sample_id, ex))
                    return (sample_id, image_link, 'failed')
            else:
                return (sample_id, image_save_path, 'exists')
    return None

def download_images_with_mapping(sample_ids, image_links, download_folder):
    """
    Download images with sample_id mapping
    Returns a DataFrame with download results
    """
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    
    # Create tuples of (sample_id, image_link)
    image_data_list = list(zip(sample_ids, image_links))
    
    results = []
    download_image_partial = partial(download_image, savefolder=download_folder)
    
    print(f"Downloading {len(image_data_list)} images with sample_id mapping...")
    
    with multiprocessing.Pool(32) as pool:
        for result in tqdm(pool.imap(download_image_partial, image_data_list), total=len(image_data_list)):
            if result:
                results.append(result)
        pool.close()
        pool.join()
    
    # Create DataFrame with results
    if results:
        results_df = pd.DataFrame(results, columns=['sample_id', 'path_or_url', 'status'])
        
        # Save mapping to CSV
        mapping_file = os.path.join(download_folder, 'download_mapping.csv')
        results_df.to_csv(mapping_file, index=False)
        print(f"Download mapping saved to: {mapping_file}")
        
        # Print summary
        success_count = len(results_df[results_df['status'] == 'success'])
        failed_count = len(results_df[results_df['status'] == 'failed'])
        exists_count = len(results_df[results_df['status'] == 'exists'])
        
        print(f"\nDownload Summary:")
        print(f"  Successfully downloaded: {success_count}")
        print(f"  Already existed: {exists_count}")
        print(f"  Failed: {failed_count}")
        
        return results_df
    else:
        print("No results to return")
        return pd.DataFrame()

def download_images(image_links, download_folder):
    """Original function for backward compatibility"""
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    
    # Convert to old format for compatibility
    image_data_list = [(i, link) for i, link in enumerate(image_links)]
    
    results = []
    download_image_partial = partial(download_image, savefolder=download_folder)
    with multiprocessing.Pool(32) as pool:
        for result in tqdm(pool.imap(download_image_partial, image_data_list), total=len(image_data_list)):
            results.append(result)
        pool.close()
        pool.join()