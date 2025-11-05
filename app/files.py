import os
from loguru import logger

def ensure_archive_folder(archive_folder):
    logger.debug(f"Ensuring archive folder: {archive_folder}")
    if not os.path.exists(archive_folder):
        os.makedirs(archive_folder)
        logger.info(f"Created archive folder: {archive_folder}")

def load_config():
    logger.info("Loading config from config.json")
    import json
    with open('config.json', 'r', encoding='utf-8') as config_file:
        config = json.load(config_file)
        in_event_ids = config.get("in_event_ids", [])
        out_event_ids = config.get("out_event_ids", [])
        events_file = config.get("events_file", "PREvents.csv")
        archive_folder = config.get("archive_folder", "archive")
        processing_interval_minutes = config.get("processing_interval_minutes", 30)
        event_ids = in_event_ids + out_event_ids
        logger.info(f"Config: in={in_event_ids}, out={out_event_ids}, file={events_file}, archive={archive_folder}, interval={processing_interval_minutes}")
        return in_event_ids, out_event_ids, event_ids, events_file, archive_folder, processing_interval_minutes


def archive_file( events_file, archive_folder):
    logger.info(f"Archiving {events_file} to {archive_folder}")
    import shutil
    import os
    
    # Check if source is SMB path
    if events_file.startswith('\\\\') or events_file.startswith('//'):
        logger.info("Source is SMB path, reading content first")
        # For SMB files, we need to read the content and write to local archive
        try:
            from app.events import EventProcessor
            content = EventProcessor._read_smb_file(events_file)
            
            base_name = os.path.basename(events_file.replace('\\', '/'))
            archive_dir = archive_folder
            
            if not os.path.exists(archive_dir):
                os.makedirs(archive_dir)
            
            # List files in archive_dir
            try:
                files = os.listdir(archive_dir)
            except OSError:
                files = []
            
            # Filter files that start with base_name + '.'
            matching_files = [f for f in files if f.startswith(base_name + '.')]
            
            if not matching_files:
                next_num = 1
            else:
                # Find the most recently modified matching file
                mtimes = [(f, os.path.getmtime(os.path.join(archive_dir, f))) for f in matching_files]
                last_file, _ = max(mtimes, key=lambda x: x[1])
                
                # Parse the number from the filename
                parts = last_file.split('.')
                if len(parts) >= 2 and parts[-1].isdigit():
                    num = int(parts[-1])
                    next_num = num + 1
                else:
                    next_num = 1
            
            # Destination path
            dest_filename = f"{base_name}.{next_num}"
            dest_path = os.path.join(archive_dir, dest_filename)
            
            # Write content to archive
            with open(dest_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Now delete the original SMB file to complete the "move" operation
            try:
                import smbclient
                # Configure smbclient to use current user's credentials
                smbclient.ClientConfig(username=None, password=None)
                
                # Build the SMB URL for deletion
                smb_url = events_file.replace('/', '\\')
                smbclient.remove(smb_url)
                logger.info(f"Deleted original SMB file: {events_file}")
                
            except Exception as delete_e:
                logger.warning(f"Failed to delete original SMB file {events_file}: {delete_e}")
                # Don't fail the entire operation if deletion fails
            
            logger.info(f"Archived (moved) SMB file {events_file} to {dest_path}")
            return
            
        except Exception as e:
            logger.error(f"Failed to archive SMB file: {e}")
            raise
    
    # Original logic for local files
    base_name = os.path.basename(events_file)
    archive_dir = archive_folder
    
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
    
    # List files in archive_dir
    try:
        files = os.listdir(archive_dir)
    except OSError:
        files = []
    
    # Filter files that start with base_name + '.'
    matching_files = [f for f in files if f.startswith(base_name + '.')]
    
    if not matching_files:
        next_num = 1
    else:
        # Find the most recently modified matching file
        mtimes = [(f, os.path.getmtime(os.path.join(archive_dir, f))) for f in matching_files]
        last_file, _ = max(mtimes, key=lambda x: x[1])
        
        # Parse the number from the filename
        parts = last_file.split('.')
        if len(parts) >= 2 and parts[-1].isdigit():
            num = int(parts[-1])
            next_num = num + 1
        else:
            # If the last part is not a digit, start from 1
            next_num = 1
    
    # Source file path
    src_path = events_file
    
    # Destination path
    dest_filename = f"{base_name}.{next_num}"
    dest_path = os.path.join(archive_dir, dest_filename)
    
    # Move the file
    shutil.move(src_path, dest_path)
    logger.info(f"Archived {src_path} to {dest_path}")
    

