# -*- coding: utf-8 -*-
"""
School Configuration Manager
Handles loading and saving school settings from JSON configuration
"""

import json
import os
from typing import Dict, Any

class SchoolConfigManager:
    """Manages school configuration using JSON file storage"""
    
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(__file__), 'school_settings.json')
        self._ensure_config_file_exists()
    
    def _ensure_config_file_exists(self):
        """Ensure configuration file exists with default values"""
        if not os.path.exists(self.config_file):
            default_config = {
                "school_name": "KHAYYAM ACADEMY",
                "school_subtitle": "Excellence in Islamic Education",
                "address": "P.O. Box 123, School Street, City, Country",
                "email": "info@khayyamacademy.edu",
                "phone_numbers": ["+123-456-7890", "+123-456-7891"],
                "logo_path": "",
                "show_logo": False,
                "academic_year": "2024-2025",
                "current_term": "3RD TERM",
                "report_titles": {
                    "Mid-term": "MID-TERM EXAMINATION REPORT",
                    "End of Term": "END OF TERM EXAMINATION REPORT"
                },
                "grade_remarks": {
                    "1": "HIGHEST", "2": "HIGHER", "3": "HIGH", "4": "GOOD", "5": "CREDIT",
                    "6": "PASS", "7": "FAIR", "8": "POOR", "9": "FAIL"
                },
                "colors": {
                    "school_primary": "#1A3380",
                    "accent": "#FFCC00", 
                    "success": "#33B547"
                }
            }
            self.save_config(default_config)
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def save_config(self, config_data: Dict[str, Any]) -> bool:
        """Save configuration to JSON file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default=None):
        """Get a configuration value"""
        config = self.load_config()
        return config.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """Set a configuration value"""
        config = self.load_config()
        config[key] = value
        return self.save_config(config)
    
    def update(self, updates: Dict[str, Any]) -> bool:
        """Update multiple configuration values"""
        config = self.load_config()
        config.update(updates)
        return self.save_config(config)

# Create global instance
school_config = SchoolConfigManager()

# Convenience class that mimics the old SchoolConfig interface
class SchoolConfig:
    """Backward compatibility wrapper for the JSON-based configuration"""
    
    @property
    def SCHOOL_NAME(self):
        return school_config.get('school_name', 'KHAYYAM ACADEMY')
    
    @property
    def SCHOOL_SUBTITLE(self):
        return school_config.get('school_subtitle', 'Excellence in Islamic Education')
    
    @property
    def ADDRESS(self):
        return school_config.get('address', 'P.O. Box 123, School Street, City, Country')
    
    @property
    def EMAIL(self):
        return school_config.get('email', 'info@khayyamacademy.edu')
    
    @property
    def PHONE_NUMBERS(self):
        return school_config.get('phone_numbers', ['+123-456-7890', '+123-456-7891'])
    
    @property
    def LOGO_PATH(self):
        return school_config.get('logo_path', '')
    
    @property
    def SHOW_LOGO(self):
        return school_config.get('show_logo', False)
    
    @property
    def ACADEMIC_YEAR(self):
        return school_config.get('academic_year', '2024-2025')
    
    @property
    def CURRENT_TERM(self):
        return school_config.get('current_term', '3RD TERM')
    
    @property
    def REPORT_TITLES(self):
        return school_config.get('report_titles', {
            "Mid-term": "MID-TERM EXAMINATION REPORT",
            "End of Term": "END OF TERM EXAMINATION REPORT"
        })
    
    @property
    def GRADE_REMARKS(self):
        grade_remarks_str = school_config.get('grade_remarks', {
            "1": "HIGHEST", "2": "HIGHER", "3": "HIGH", "4": "GOOD", "5": "CREDIT",
            "6": "PASS", "7": "FAIR", "8": "POOR", "9": "FAIL"
        })
        # Convert string keys to integers
        if grade_remarks_str:
            return {int(k): v for k, v in grade_remarks_str.items()}
        else:
            return {1: "HIGHEST", 2: "HIGHER", 3: "HIGH", 4: "GOOD", 5: "CREDIT",
                    6: "PASS", 7: "FAIR", 8: "POOR", 9: "FAIL"}
    
    @property
    def COLORS(self):
        return school_config.get('colors', {
            "school_primary": "#1A3380",
            "accent": "#FFCC00",
            "success": "#33B547"
        })