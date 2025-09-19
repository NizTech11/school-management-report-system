#!/usr/bin/env python3
"""
Test script to verify delete all marks functionality
"""

import sys
sys.path.append('src')

from services.db import get_session, Mark
from sqlmodel import select

def test_delete_all_marks():
    """Test the delete all marks functionality"""
    print("🔍 Testing Delete All Marks Functionality")
    print("=" * 50)
    
    # Check initial count
    with get_session() as session:
        initial_marks = session.exec(select(Mark)).all()
        initial_count = len(initial_marks)
        print(f"📊 Initial marks count: {initial_count}")
    
    if initial_count == 0:
        print("ℹ️  No marks to delete. Test completed.")
        return
    
    # Perform deletion
    print("🗑️  Deleting all marks...")
    try:
        with get_session() as session:
            # Get all marks
            all_marks = session.exec(select(Mark)).all()
            delete_count = len(all_marks)
            
            # Delete each mark
            for mark in all_marks:
                session.delete(mark)
            
            # Commit the transaction
            session.commit()
            print(f"✅ Deleted {delete_count} marks successfully")
            
        # Verify deletion
        with get_session() as session:
            remaining_marks = session.exec(select(Mark)).all()
            remaining_count = len(remaining_marks)
            print(f"📊 Remaining marks count: {remaining_count}")
            
            if remaining_count == 0:
                print("🎉 SUCCESS: All marks deleted successfully!")
            else:
                print(f"❌ FAILURE: {remaining_count} marks still remain")
                
    except Exception as e:
        print(f"❌ ERROR during deletion: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_delete_all_marks()