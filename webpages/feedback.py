import streamlit as st
from webpages.footer import footer
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json
from datetime import datetime
import uuid

# Google Sheets setup for saving feedback
@st.cache_resource
def init_feedback_sheets():
    """Initialize Google Sheets connection for feedback saving"""
    try:
        SERVICE_ACCOUNT_FILE = '/Users/vuhainam/Documents/PROJECT_DA/EdtechAgency/Ranking/2025/Criteria-Scrapers/credentials.json'
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        
        credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        client = gspread.authorize(credentials)
        
        return client
    except Exception as e:
        st.error(f"Error initializing feedback sheets: {e}")
        return None

def save_feedback_to_sheets(data, spreadsheet_id="15Eboneu5_6UfUNymCU_Dz1ZrhPCsoKECXY2MsUYBOP8"):
    """Save feedback data to Google Sheets"""
    try:
        client = init_feedback_sheets()
        if client is None:
            return False
        
        # Open the existing spreadsheet
        spreadsheet = client.open_by_key(spreadsheet_id)
        
        # Try to get or create 'FEEDBACK' worksheet
        try:
            worksheet = spreadsheet.worksheet('FEEDBACK')
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title='FEEDBACK', rows=1000, cols=20)
        
        # Get existing headers
        try:
            headers = worksheet.row_values(1)
        except:
            headers = []
        
        # If no headers exist, create them
        if not headers:
            headers = list(data.keys())
            worksheet.append_row(headers)
        
        # Ensure all data keys are in headers (add missing ones)
        missing_headers = [key for key in data.keys() if key not in headers]
        if missing_headers:
            headers.extend(missing_headers)
            worksheet.update('1:1', [headers])
        
        # Create row data in the same order as headers
        row_data = [str(data.get(header, '')) for header in headers]
        
        # Append the data
        worksheet.append_row(row_data)
        
        return True
    except Exception as e:
        st.error(f"Error saving feedback to sheets: {e}")
        return False

def validate_required_fields(data, required_fields):
    """Validate that all required fields are filled"""
    missing_fields = []
    for field in required_fields:
        value = data.get(field)
        if not value or (isinstance(value, str) and value.strip() == "") or value == "":
            missing_fields.append(field)
    return missing_fields

def main_feedback():

    with open('/Users/vuhainam/Documents/PROJECT_DA/EdtechAgency/RANKING/2025/webpages/feedback.css')as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

    # st.markdown("<h2 style='text-align: center; margin-bottom: 20px; background-image: linear-gradient(to right, #96d9a4, #c23640); color:#061c04;'>"
    #                 "Want to join the ranking system?</h2>", unsafe_allow_html=True) 
    st.markdown("""
        <style>
        .typewriter-subheader {
        display: flex;
        justify-content: center;
        margin-top: 20px;
        }

        .typewriter-subheader h2 {
        padding: 10px 20px;
        overflow: hidden;
        border-right: .15em solid white;
        white-space: nowrap;
        letter-spacing: .1em;
        animation:
            typing 3s steps(40, end),
            blink-caret .75s step-end infinite;
        font-size: 1.5em;
        font-weight: normal;
        color: white;
        background-image: linear-gradient(to right, #96d9a4, #c23640);
        border-radius: 10px;
        }
        @keyframes typing {
        from { width: 0 }
        to { width: 100% }
        }
        @keyframes blink-caret {
        from, to { border-color: transparent }
        50% { border-color: white; }
        }
        </style>

        <div class="typewriter-subheader">
        <h2>Want to join the ranking system</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Filter for feedback type
    feedback_types = ["Đánh giá", "Câu hỏi", "Phản hồi", "Tư vấn", "Hợp tác"]
    feedback_type = st.selectbox("Loại phản hồi", feedback_types)

    # Feedback form
    st.markdown(f"<h3>Biểu mẫu {feedback_type}</h3>", unsafe_allow_html=True)
    
    # Required fields indicator
    st.markdown("**<span style='color: red;'>*</span> Trường bắt buộc**", unsafe_allow_html=True)

    with st.form("feedback_form"):
        # Common fields with required/optional indicators
        st.markdown("#### Thông tin cơ bản")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Họ và tên *", help="Trường bắt buộc")
            email = st.text_input("Email *", help="Trường bắt buộc")
            phone = st.text_input("Số điện thoại", help="Trường tùy chọn")
        with col2:
            company = st.text_input("Công ty", help="Trường tùy chọn")
            role = st.text_input("Chức vụ", help="Trường tùy chọn")
            product = st.text_input("Sản phẩm quan tâm", help="Trường tùy chọn")
        
        # Define required fields for common section
        required_fields = ["name", "email"]
        
        # Specific fields based on feedback type
        # st.markdown("#### Thông tin chi tiết")
        with st.expander("**Thông tin chi tiết**"):

            if feedback_type == "Đánh giá":
                rating = st.slider("Điểm đánh giá *", 1, 5, 5, help="Trường bắt buộc")
                product_used = st.text_input("Sản phẩm đã sử dụng *", help="Trường bắt buộc")
                usage_period = st.selectbox("Thời gian sử dụng *", 
                                        ["", "Dưới 1 tháng", "1-3 tháng", "3-6 tháng", "6-12 tháng", "Trên 12 tháng"],
                                        help="Trường bắt buộc")
                pros = st.text_area("Điểm mạnh sản phẩm", height=100, help="Trường tùy chọn")
                cons = st.text_area("Điểm cần cải thiện", height=100, help="Trường tùy chọn")
                would_recommend = st.checkbox("Tôi sẵn sàng giới thiệu sản phẩm này cho người khác")
                required_fields.extend(["product_used", "usage_period"])
            
            elif feedback_type == "Câu hỏi":
                question_category = st.selectbox("Danh mục câu hỏi *", 
                                                ["", "Sản phẩm", "Dịch vụ", "Giá cả", "Kỹ thuật", "Khác"],
                                                help="Trường bắt buộc")
                urgency = st.radio("Mức độ khẩn cấp *", ["Thấp", "Trung bình", "Cao"], help="Trường bắt buộc")
                preferred_contact_method = st.selectbox("Phương thức liên hệ ưa thích", 
                                                    ["", "Email", "Điện thoại", "Cuộc họp trực tuyến"],
                                                    help="Trường tùy chọn")
                required_fields.extend(["question_category", "urgency"])
            
            elif feedback_type == "Phản hồi":
                feedback_category = st.selectbox("Danh mục phản hồi *", 
                                                ["", "Góp ý cải thiện", "Báo lỗi", "Đề xuất tính năng", "Khác"],
                                                help="Trường bắt buộc")
                severity = st.selectbox("Mức độ nghiêm trọng (đối với lỗi)", 
                                                ["Không áp dụng", "Thấp", "Trung bình", "Cao", "Nghiêm trọng"],
                                                help="Trường tùy chọn")
                reproducible = st.radio("Lỗi có thể tái hiện được không?", 
                                                ["Không rõ", "Có","Không"], horizontal=True, help="Trường tùy chọn")
                required_fields.append("feedback_category")

            elif feedback_type == "Tư vấn":
                topic_category = st.selectbox("Chủ đề tư vấn *", 
                                                ["", "Sản phẩm phù hợp", "Giải pháp tùy chỉnh", "Chi phí triển khai", "Quá trình triển khai", "Khác"],
                                                help="Trường bắt buộc")
                budget_category = st.selectbox("Ngân sách", 
                                                ["Chưa xác định", "Dưới 50 triệu", "50-100 triệu", "100-500 triệu", "Trên 500 triệu"],
                                                help="Trường tùy chọn")
                timeline_category = st.selectbox("Khung thời gian dự án", 
                                                ["Chưa xác định", "Dưới 1 tháng", "1-3 tháng", "3-6 tháng", "6-12 tháng", "Trên 12 tháng"],
                                                help="Trường tùy chọn")
                required_fields.append("topic_category")
                
            elif feedback_type == "Hợp tác":
                partnership_type = st.selectbox("Loại hình hợp tác *", 
                                                ["", "Đại lý", "Nhà phân phối", "Đối tác công nghệ", "Đối tác triển khai", "Khác"],
                                                help="Trường bắt buộc")
                industry = st.text_input("Ngành nghề kinh doanh *", help="Trường bắt buộc")
                partnership_goals = st.text_area("Mục tiêu hợp tác", 
                                                placeholder="Mô tả ngắn gọn mục tiêu hợp tác của bạn", 
                                                height=100, max_chars=1000, help="Trường tùy chọn")
                required_fields.extend(["partnership_type", "industry"])
            
        # Common message field
        message = st.text_area("Nội dung phản hồi *", height=150, help="Trường bắt buộc")
        required_fields.append("message")
        
        col1, col2 = st.columns([1, 5])
        with col1:
            submit_button = st.form_submit_button("Gửi phản hồi", type='secondary', icon="🔥")
        
        if submit_button:
            # Create entry with ID and timestamp
            entry = {
                "id": str(uuid.uuid4()),
                "created_at": datetime.now().isoformat(),
                "feedback_type": feedback_type,
                "name": name,
                "email": email,
                "phone": phone,
                "company": company,
                "role": role,
                "product": product,
                "message": message,
                "status": "Mới"
            }
            
            # Add specific fields based on feedback type
            if feedback_type == "Đánh giá":
                entry.update({
                    "rating": rating,
                    "product_used": product_used,
                    "usage_period": usage_period,
                    "pros": pros,
                    "cons": cons,
                    "would_recommend": would_recommend
                })
            elif feedback_type == "Câu hỏi":
                entry.update({
                    "question_category": question_category,
                    "urgency": urgency,
                    "preferred_contact_method": preferred_contact_method
                })
            elif feedback_type == "Phản hồi":
                entry.update({
                    "feedback_category": feedback_category,
                    "severity": severity,
                    "reproducible": reproducible
                })
            elif feedback_type == "Tư vấn":
                entry.update({
                    "topic_category": topic_category,
                    "budget_category": budget_category,
                    "timeline_category": timeline_category
                })
            elif feedback_type == "Hợp tác":
                entry.update({
                    "partnership_type": partnership_type,
                    "industry": industry,
                    "partnership_goals": partnership_goals
                })
            
            # Validate required fields
            missing_fields = validate_required_fields(entry, required_fields)
            
            if missing_fields:
                # Create user-friendly field names for Vietnamese
                field_names = {
                    "name": "Họ và tên",
                    "email": "Email", 
                    "message": "Nội dung phản hồi",
                    "product_used": "Sản phẩm đã sử dụng",
                    "usage_period": "Thời gian sử dụng",
                    "question_category": "Danh mục câu hỏi",
                    "urgency": "Mức độ khẩn cấp",
                    "feedback_category": "Danh mục phản hồi",
                    "topic_category": "Chủ đề tư vấn",
                    "partnership_type": "Loại hình hợp tác",
                    "industry": "Ngành nghề kinh doanh"
                }
                
                missing_names = [field_names.get(field, field) for field in missing_fields]
                st.error(f"❌ Vui lòng điền đầy đủ các trường bắt buộc: **{', '.join(missing_names)}**")
            else:
                # Try to save to Google Sheets
                with st.spinner('Đang lưu phản hồi...'):
                    success = save_feedback_to_sheets(entry)
                
                if success:
                    st.success("✅ Phản hồi của bạn đã được gửi thành công! Chúng tôi sẽ liên hệ lại trong thời gian sớm nhất.")
                    st.balloons()  # Add celebration effect
                else:
                    st.error("❌ Có lỗi xảy ra khi lưu phản hồi. Vui lòng thử lại sau hoặc liên hệ trực tiếp với chúng tôi.")

    st.divider()

    # Raw data section
    # st.markdown("<h3 style='text-align: center; margin-bottom: 20px; background-image: linear-gradient(to right, #4ced94, #4eabf2); color:#061c04;'>"
    #                 "Dữ liệu thô</h3>", unsafe_allow_html=True) 
    st.markdown("""
        <style>
        .typewriter-subheader2 {
        display: flex;
        justify-content: center;
        margin-top: 20px;
        }

        .typewriter-subheader2 h2 {
        padding: 10px 20px;
        overflow: hidden;
        border-right: .15em solid white;
        white-space: nowrap;
        letter-spacing: .1em;
        animation:
            typing 3s steps(40, end),
            blink-caret .75s step-end infinite;
        font-size: 1.5em;
        font-weight: normal;
        color: #000000;
        background-image: linear-gradient(to right, #4ced94, #4eabf2);
        border-radius: 10px;
        }
        @keyframes typing {
        from { width: 0 }
        to { width: 100% }
        }
        @keyframes blink-caret {
        from, to { border-color: transparent }
        50% { border-color: white; }
        }
        </style>

        <div class="typewriter-subheader2">
        <h2>Ranking Raw Data</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<h6 style='text-align: right'>"
                    "Dữ liệu xếp hạng được nhúng từ Google Sheet</h6>", unsafe_allow_html=True) 
    
    # Load existing raw data functionality
    import time
    with st.spinner("Đang truy xuất dữ liệu ..."):
        time.sleep(3)  # Reduced loading time

    # Google Sheets connection for raw data
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = '/Users/vuhainam/Documents/PROJECT_DA/EdtechAgency/Ranking/2025/Criteria-Scrapers/credentials.json'
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    gc = gspread.authorize(credentials)
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/15Eboneu5_6UfUNymCU_Dz1ZrhPCsoKECXY2MsUYBOP8"
    spreadsheet = gc.open_by_url(spreadsheet_url)

    sheet_name = st.radio('Select raw data sheet', ['WEB','APP'], horizontal=True)
    
    try:
        worksheet_input = spreadsheet.worksheet(sheet_name)
        header_row_position = 1    
        all_values = worksheet_input.get_all_values()
        header = all_values[header_row_position - 1]  
        data_rows = all_values[header_row_position:]  
        df = pd.DataFrame(data_rows, columns=header)
        
        def make_columns_unique(columns):
            seen = {}
            new_columns = []
            for col in columns:
                if col in seen:
                    seen[col] += 1
                    new_columns.append(f"{col}.{seen[col]}")
                else:
                    seen[col] = 0
                    new_columns.append(col)
            return new_columns

        df.columns = make_columns_unique(df.columns)
        
        # Display data with better formatting
        st.dataframe(df, use_container_width=True, height=400)
        
        # Add download option
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Tải xuống dữ liệu CSV",
            data=csv,
            file_name=f'ranking_data_{sheet_name}_{datetime.now().strftime("%Y%m%d")}.csv',
            mime='text/csv'
        )
        
    except Exception as e:
        st.error(f"Lỗi khi tải dữ liệu: {e}")

    footer()