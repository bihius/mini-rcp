import pandas as pd
from datetime import datetime
from loguru import logger



class EventProcessor:
    def __init__(self, time, date, name, surname, id_point):
        self.time = time
        self.date = date
        self.name = name
        self.surname = surname
        self.id_point = id_point
        
    def __repr__(self):
        return f"EventProcessor(time={self.time}, date={self.date}, name={self.name}, surname={self.surname}, id_point={self.id_point})"
    
    @classmethod
    def from_csv(cls, file_path):
        logger.info(f"Reading events from CSV: {file_path}")
        
        # Check if it's an SMB path
        if file_path.startswith('\\\\') or file_path.startswith('//'):
            logger.info("Detected SMB path, using SMB protocol")
            content = cls._read_smb_file(file_path)
        else:
            logger.info("Using local file access")
            content = cls._read_file_with_encoding_detection(file_path, use_smb=False)
        
        lines = content.splitlines()
        clean_lines = [line for line in lines if not line.startswith('#') and line.strip()]
        logger.debug(f"Clean lines: {len(clean_lines)}")
        
        # Parse CSV data, handling variable column counts
        data = []
        for line in clean_lines:
            parts = line.strip().split(';')
            # Remove empty trailing fields
            while parts and parts[-1] == '':
                parts.pop()
            
            # Skip if not enough columns (need at least time, date, id_point)
            if len(parts) < 5:
                logger.debug(f"Skipping line with insufficient columns ({len(parts)}): {line[:50]}...")
                continue
            
            # Pad with empty strings if needed to ensure 5 columns
            while len(parts) < 5:
                parts.append('')
            
            # Take only first 5 columns (time, date, name, surname, id_point)
            if len(parts) >= 5:
                data.append(parts[:5])
            else:
                logger.debug(f"Skipping malformed line: {line[:50]}...")
        
        logger.info(f"Valid data rows: {len(data)} (filtered from {len(clean_lines)} total lines)")
        
        if not data:
            raise Exception("No valid data rows found in CSV file")
        
        df = pd.DataFrame(data, columns=['time', 'date', 'name', 'surname', 'id_point'])
        df['id_point'] = df['id_point'].astype(int)
        events = [cls(**row) for _, row in df.iterrows()]
        logger.info(f"Loaded {len(events)} events from CSV")
        return events
    
    @staticmethod
    def _read_file_with_encoding_detection(file_path, use_smb=False):
        """Read file with automatic encoding detection"""
        # Try Polish-friendly encodings first
        encodings_to_try = ['cp1250', 'utf-8', 'utf-16', 'cp1252', 'latin1']
        content = None
        
        for encoding in encodings_to_try:
            try:
                logger.debug(f"Trying to read file with encoding: {encoding}")
                if use_smb:
                    import smbclient
                    with smbclient.open_file(file_path, mode='r', encoding=encoding) as f:
                        content = f.read()
                else:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                logger.info(f"Successfully read file using {encoding} encoding")
                return content
            except UnicodeDecodeError:
                logger.debug(f"Failed to decode with {encoding}, trying next encoding...")
                continue
            except Exception as enc_error:
                logger.debug(f"Error with {encoding}: {enc_error}")
                continue
        
        raise Exception("Failed to read file with any supported encoding")
        
    @staticmethod
    def _read_smb_file(smb_path):
        """Read file from SMB share using smbprotocol with proper Windows authentication"""
        try:
            import smbclient
            
            # Parse SMB path: \\server\share\path\to\file or //server/share/path/to/file
            if smb_path.startswith('\\\\'):
                smb_path = smb_path[2:]  # Remove leading \\
            elif smb_path.startswith('//'):
                smb_path = smb_path[2:]  # Remove leading //
            
            parts = smb_path.replace('\\', '/').split('/')
            server = parts[0]
            share = parts[1]
            file_path = '/'.join(parts[2:])
            
            logger.info(f"Connecting to SMB: server={server}, share={share}, file={file_path}")
            
            # Configure smbclient to use current user's credentials
            # This will automatically use the Windows user's session
            smbclient.ClientConfig(username=None, password=None)  # Use integrated auth
            
            # Build the full SMB URL
            file_path_windows = file_path.replace('/', '\\')
            smb_url = f"\\\\{server}\\{share}\\{file_path_windows}"
            
            # Read the file using encoding detection
            return EventProcessor._read_file_with_encoding_detection(smb_url, use_smb=True)
            
        except Exception as e:
            logger.error(f"Failed to read SMB file: {e}")
            raise
    
    @staticmethod
    def filter_events(events, event_ids):
        logger.debug(f"Filtering {len(events)} events with ids {event_ids}")
        filtered = [event for event in events if event.id_point in event_ids]
        logger.info(f"Filtered to {len(filtered)} events")
        return filtered
    
def read_events(events_file, event_ids):
    logger.info(f"Reading and filtering events from {events_file}")
    all_events = EventProcessor.from_csv(events_file)
    filtered_events = EventProcessor.filter_events(all_events, event_ids)
    return filtered_events