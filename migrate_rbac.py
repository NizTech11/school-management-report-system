#!/usr/bin/env python3
"""
Migration script to add User and Role tables for RBAC system
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

def migrate_rbac_tables():
    """Add User and Role tables for role-based access control"""
    db_path = Path("students.db")
    
    if not db_path.exists():
        print("❌ Database file not found. Please run the application first to create the database.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Starting RBAC tables migration...")
        
        # Check if User table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='user';
        """)
        user_table_exists = cursor.fetchone() is not None
        
        if not user_table_exists:
            print("Creating User table...")
            cursor.execute("""
                CREATE TABLE user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR UNIQUE NOT NULL,
                    email VARCHAR UNIQUE NOT NULL,
                    hashed_password VARCHAR NOT NULL,
                    full_name VARCHAR NOT NULL,
                    role VARCHAR DEFAULT 'Teacher' NOT NULL,
                    is_active BOOLEAN DEFAULT 1 NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            """)
            print("✅ User table created")
        else:
            print("✅ User table already exists")
        
        # Check if Role table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='role';
        """)
        role_table_exists = cursor.fetchone() is not None
        
        if not role_table_exists:
            print("Creating Role table...")
            cursor.execute("""
                CREATE TABLE role (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR UNIQUE NOT NULL,
                    description VARCHAR NOT NULL,
                    permissions TEXT NOT NULL
                )
            """)
            print("✅ Role table created")
        else:
            print("✅ Role table already exists")
        
        # Insert default roles
        roles_data = [
            ('Teacher', 'Standard teacher role', '["students.view", "students.create", "students.edit", "classes.view", "subjects.view", "marks.view", "marks.create", "marks.edit", "reports.view", "reports.generate", "analytics.view", "calendar.view", "curriculum.view", "assignments.view", "assignments.create", "assignments.grade"]'),
            ('Head', 'Head teacher role with management permissions', '["students.view", "students.create", "students.edit", "students.delete", "teachers.view", "teachers.create", "teachers.edit", "classes.view", "classes.create", "classes.edit", "classes.delete", "subjects.view", "subjects.create", "subjects.edit", "subjects.delete", "marks.view", "marks.create", "marks.edit", "marks.delete", "reports.view", "reports.generate", "reports.export", "analytics.view", "analytics.advanced", "calendar.view", "calendar.create", "calendar.edit", "calendar.delete", "curriculum.view", "curriculum.create", "curriculum.edit", "assignments.view", "assignments.create", "assignments.grade"]'),
            ('Admin', 'Full system administrator role', '["students.view", "students.create", "students.edit", "students.delete", "teachers.view", "teachers.create", "teachers.edit", "teachers.delete", "classes.view", "classes.create", "classes.edit", "classes.delete", "subjects.view", "subjects.create", "subjects.edit", "subjects.delete", "marks.view", "marks.create", "marks.edit", "marks.delete", "reports.view", "reports.generate", "reports.export", "analytics.view", "analytics.advanced", "calendar.view", "calendar.create", "calendar.edit", "calendar.delete", "system.settings", "system.backup", "system.logs", "system.users", "system.roles", "curriculum.view", "curriculum.create", "curriculum.edit", "assignments.view", "assignments.create", "assignments.grade"]')
        ]
        
        for role_name, description, permissions in roles_data:
            # Check if role exists
            cursor.execute("SELECT id FROM role WHERE name = ?", (role_name,))
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO role (name, description, permissions) VALUES (?, ?, ?)",
                    (role_name, description, permissions)
                )
                print(f"✅ Created default role: {role_name}")
        
        # Create default admin user if no users exist
        cursor.execute("SELECT COUNT(*) FROM user")
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            print("Creating default admin user...")
            import bcrypt
            
            # Hash the default password
            password = "admin123"
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute("""
                INSERT INTO user (username, email, hashed_password, full_name, role, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                'admin',
                'admin@school.com', 
                hashed_password,
                'System Administrator',
                'Admin',
                1,
                datetime.utcnow().isoformat()
            ))
            print("✅ Default admin user created")
            print("   Username: admin")
            print("   Password: admin123")
            print("   Please change these credentials after first login!")
        else:
            print("✅ Users already exist, skipping default admin creation")
        
        # Commit changes
        conn.commit()
        print("✅ RBAC migration completed successfully!")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM user")
        user_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM role")
        role_count = cursor.fetchone()[0]
        
        print(f"📊 Migration Summary:")
        print(f"   - Total users: {user_count}")
        print(f"   - Total roles: {role_count}")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error during migration: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during migration: {e}")
        return False

if __name__ == "__main__":
    print("🚀 RBAC System Migration Script")
    print("=" * 50)
    
    success = migrate_rbac_tables()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("The Role-Based Access Control system is now ready.")
        print("You can now restart the application and log in with the admin credentials.")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)