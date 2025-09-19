"""
Clean Report Template Editor
Simple and robust web interface for customizing school report templates
"""

import streamlit as st
import os
import sys
import json
from datetime import datetime

# Ensure proper imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.rbac import is_logged_in, get_current_user, has_permission

# Page configuration and authentication check
st.set_page_config(page_title="Report Template Editor", page_icon="📝", layout="wide")

# Authentication check
if not is_logged_in():
    st.error("🔐 Please log in to access this page.")
    st.stop()

user = get_current_user()
if not user or not has_permission(user['role'], 'reports.templates.edit'):
    st.error("🚫 You don't have permission to edit report templates.")
    st.stop()

def get_config_file_path():
    """Get the path to the configuration file"""
    return os.path.join(os.path.dirname(__file__), '..', 'config', 'clean_school_settings.json')

def load_config():
    """Load configuration from JSON file with robust error handling and multiple encoding fallbacks"""
    config_file = get_config_file_path()
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
        }
    }
    
    if not os.path.exists(config_file):
        # Create the file with default config if it doesn't exist
        try:
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=True)
            st.info("Created new configuration file with default settings.")
            return default_config
        except Exception as e:
            st.error(f"Could not create configuration file: {str(e)}")
            return default_config
    
    # Try multiple encodings to handle Windows encoding issues
    encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'ascii']
    
    for encoding in encodings_to_try:
        try:
            with open(config_file, 'r', encoding=encoding) as f:
                content = f.read()
                
                # Remove BOM if present
                if content.startswith('\ufeff'):
                    content = content[1:]
                
                # Clean the content of problematic characters
                content = clean_content(content)
                
                # Try to parse JSON
                config = json.loads(content)
                
                # Validate and sanitize the loaded config
                config = sanitize_config(config)
                return config
                
        except (UnicodeDecodeError, UnicodeError) as e:
            st.warning(f"Could not read file with {encoding} encoding: {str(e)}")
            continue
        except json.JSONDecodeError as e:
            st.error(f"Configuration file is corrupted with {encoding} encoding: {str(e)}")
            continue
        except Exception as e:
            st.warning(f"Unexpected error with {encoding} encoding: {str(e)}")
            continue
    
    # If all encodings failed, recreate with clean default config
    st.error("⚠️ Configuration file has encoding issues. Creating a new clean configuration.")
    try:
        # Backup the problematic file
        backup_file = config_file + '.backup'
        if os.path.exists(config_file):
            os.rename(config_file, backup_file)
            st.info(f"Backed up problematic file to: {backup_file}")
        
        # Create new clean file
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4, ensure_ascii=True)
        
        st.success("✅ Created new clean configuration file.")
        return default_config
    except Exception as e:
        st.error(f"Could not recreate configuration file: {str(e)}")
        return default_config

def clean_content(content):
    """Remove problematic characters from file content"""
    if not isinstance(content, str):
        return content
    
    # Remove or replace problematic bytes/characters
    # Byte 0x90 often appears as a control character
    cleaned = content.replace('\x90', '')  # Remove the problematic byte
    
    # Remove other potential problematic control characters
    cleaned = ''.join(char for char in cleaned if ord(char) >= 32 or char in '\n\r\t')
    
    return cleaned

def sanitize_config(config):
    """Sanitize configuration values to ensure they're safe"""
    if not isinstance(config, dict):
        return config
    
    sanitized = {}
    for key, value in config.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_input(value)
        elif isinstance(value, list):
            sanitized[key] = [sanitize_input(item) if isinstance(item, str) else item for item in value]
        elif isinstance(value, dict):
            sanitized[key] = sanitize_config(value)  # Recursive for nested dicts
        else:
            sanitized[key] = value
    
    return sanitized

def save_config(config_data):
    """Save configuration to JSON file with robust error handling and encoding safety"""
    config_file = get_config_file_path()
    
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        # Sanitize all data before saving
        clean_config = sanitize_config(config_data)
        
        # Create a temporary file first
        temp_file = config_file + '.tmp'
        
        # Write to temporary file with safe ASCII encoding to avoid Windows issues
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(clean_config, f, indent=4, ensure_ascii=True, separators=(',', ': '))
        
        # Verify the temporary file can be read back
        with open(temp_file, 'r', encoding='utf-8') as f:
            test_load = json.load(f)  # This will raise an exception if the JSON is invalid
        
        # If we get here, the file is valid, so replace the original
        if os.path.exists(config_file):
            # Backup the old file first
            backup_file = config_file + '.bak'
            try:
                if os.path.exists(backup_file):
                    os.remove(backup_file)
                os.rename(config_file, backup_file)
            except:
                pass  # If backup fails, continue anyway
        
        os.rename(temp_file, config_file)
        
        st.success(f"Configuration saved successfully to: {os.path.basename(config_file)}")
        return True
        
    except PermissionError:
        st.error("❌ **Permission denied.** Please check if you have write access to the configuration directory.")
        st.info("💡 **Try running as administrator** or check your file permissions.")
        return False
    except OSError as e:
        st.error(f"❌ **File system error:** {str(e)}")
        st.info("💡 Check if the drive has enough space and the path is accessible.")
        return False
    except UnicodeEncodeError as e:
        st.error(f"❌ **Character encoding error:** {str(e)}")
        st.info("💡 Please remove any special characters from your input and try again.")
        return False
    except Exception as e:
        st.error(f"❌ **Unexpected error saving configuration:** {str(e)}")
        st.info("💡 Please try again or contact your system administrator.")
        # Clean up temporary file if it exists
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except:
            pass
        return False

def sanitize_input(text):
    """Remove potentially problematic characters from text input"""
    if not isinstance(text, str):
        return text
    
    # Remove the specific problematic byte 0x90 that's causing the error
    sanitized = text.replace('\x90', '')  # This is the main culprit
    
    # Remove other potentially problematic control characters but keep essential whitespace
    # Keep: newline (\n=10), carriage return (\r=13), tab (\t=9), space (32)
    # Remove: control characters below 32 except the ones above
    sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\n\r\t')
    
    # Additional cleanup for common Windows encoding issues
    # Remove other problematic bytes that can cause encoding errors
    problem_chars = [
        '\x80', '\x81', '\x82', '\x83', '\x84', '\x85', '\x86', '\x87',
        '\x88', '\x89', '\x8a', '\x8b', '\x8c', '\x8d', '\x8e', '\x8f',
        '\x90', '\x91', '\x92', '\x93', '\x94', '\x95', '\x96', '\x97',
        '\x98', '\x99', '\x9a', '\x9b', '\x9c', '\x9d', '\x9e', '\x9f'
    ]
    
    for char in problem_chars:
        sanitized = sanitized.replace(char, '')
    
    # Replace common Windows-1252 characters with their ASCII equivalents
    replacements = {
        '\u2018': "'",  # Left single quotation mark
        '\u2019': "'",  # Right single quotation mark  
        '\u201C': '"',  # Left double quotation mark
        '\u201D': '"',  # Right double quotation mark
        '\u2013': '-',  # En dash
        '\u2014': '-',  # Em dash
        '\u2026': '...'  # Horizontal ellipsis
    }
    
    for old, new in replacements.items():
        sanitized = sanitized.replace(old, new)
    
    # Limit length to prevent extremely long inputs
    return sanitized[:1000] if len(sanitized) > 1000 else sanitized

def main():
    """Main template editor interface"""
    st.title("📝 Report Template Editor")
    st.write("Customize your school report templates with your own information and styling.")
    
    # Load current configuration
    config = load_config()
    if not config:
        st.error("Could not load configuration. Please check your setup.")
        return
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏫 School Info", 
        "📞 Contact Details", 
        "📅 Academic Settings", 
        "💾 Save Changes"
    ])
    
    # Initialize the configuration updates
    updated_config = config.copy()
    
    with tab1:
        st.header("School Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            school_name = st.text_input(
                "School Name",
                value=config.get("school_name", ""),
                help="The main name of your school that appears at the top of reports",
                max_chars=100
            )
            updated_config["school_name"] = sanitize_input(school_name)
            
            school_subtitle = st.text_input(
                "School Subtitle/Motto", 
                value=config.get("school_subtitle", ""),
                help="Optional subtitle or motto (e.g., 'Excellence in Education')",
                max_chars=150
            )
            updated_config["school_subtitle"] = sanitize_input(school_subtitle)
        
        with col2:
            address = st.text_area(
                "School Address",
                value=config.get("address", ""),
                help="Full address of the school",
                height=100,
                max_chars=300
            )
            updated_config["address"] = sanitize_input(address)
        
        # Logo Configuration Section
        st.divider()
        st.subheader("🎨 School Logo Configuration")
        
        logo_col1, logo_col2 = st.columns(2)
        
        with logo_col1:
            logo_path = st.text_input(
                "Logo File Path",
                value=config.get("logo_path", ""),
                help="Full path to your school logo file (PNG, JPEG, or GIF)",
                placeholder="e.g., C:/path/to/your/school_logo.png",
                max_chars=500
            )
            updated_config["logo_path"] = sanitize_input(logo_path)
            
            # File validation
            if logo_path:
                import os
                if os.path.exists(logo_path):
                    file_ext = os.path.splitext(logo_path)[1].lower()
                    if file_ext in ['.png', '.jpg', '.jpeg', '.gif']:
                        st.success("✅ Logo file found and format is supported!")
                        try:
                            file_size = os.path.getsize(logo_path) / (1024 * 1024)  # Size in MB
                            st.info(f"📊 File size: {file_size:.2f} MB")
                            if file_size > 2:
                                st.warning("⚠️ Large file size may slow down report generation")
                        except:
                            pass
                    else:
                        st.error(f"❌ Unsupported file format: {file_ext}")
                        st.info("💡 Supported formats: PNG, JPEG, GIF")
                else:
                    st.error("❌ File not found at the specified path")
                    st.info("💡 Make sure to use the full absolute path to your logo file")
        
        with logo_col2:
            show_logo = st.checkbox(
                "Show Logo in Reports",
                value=config.get("show_logo", False),
                help="Enable this to display the school logo on all generated reports"
            )
            updated_config["show_logo"] = show_logo
            
            if show_logo:
                st.info("🎯 **Logo Display Settings:**")
                st.write("• Logo appears at the top of all PDF reports")
                st.write("• Recommended logo size: 300x300 pixels")
                st.write("• Logo is automatically resized to fit the report")
                st.write("• Square or rectangular logos work best")
                
                if not logo_path:
                    st.warning("⚠️ Please specify the logo file path above to display the logo")
            else:
                st.info("ℹ️ Logo display is disabled. Reports will show only text headers.")
        
        # Logo setup instructions
        with st.expander("📖 How to Set Up Your School Logo"):
            st.markdown("""
            **Step-by-Step Logo Setup:**
            
            1. **Prepare Your Logo File:**
               - Save your logo as PNG, JPEG, or GIF format
               - Recommended size: 300x300 pixels or similar square/rectangular dimensions
               - Keep file size under 2MB for best performance
            
            2. **Save Logo in Assets Folder:**
               - Copy your logo to: `assets/logos/` folder in your project
               - Or save it anywhere accessible on your computer
            
            3. **Configure Logo Path:**
               - Enter the full path to your logo file in the "Logo File Path" field above
               - Example: `C:/Users/YourName/Desktop/school_logo.png`
               - Or use the assets folder: `assets/logos/school_logo.png`
            
            4. **Enable Logo Display:**
               - Check the "Show Logo in Reports" checkbox above
               - Save your configuration
            
            5. **Test:**
               - Generate any report to see your logo appear at the top
            
            **Troubleshooting:**
            - Logo not showing? Check that the file path is correct
            - File format error? Try PNG format for best compatibility
            - Logo too big/small? The system automatically resizes it for reports
            """)
        
        # Quick logo directory creation
        if st.button("📁 Create Logo Directory", help="Create an assets/logos folder for storing your logo"):
            try:
                import os
                logo_dir = os.path.join(os.getcwd(), "assets", "logos")
                os.makedirs(logo_dir, exist_ok=True)
                st.success(f"✅ Logo directory created: {logo_dir}")
                st.info(f"💡 You can now copy your logo file to: {logo_dir}")
            except Exception as e:
                st.error(f"❌ Error creating directory: {e}")
    
    with tab2:
        st.header("Contact Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            email = st.text_input(
                "School Email",
                value=config.get("email", ""),
                help="Main email address for the school",
                max_chars=100
            )
            updated_config["email"] = sanitize_input(email)
        
        with col2:
            st.write("**Phone Numbers**")
            
            # Get current phone numbers
            current_phones = config.get("phone_numbers", [])
            
            # Allow editing phone numbers
            phone_1 = st.text_input(
                "Phone 1", 
                value=current_phones[0] if len(current_phones) > 0 else "",
                max_chars=20
            )
            phone_2 = st.text_input(
                "Phone 2", 
                value=current_phones[1] if len(current_phones) > 1 else "",
                max_chars=20
            )
            phone_3 = st.text_input(
                "Phone 3 (Optional)", 
                value=current_phones[2] if len(current_phones) > 2 else "",
                max_chars=20
            )
            
            # Build updated phone list (only include non-empty phones)
            updated_phones = []
            for phone in [phone_1, phone_2, phone_3]:
                sanitized_phone = sanitize_input(phone)
                if sanitized_phone and sanitized_phone.strip():
                    updated_phones.append(sanitized_phone.strip())
            
            updated_config["phone_numbers"] = updated_phones
    
    with tab3:
        st.header("Academic Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            academic_year = st.text_input(
                "Academic Year",
                value=config.get("academic_year", "2024-2025"),
                help="Current academic year (e.g., '2024-2025')",
                max_chars=20
            )
            updated_config["academic_year"] = sanitize_input(academic_year)
            
            current_term = st.selectbox(
                "Current Term",
                options=["1ST TERM", "2ND TERM", "3RD TERM"],
                index=2 if config.get("current_term") == "3RD TERM" else 0,
                help="Current academic term for reports"
            )
            updated_config["current_term"] = current_term
        
        with col2:
            st.subheader("Report Titles")
            
            report_titles = config.get("report_titles", {})
            
            midterm_title = st.text_input(
                "Mid-term Report Title",
                value=report_titles.get("Mid-term", "MID-TERM EXAMINATION REPORT"),
                help="Title for mid-term examination reports",
                max_chars=100
            )
            
            endterm_title = st.text_input(
                "End of Term Report Title", 
                value=report_titles.get("End of Term", "END OF TERM EXAMINATION REPORT"),
                help="Title for end of term examination reports",
                max_chars=100
            )
            
            updated_config["report_titles"] = {
                "Mid-term": sanitize_input(midterm_title),
                "End of Term": sanitize_input(endterm_title)
            }
    
    with tab4:
        st.header("Preview & Save Changes")
        
        # Show a preview of how the report header will look
        st.subheader("🔍 Report Header Preview")
        
        # Logo preview section
        if updated_config.get('show_logo') and updated_config.get('logo_path'):
            logo_preview = f"""
            <div style="text-align: center; padding: 10px; border: 1px dashed #999; border-radius: 5px; background-color: #f0f0f0; margin: 10px 0;">
                <p style="color: #666; margin: 0; font-size: 12px;">🎨 School Logo will appear here</p>
                <p style="color: #888; margin: 5px 0; font-size: 10px;">Logo: {updated_config['logo_path'].split('/')[-1]}</p>
            </div>
            """
            st.markdown(logo_preview, unsafe_allow_html=True)
        
        # Use basic HTML without special characters that might cause encoding issues
        preview_html = f"""
        <div style="text-align: center; padding: 20px; border: 2px solid #ccc; border-radius: 10px; background-color: #f8f9fa; margin: 10px 0;">
            <h2 style="color: #1A3380; margin: 5px 0;">{updated_config['school_name']}</h2>
            <p style="color: #666; margin: 5px 0; font-style: italic;">{updated_config['school_subtitle']}</p>
            <p style="color: #666; margin: 5px 0;">{updated_config['address']}</p>
            <p style="color: #666; margin: 5px 0;">
                Email: {updated_config['email']} | Phone: {' / '.join(updated_config['phone_numbers'])}
            </p>
            <div style="background-color: #1A3380; color: white; padding: 10px; border-radius: 5px; margin: 10px 0; font-weight: bold;">
                {updated_config['report_titles']['End of Term']} ({updated_config['current_term']} {updated_config['academic_year'].split('-')[0] if '-' in updated_config['academic_year'] else '2024'})
            </div>
        </div>
        """
        
        st.markdown(preview_html, unsafe_allow_html=True)
        
        # Configuration summary
        st.subheader("📋 Configuration Summary")
        
        config_summary = {
            "School Name": updated_config['school_name'],
            "Subtitle": updated_config['school_subtitle'],
            "Address": updated_config['address'],
            "Email": updated_config['email'],
            "Phone Numbers": ', '.join(updated_config['phone_numbers']) if updated_config['phone_numbers'] else 'None',
            "Logo Path": updated_config.get('logo_path', 'Not set'),
            "Show Logo": "Yes" if updated_config.get('show_logo') else "No",
            "Academic Year": updated_config['academic_year'],
            "Current Term": updated_config['current_term']
        }
        
        for key, value in config_summary.items():
            # Highlight logo settings
            if key in ["Logo Path", "Show Logo"]:
                if key == "Show Logo" and value == "Yes":
                    st.write(f"🎨 **{key}:** {value}")
                elif key == "Logo Path" and value != "Not set":
                    st.write(f"🖼️ **{key}:** {value}")
                else:
                    st.write(f"**{key}:** {value}")
            else:
                st.write(f"**{key}:** {value}")
        
        # Save changes button
        st.divider()
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button(
                "💾 Save All Changes",
                type="primary",
                use_container_width=True,
                help="Save all changes and update the report template"
            ):
                # Pre-save validation
                try:
                    st.info("🔍 **Validating data...**")
                    
                    # Check for any problematic characters in the config
                    for key, value in updated_config.items():
                        if isinstance(value, str):
                            if any(ord(c) < 32 and c not in '\n\r\t' for c in value):
                                st.warning(f"⚠️ Found control characters in {key}. They will be removed automatically.")
                        elif isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                if isinstance(sub_value, str) and any(ord(c) < 32 and c not in '\n\r\t' for c in sub_value):
                                    st.warning(f"⚠️ Found control characters in {key}.{sub_key}. They will be removed automatically.")
                    
                    # Show what will be saved
                    st.info("💾 **Preparing to save configuration...**")
                    
                    with st.spinner("Saving configuration..."):
                        success = save_config(updated_config)
                        
                        if success:
                            st.success("✅ **Configuration saved successfully!**")
                            st.info("🔄 **Next Steps:**")
                            st.write("1. Go to the **Reports** page")
                            st.write("2. Generate a **School Report PDF** to see your changes")
                            st.write("3. All future reports will use your new settings")
                            
                            # Balloons for success
                            st.balloons()
                            
                            # Small delay before refresh
                            import time
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("❌ **Error saving configuration.** Please check the error details above and try again.")
                            
                            # Provide additional troubleshooting info
                            st.info("🔧 **Troubleshooting Steps:**")
                            st.write("1. **Try clearing special characters** from all text fields")
                            st.write("2. **Check file permissions** - run as administrator if needed")
                            st.write("3. **Restart the application** and try again")
                            st.write("4. **Contact support** if the problem persists")
                            
                except Exception as e:
                    st.error(f"❌ **Validation Error:** {str(e)}")
                    st.info("💡 Please check your input for special characters or unusual formatting.")
        
        # Additional help
        st.divider()
        
        with st.expander("💡 Tips for Best Results"):
            st.markdown("""
            **Text Guidelines:**
            - Keep school name concise but descriptive
            - Include complete contact information
            - Double-check spelling and formatting
            - Use professional language for subtitles and mottos
            - Avoid special characters that might cause display issues
            
            **Phone Numbers:**
            - Enter phone numbers in your preferred format
            - Leave unused phone fields empty
            - Include country codes if needed
            
            **Academic Settings:**
            - Keep academic year in YYYY-YYYY format
            - Select the current term accurately
            - Customize report titles to match your school's style
            
            **Testing:**
            - Save your changes first
            - Go to Reports page to test PDF generation
            - Check that all information appears correctly
            
            **Troubleshooting:**
            - If saving fails, try removing special characters from text fields
            - Make sure you have write permissions to the application directory
            - Contact your system administrator if issues persist
            """)

# Run the main function
main()