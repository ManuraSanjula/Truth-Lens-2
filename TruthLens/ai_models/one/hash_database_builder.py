import os
import sqlite3
import imagehash
from PIL import Image
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HashDatabaseBuilder:
    def __init__(self, db_path):
        """Initialize the hash database builder"""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.init_db()

    def init_db(self):
        """Create the database and tables if they don't exist"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()

            # Create table for known fake image hashes
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS fake_image_hashes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hash TEXT NOT NULL,
                source TEXT,
                classification TEXT,
                confidence REAL,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # Create index on hash for fast lookups
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_hash ON fake_image_hashes(hash)')

            self.conn.commit()
            logger.info(f"Database initialized at {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise

    def add_images_from_directory(self, directory, classification="deepfake", source="unknown", confidence=0.9):
        """Process all images in a directory and add their hashes to the database"""
        if not os.path.exists(directory):
            logger.error(f"Directory not found: {directory}")
            return False

        count = 0
        failed = 0

        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
                    image_path = os.path.join(root, file)
                    try:
                        img_hash = self._compute_image_hash(image_path)
                        self._add_hash_to_db(img_hash, classification, source, confidence)
                        count += 1
                        if count % 100 == 0:
                            logger.info(f"Processed {count} images")
                    except Exception as e:
                        logger.warning(f"Failed to process {image_path}: {e}")
                        failed += 1

        logger.info(f"Successfully added {count} images to the database. Failed: {failed}")
        return count

    def _compute_image_hash(self, image_path):
        """Compute perceptual hash for an image"""
        img = Image.open(image_path)
        # Using phash (perceptual hash) as it's robust to minor changes
        img_hash = imagehash.phash(img)
        return str(img_hash)

    def _add_hash_to_db(self, img_hash, classification, source, confidence):
        """Add a hash to the database"""
        try:
            self.cursor.execute(
                "INSERT INTO fake_image_hashes (hash, source, classification, confidence) VALUES (?, ?, ?, ?)",
                (img_hash, source, classification, confidence)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Database insert error: {e}")
            self.conn.rollback()
            return False

    def query_hash(self, img_hash, threshold=0):
        """Query if a hash exists in the database with optional threshold for fuzzy matching"""
        try:
            # For exact matching
            if threshold == 0:
                self.cursor.execute("SELECT * FROM fake_image_hashes WHERE hash = ?", (str(img_hash),))
                return self.cursor.fetchone() is not None

            # For fuzzy matching (not implemented in this simple version)
            # This would need a more complex algorithm to compare hash distances

            return False
        except sqlite3.Error as e:
            logger.error(f"Database query error: {e}")
            return False

    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


def main():
    parser = argparse.ArgumentParser(description='Build a database of perceptual hashes from deepfake images')
    parser.add_argument('--db_path', required=True, help='Path to save the SQLite database')
    parser.add_argument('--image_dir', required=True, help='Directory containing deepfake images')
    parser.add_argument('--classification', default='deepfake', help='Classification label for the images')
    parser.add_argument('--source', default='unknown', help='Source of the deepfake images')

    args = parser.parse_args()

    db_builder = HashDatabaseBuilder(args.db_path)
    try:
        db_builder.add_images_from_directory(
            args.image_dir,
            classification=args.classification,
            source=args.source
        )
    finally:
        db_builder.close()


if __name__ == "__main__":
    main()