import json
import traceback
from scraper_ingest import scrape_and_ingest

def lambda_handler(event, context):
    print("Lambda triggered: Starting ingestion job...")

    try:
        scrape_and_ingest()

        print("Ingestion completed successfully.")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Ingestion completed successfully"
            })
        }

    except Exception as e:
        print("Error occurred:", str(e))
        traceback.print_exc()

        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }
