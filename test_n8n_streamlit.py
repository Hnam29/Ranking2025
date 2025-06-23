import streamlit as st
import requests
import json
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Contact Form with Google Sheets",
    page_icon="📝",
    layout="wide"
)

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Google Sheets Configuration
    st.subheader("📊 Google Sheets Setup")
    
    # File input for service account JSON
    service_account_file = st.file_uploader(
        "Upload Service Account JSON",
        type=['json'],
        help="Upload your Google Service Account credentials JSON file"
    )
    
    # Google Sheet URL or ID input
    sheet_input = st.text_input(
        "Google Sheet URL or ID:",
        placeholder="Paste Google Sheet URL or just the sheet ID",
        help="You can paste the full URL or just the sheet ID"
    )
    
    # Extract sheet ID from URL if full URL provided
    sheet_id = ""
    if sheet_input:
        if "docs.google.com/spreadsheets" in sheet_input:
            # Extract ID from URL
            try:
                sheet_id = sheet_input.split('/d/')[1].split('/')[0]
                st.success(f"✅ Sheet ID extracted: {sheet_id[:20]}...")
            except:
                st.error("❌ Invalid Google Sheets URL format")
        else:
            # Assume it's already the ID
            sheet_id = sheet_input
            st.success(f"✅ Using Sheet ID: {sheet_id[:20]}...")
    
    sheet_name = st.text_input(
        "Sheet Name:",
        value="ContactForm",
        help="Name of the sheet tab (will be created if doesn't exist)"
    )
    
    st.divider()
    
    # N8N Configuration
    st.subheader("🔗 N8N Webhook Setup")
    webhook_url = st.text_input(
        "N8N Webhook URL:", 
        placeholder="https://your-n8n-instance.com/webhook/contact-form",
        help="Paste your n8n webhook URL here"
    )
    
    # Show current URL status
    if webhook_url:
        if webhook_url.startswith("http"):
            st.success(f"✅ Webhook URL looks good")
        else:
            st.error("❌ URL should start with http:// or https://")

# Function to setup Google Sheets connection
@st.cache_resource
def setup_google_sheets(service_account_info, sheet_id):
    """Setup Google Sheets connection"""
    try:
        # Define the scope
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Create credentials
        creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
        client = gspread.authorize(creds)
        
        # Open the spreadsheet
        spreadsheet = client.open_by_key(sheet_id)
        
        return client, spreadsheet
    except Exception as e:
        st.error(f"Error setting up Google Sheets: {str(e)}")
        return None, None

def ensure_sheet_exists(spreadsheet, sheet_name):
    """Create sheet if it doesn't exist and add headers"""
    try:
        # Try to get the worksheet
        worksheet = spreadsheet.worksheet(sheet_name)
        st.success(f"✅ Sheet '{sheet_name}' found")
    except gspread.WorksheetNotFound:
        # Create the worksheet if it doesn't exist
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols="20")
        st.success(f"✅ Sheet '{sheet_name}' created")
    
    # Check if headers exist, if not add them
    try:
        headers = worksheet.row_values(1)
        expected_headers = ["Timestamp", "Name", "Company", "Position", "Email", "Phone No", "Send Connection"]
        
        if not headers or headers != expected_headers:
            worksheet.insert_row(expected_headers, 1)
            st.info("📝 Headers added to sheet")
    except Exception as e:
        st.warning(f"Could not check/add headers: {str(e)}")
    
    return worksheet

def add_data_to_sheet(worksheet, form_data):
    """Add form data to Google Sheet"""
    try:
        # Prepare row data
        row_data = [
            form_data["timestamp"],
            form_data["name"],
            form_data["company"],
            form_data["position"],
            form_data["email"],
            form_data["phone_no"],
            form_data["send_connection"]
        ]
        
        # Append row
        worksheet.append_row(row_data)
        return True
    except Exception as e:
        st.error(f"Error adding data to sheet: {str(e)}")
        return False

# Main form
st.header("📝 Contact Information Form")

# Check if Google Sheets is configured
sheets_configured = service_account_file is not None and sheet_id != ""

if not sheets_configured:
    st.warning("⚠️ Please configure Google Sheets in the sidebar first")

with st.form("contact_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("👤 Full Name *", placeholder="Enter your full name")
        company = st.text_input("🏢 Company *", placeholder="Enter your company name")
        position = st.text_input("💼 Position *", placeholder="Enter your job position")
    
    with col2:
        email = st.text_input("📧 Email *", placeholder="Enter your email address")
        phone_no = st.text_input("📱 Phone Number", placeholder="Enter your phone number")
    
    st.divider()
    
    # Form validation - check if fields have content
    form_valid = (
        name.strip() != "" and 
        company.strip() != "" and 
        position.strip() != "" and 
        email.strip() != ""
    )
    
    if not form_valid:
        st.error("❌ Please fill in all required fields marked with *")
    
    submit = st.form_submit_button("🚀 Submit Form")

# Process form submission
if submit and form_valid:
    # Prepare form data
    form_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "name": name.strip(),
        "company": company.strip(),
        "position": position.strip(),
        "email": email.strip(),
        "phone_no": phone_no.strip(),
        "send_connection": "No"  # Default value, admin will change this in Google Sheets
    }
    
    success_count = 0
    total_operations = 2  # Google Sheets + N8N webhook
    
    # Google Sheets Integration
    if sheets_configured:
        st.subheader("📊 Saving to Google Sheets...")
        
        try:
            # Parse service account JSON
            service_account_info = json.load(service_account_file)
            
            with st.spinner("Connecting to Google Sheets..."):
                client, spreadsheet = setup_google_sheets(service_account_info, sheet_id)
                
                if client and spreadsheet:
                    worksheet = ensure_sheet_exists(spreadsheet, sheet_name)
                    
                    if add_data_to_sheet(worksheet, form_data):
                        st.success("✅ Data successfully saved to Google Sheets!")
                        success_count += 1
                        
                        # Show a preview of recent data
                        try:
                            recent_data = worksheet.get_all_records()[-5:]  # Last 5 records
                            if recent_data:
                                st.subheader("📋 Recent Entries")
                                df = pd.DataFrame(recent_data)
                                st.dataframe(df, use_container_width=True)
                        except:
                            pass
                    else:
                        st.error("❌ Failed to save data to Google Sheets")
                else:
                    st.error("❌ Failed to connect to Google Sheets")
                    
        except json.JSONDecodeError:
            st.error("❌ Invalid service account JSON file")
        except Exception as e:
            st.error(f"❌ Google Sheets error: {str(e)}")
    else:
        st.warning("⚠️ Google Sheets not configured - skipping")
        total_operations -= 1
    
    # N8N Webhook Integration
    if webhook_url and webhook_url.startswith("http"):
        st.subheader("🔗 Sending to N8N Webhook...")
        
        # Add additional data for N8N
        webhook_data = form_data.copy()
        webhook_data.update({
            "source": "streamlit_contact_form",
            "form_id": f"contact_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        })
        
        try:
            with st.spinner("Sending to N8N webhook..."):
                response = requests.post(
                    webhook_url,
                    json=webhook_data,
                    headers={
                        'Content-Type': 'application/json',
                        'User-Agent': 'Streamlit-Contact-Form'
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    st.success("✅ Data successfully sent to N8N!")
                    success_count += 1
                    
                    # Show response if available
                    try:
                        response_json = response.json()
                        with st.expander("📥 N8N Response"):
                            st.json(response_json)
                    except:
                        if response.text:
                            with st.expander("📥 N8N Response"):
                                st.text(response.text)
                else:
                    st.error(f"❌ N8N webhook error: {response.status_code} - {response.reason}")
                    
        except requests.exceptions.Timeout:
            st.error("❌ N8N webhook timeout")
        except requests.exceptions.ConnectionError:
            st.error("❌ Could not connect to N8N webhook")
        except Exception as e:
            st.error(f"❌ N8N webhook error: {str(e)}")
    else:
        st.warning("⚠️ N8N webhook not configured - skipping")
        total_operations -= 1
    
    # Final status
    st.divider()
    if success_count == total_operations and total_operations > 0:
        st.balloons()
        st.success(f"🎉 Form submitted successfully! ({success_count}/{total_operations} operations completed)")
    elif success_count > 0:
        st.warning(f"⚠️ Partial success: {success_count}/{total_operations} operations completed")
    else:
        st.error("❌ Form submission failed")

# Instructions
with st.expander("📖 Setup Instructions"):
    st.markdown("""
    ### Google Sheets Setup:
    1. **Create a Google Cloud Project** and enable Google Sheets API
    2. **Create a Service Account** and download the JSON credentials
    3. **Share your Google Sheet** with the service account email
    4. **Upload the JSON file** and paste your sheet URL/ID in the sidebar
    
    ### N8N Webhook Setup:
    1. **Create a webhook trigger** in your N8N workflow
    2. **Copy the webhook URL** and paste it in the sidebar
    3. **Add Google Sheets nodes** in N8N to process the data further
    
    ### Form Fields:
    - **Name, Company, Position, Email**: Required fields
    - **Phone Number**: Optional
    - **Send Connection**: Admin-only field (automatically set to "No", admin can change in Google Sheets)
    """)

# Show current configuration status
st.sidebar.divider()
st.sidebar.subheader("📋 Status")
if sheets_configured:
    st.sidebar.success("✅ Google Sheets configured")
else:
    st.sidebar.error("❌ Google Sheets not configured")

if webhook_url and webhook_url.startswith("http"):
    st.sidebar.success("✅ N8N webhook configured")
else:
    st.sidebar.error("❌ N8N webhook not configured")