import os
import shutil
from pathlib import Path
from .init_db import init_db

def reset_database():
    """
    Reset the database by:
    1. Deleting the SQLite database file
    2. Clearing the vector store directory
    3. Removing the topics file
    """

    # Get base directory
    base_dir = Path(__file__).parent.parent.parent  # backend/
    
    # Paths to clean
    db_path = os.path.join(base_dir, "ragchat.db")
    vectorstore_dir = os.path.join(base_dir, "app", "data", "vectorstore")
    topics_file = os.path.join(base_dir, "app", "data", "vectorstore_topics", "topics.txt")
    
    # Delete database file
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"Deleted database file: {db_path}")
        except Exception as e:
            print(f"Error deleting database file: {e}")
    else:
        print(f"Database file not found: {db_path}")
    
    # Clear vector store directory
    if os.path.exists(vectorstore_dir):
        try:
            shutil.rmtree(vectorstore_dir)
            os.makedirs(vectorstore_dir, exist_ok=True)
            print(f"Deleted vector store directory contents: {vectorstore_dir}")
        except Exception as e:
            print(f"Error clearing vector store directory: {e}")
    else:
        print(f"Vector store directory not found: {vectorstore_dir}")
    
    # Remove topics file
    if os.path.exists(topics_file):
        try:
            os.remove(topics_file)
            print(f"Deleted topics file: {topics_file}")
        except Exception as e:
            print(f"Error removing topics file: {e}")
    else:
        print(f"Topics file not found: {topics_file}")
    
    print("Database and vector store reset complete")

if __name__ == "__main__":
    # Ask for confirmation before proceeding
    confirm = input("WARNING: This will delete all conversations and documents. Are you sure? (y/n): ")
    if confirm.lower() == 'y':
        reset_database()
        init_db()
    else:
        print("Operation cancelled")