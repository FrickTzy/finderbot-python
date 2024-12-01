import firebase_admin
from firebase_admin import credentials, db
from typing import List, Dict, Optional
from settings import DB_PATH, KEY


class DatabaseFetcher:
    def __init__(self, firebase_credentials_path: str, db_url: str) -> None:
        """
        Initialize the DatabaseFetcher with Firebase credentials and the database URL.

        Args:
            firebase_credentials_path (str): Path to the Firebase service account credentials JSON file.
            db_url (str): URL of the Firebase Realtime Database (e.g., 'https://your-database-name.firebaseio.com/').
        """
        # Initialize the Firebase Admin SDK
        cred = credentials.Certificate(firebase_credentials_path)
        firebase_admin.initialize_app(cred, {'databaseURL': db_url})

    @staticmethod
    def fetch_all_missing_people() -> List[Dict[str, Optional[str]]]:
        """
        Fetch all missing people from Firebase Realtime Database.

        Returns:
            list[dict]: A list of dictionaries representing missing people. 
                        Each dictionary has keys like 'name', 'age', 'last_seen', 'location', etc.
        """
        try:
            ref = db.reference('missingReports')

            result: dict | object = ref.get()
            if result:
                return [missing_person for missing_person in result.values()]
            else:
                return []

        except Exception as e:
            print(f"Error fetching missing people: {e}")
            return []


if __name__ == "__main__":
    fetcher = DatabaseFetcher(KEY, DB_PATH)
    missing_people = fetcher.fetch_all_missing_people()

