from . import events
from . import database
import os
from . import files
import time
from loguru import logger

logger.add("logs/processor.log", rotation="10 MB", retention="1 week")

def main():
    logger.info("Starting MINI RCP Processor")

    # Load configuration
    logger.info("Loading configuration")
    in_event_ids, out_event_ids, event_ids, events_file, archive_folder, processing_interval_minutes = files.load_config()
    logger.info(f"Configuration loaded: events_file={events_file}, interval={processing_interval_minutes} minutes")

    while True:
        try:
            logger.info("Starting event processing cycle")

            # Ensure archive folder exists
            files.ensure_archive_folder(archive_folder)

            # Initialize database
            logger.info("Initializing database")
            database.init_db()

            # Read and process events
            logger.info(f"Reading events from {events_file}")
            event_list = events.read_events(events_file, event_ids)
            logger.info(f"Loaded {len(event_list)} events")

            for event in event_list:
                database.insert_event(event)
            logger.info("Inserted events into database")

            # Archive the processed events file
            logger.info(f"Archiving {events_file} to {archive_folder}")
            files.archive_file(events_file, archive_folder)
            logger.info("Event processing cycle completed")

        except Exception as e:
            logger.error(f"Error in processing cycle: {e}")
            logger.exception("Full traceback:")

        # Wait for next cycle
        logger.info(f"Sleeping for {processing_interval_minutes} minutes")
        time.sleep(processing_interval_minutes * 60)

if __name__ == '__main__':
    main()
