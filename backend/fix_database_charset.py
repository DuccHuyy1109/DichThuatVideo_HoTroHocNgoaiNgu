"""
Fix Database Charset to UTF-8
Sửa encoding của database để hiển thị đúng tất cả ngôn ngữ
"""
import sqlite3
import sys

def fix_database_charset(db_path='instance/database.db'):
    """
    Fix SQLite database charset to UTF-8
    """
    try:
        print("🔧 Connecting to database...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Set UTF-8 encoding
        cursor.execute("PRAGMA encoding = 'UTF-8'")
        
        print("✅ Database encoding set to UTF-8")
        
        # Check current vocabulary with issues
        cursor.execute("""
            SELECT vocab_id, word, translation, language 
            FROM vocabulary 
            WHERE word LIKE '%?%' OR translation LIKE '%?%'
            LIMIT 10
        """)
        
        corrupted = cursor.fetchall()
        
        if corrupted:
            print(f"⚠️ Found {len(corrupted)} corrupted entries:")
            for row in corrupted:
                print(f"  - ID {row[0]}: word='{row[1]}', translation='{row[2]}', language={row[3]}")
            
            print("\n💡 These entries need to be re-extracted from videos.")
            print("   Delete them and reprocess videos:")
            print(f"   DELETE FROM vocabulary WHERE word LIKE '%?%';")
        else:
            print("✅ No corrupted entries found")
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def create_new_database_with_utf8():
    """
    Tạo database mới với UTF-8 encoding đúng
    """
    print("\n🔧 Creating new UTF-8 database...")
    
    try:
        conn = sqlite3.connect('instance/database_utf8.db')
        conn.execute("PRAGMA encoding = 'UTF-8'")
        
        # Create vocabulary table with UTF-8
        conn.execute("""
            CREATE TABLE IF NOT EXISTS vocabulary (
                vocab_id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id INTEGER,
                word TEXT NOT NULL,
                translation TEXT NOT NULL,
                pronunciation TEXT,
                part_of_speech TEXT,
                example_sentence TEXT,
                example_translation TEXT,
                language TEXT NOT NULL,
                difficulty_level TEXT,
                FOREIGN KEY (video_id) REFERENCES videos(video_id)
            )
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ New UTF-8 database created: instance/database_utf8.db")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == '__main__':
    print("=" * 50)
    print("DATABASE CHARSET FIX")
    print("=" * 50)
    
    # Fix existing database
    print("\n1. Fixing existing database...")
    fix_database_charset()
    
    # Option to create new one
    print("\n" + "=" * 50)
    print("RECOMMENDATION:")
    print("=" * 50)
    print("If you have corrupted data, best solution:")
    print("1. Delete corrupted vocabulary: DELETE FROM vocabulary WHERE word LIKE '%?%';")
    print("2. Reprocess videos to extract vocabulary again")
    print("3. Or create new database with: python fix_charset.py --new")
    print("=" * 50)