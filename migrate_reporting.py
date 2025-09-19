#!/usr/bin/env python3
"""
Advanced Reporting System Database Migration
Creates tables for the comprehensive reporting system
"""

import sys
import os

# Add the src directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

import sqlite3
from datetime import datetime
import json
from services.db import get_engine
from sqlmodel import SQLModel

def migrate_reporting_tables():
    """Create the reporting system tables"""
    print("🔄 Starting Advanced Reporting System migration...")
    
    # Create all tables using SQLModel
    engine = get_engine()
    SQLModel.metadata.create_all(engine)
    
    print("✅ Database tables created/updated successfully!")
    
    # Connect to database for data operations
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    
    try:
        # Check if reporting tables exist and are accessible
        cursor.execute("SELECT COUNT(*) FROM reporttemplate")
        template_count = cursor.fetchone()[0]
        print(f"📋 Report Templates: {template_count} records")
        
        cursor.execute("SELECT COUNT(*) FROM customreport")
        custom_count = cursor.fetchone()[0]
        print(f"🔧 Custom Reports: {custom_count} records")
        
        cursor.execute("SELECT COUNT(*) FROM reportexecution")
        execution_count = cursor.fetchone()[0]
        print(f"📊 Report Executions: {execution_count} records")
        
        cursor.execute("SELECT COUNT(*) FROM reportshare")
        share_count = cursor.fetchone()[0]
        print(f"📤 Report Shares: {share_count} records")
        
    except sqlite3.OperationalError as e:
        print(f"❌ Error checking tables: {e}")
        return False
    
    # Add sample report templates
    add_sample_reporting_data(cursor, conn)
    
    conn.commit()
    conn.close()
    
    print("✅ Advanced Reporting System migration completed successfully!")
    return True

def add_sample_reporting_data(cursor, conn):
    """Add sample reporting data"""
    print("📊 Adding sample reporting templates and data...")
    
    # Check if we already have sample templates
    cursor.execute("SELECT COUNT(*) FROM reporttemplate WHERE is_system = 1")
    if cursor.fetchone()[0] > 0:
        print("📋 Sample templates already exist, skipping...")
        return
    
    # Add sample report templates
    sample_templates = [
        {
            'name': 'Student Progress Report',
            'description': 'Comprehensive student performance report with grades and analytics',
            'category': 'student',
            'template_type': 'pdf',
            'data_sources': json.dumps(['students', 'marks', 'subjects']),
            'layout_config': json.dumps({'orientation': 'portrait', 'include_charts': True}),
            'fields_config': json.dumps({
                'students': ['first_name', 'last_name', 'class_name'],
                'marks': ['subject_name', 'score', 'term'],
                'subjects': ['name', 'code']
            }),
            'filters_config': json.dumps(['class', 'term', 'subject']),
            'is_system': True,
            'created_by': 1  # Admin user
        },
        {
            'name': 'Class Performance Summary',
            'description': 'Overall class performance with subject-wise breakdown',
            'category': 'class',
            'template_type': 'excel',
            'data_sources': json.dumps(['students', 'marks', 'classes']),
            'layout_config': json.dumps({'include_charts': True, 'group_by': 'subject'}),
            'fields_config': json.dumps({
                'students': ['first_name', 'last_name'],
                'marks': ['subject_name', 'score'],
                'classes': ['name', 'category']
            }),
            'filters_config': json.dumps(['class', 'term']),
            'is_system': True,
            'created_by': 1
        },
        {
            'name': 'Subject Analysis Report',
            'description': 'Detailed analysis of subject performance across all classes',
            'category': 'subject',
            'template_type': 'pdf',
            'data_sources': json.dumps(['marks', 'subjects', 'students']),
            'layout_config': json.dumps({'orientation': 'landscape', 'include_statistics': True}),
            'fields_config': json.dumps({
                'marks': ['score', 'term'],
                'subjects': ['name', 'code'],
                'students': ['class_name']
            }),
            'filters_config': json.dumps(['subject', 'term', 'class']),
            'is_system': True,
            'created_by': 1
        },
        {
            'name': 'Teacher Performance Dashboard',
            'description': 'Teacher-specific dashboard with class and student performance',
            'category': 'teacher',
            'template_type': 'html',
            'data_sources': json.dumps(['teachers', 'classes', 'students', 'marks']),
            'layout_config': json.dumps({'dashboard_style': True, 'interactive': True}),
            'fields_config': json.dumps({
                'teachers': ['first_name', 'last_name'],
                'classes': ['name'],
                'students': ['first_name', 'last_name'],
                'marks': ['score', 'subject_name']
            }),
            'filters_config': json.dumps(['teacher', 'term']),
            'is_system': True,
            'created_by': 1
        },
        {
            'name': 'School Overview Report',
            'description': 'Complete school performance overview with all key metrics',
            'category': 'school',
            'template_type': 'pdf',
            'data_sources': json.dumps(['students', 'marks', 'classes', 'subjects', 'teachers']),
            'layout_config': json.dumps({'comprehensive': True, 'include_trends': True}),
            'fields_config': json.dumps({
                'students': ['class_name'],
                'marks': ['score', 'term'],
                'classes': ['name', 'category'],
                'subjects': ['name'],
                'teachers': ['first_name', 'last_name']
            }),
            'filters_config': json.dumps(['term', 'academic_year']),
            'is_system': True,
            'created_by': 1
        }
    ]
    
    # Insert sample templates
    for template in sample_templates:
        cursor.execute("""
            INSERT INTO reporttemplate (
                name, description, category, template_type, data_sources,
                layout_config, fields_config, filters_config, is_system,
                is_active, created_by, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            template['name'], template['description'], template['category'],
            template['template_type'], template['data_sources'],
            template['layout_config'], template['fields_config'],
            template['filters_config'], template['is_system'],
            True, template['created_by'], datetime.now(), datetime.now()
        ))
    
    print("✅ Added 5 sample report templates")
    
    # Add a sample custom report
    cursor.execute("""
        INSERT INTO customreport (
            name, description, template_id, report_type, data_sources,
            filters_applied, fields_selected, layout_config, export_format,
            is_scheduled, created_by, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "Weekly Class 7 Mathematics Report",
        "Weekly performance report for Class 7 Mathematics students",
        1,  # Student Progress Report template
        "student",
        json.dumps(['students', 'marks']),
        json.dumps({'class': 'Class 7', 'subject': 'Mathematics', 'term': 'Current'}),
        json.dumps(['first_name', 'last_name', 'score']),
        json.dumps({'frequency': 'weekly'}),
        "pdf",
        False,
        1,  # Admin user
        datetime.now(),
        datetime.now()
    ))
    
    print("✅ Added 1 sample custom report")
    
    print("📊 Sample reporting data added successfully!")

if __name__ == "__main__":
    success = migrate_reporting_tables()
    if success:
        print("🎉 Migration completed successfully!")
    else:
        print("❌ Migration failed!")
        sys.exit(1)