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
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        
        lines = content.splitlines()
        clean_lines = [line for line in lines if not line.startswith('#') and line.strip()]
        logger.debug(f"Clean lines: {len(clean_lines)}")
        data = [line.strip().split(';') for line in clean_lines]
        df = pd.DataFrame(data, columns=['time', 'date', 'name', 'surname', 'id_point'])
        df['id_point'] = df['id_point'].astype(int)
        events = [cls(**row) for _, row in df.iterrows()]
        logger.info(f"Loaded {len(events)} events from CSV")
        return events
    
    @staticmethod
    def _read_smb_file(smb_path):
        """Read file from SMB share using pysmb"""
        try:
            from smb.SMBConnection import SMBConnection
            import socket
            
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
            
            # Create SMB connection
            # Use anonymous connection for now - you may need to modify for authentication
            conn = SMBConnection('', '', socket.gethostname(), server, use_ntlm_v2=True)
            
            # Connect without authentication (will use current user's credentials if available)
            if not conn.connect(server, 445):
                raise Exception("Failed to connect to SMB server")
            
            # Open and read the file
            with conn.openFile(share, file_path, 'r') as f:
                content = f.read().decode('utf-8')
            
            conn.close()
            
            return content
            
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