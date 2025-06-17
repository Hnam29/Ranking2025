import streamlit as st
from webpages.footer import footer

def main_feedback():
    # st.markdown("<h1 style='text-align: center;'>Phản hồi</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; margin-bottom: 20px; background-image: linear-gradient(to right, #96d9a4, #c23640); color:#061c04;'>"
                    "Want to join the ranking system?</h2>", unsafe_allow_html=True) 

    # from datetime import datetime
    # import uuid

    # # Filter for feedback type
    # feedback_types = ["Đánh giá", "Câu hỏi", "Phản hồi", "Tư vấn", "Hợp tác"]
    # feedback_type = st.selectbox("Loại phản hồi", feedback_types)

    # # Feedback form
    # st.markdown(f"<h3>Biểu mẫu {feedback_type}</h3>", unsafe_allow_html=True)

    # with st.form("feedback_form"):
    #     # Common fields
    #     col1, col2 = st.columns(2)
    #     with col1:
    #         name = st.text_input("Họ và tên")
    #         email = st.text_input("Email")
    #         phone = st.text_input("Số điện thoại")
    #     with col2:
    #         company = st.text_input("Công ty")
    #         role = st.text_input("Chức vụ")
    #         product = st.text_input("Sản phẩm quan tâm")
        
    #     # Specific fields based on feedback type
    #     if feedback_type == "Đánh giá":
    #         rating = st.slider("Điểm đánh giá", 1, 5, 5)
    #         product_used = st.text_input("Sản phẩm đã sử dụng")
    #         usage_period = st.selectbox("Thời gian sử dụng", 
    #                                 ["Dưới 1 tháng", "1-3 tháng", "3-6 tháng", "6-12 tháng", "Trên 12 tháng"])
    #         pros = st.text_area("Điểm mạnh sản phẩm", height=100)
    #         cons = st.text_area("Điểm cần cải thiện", height=100)
    #         would_recommend = st.checkbox("Tôi sẵn sàng giới thiệu sản phẩm này cho người khác")
        
    #     elif feedback_type == "Câu hỏi":
    #         question_category = st.selectbox("Danh mục câu hỏi", 
    #                                         ["Sản phẩm", "Dịch vụ", "Giá cả", "Kỹ thuật", "Khác"])
    #         urgency = st.radio("Mức độ khẩn cấp", ["Thấp", "Trung bình", "Cao"])
    #         preferred_contact_method = st.selectbox("Phương thức liên hệ ưa thích", 
    #                                             ["Email", "Điện thoại", "Cuộc họp trực tuyến"])
        
    #     elif feedback_type == "Phản hồi":
    #         feedback_category = st.selectbox("Danh mục phản hồi", 
    #                                         ["Góp ý cải thiện", "Báo lỗi", "Đề xuất tính năng", "Khác"])
    #         severity = st.selectbox("Mức độ nghiêm trọng (đối với lỗi)", 
    #                                         ["Thấp", "Trung bình", "Cao", "Nghiêm trọng", "Không áp dụng"])
    #         reproducible = st.radio("Lỗi có thể tái hiện được không?", 
    #                                         ["Có","Không"],horizontal=True)

    #     elif feedback_type == "Tư vấn":
    #         topic_category = st.selectbox("Chủ đề tư vấn", 
    #                                         ["Sản phẩm phù hợp", "Giải pháp tùy chỉnh", "Chi phí triển khai", "Quá trình triển khai", "Khác"])
    #         budget_category = st.selectbox("Ngân sách", 
    #                                         ["Dưới 50 triệu", "50-100 triệu", "100-500 triệu", "Trên 500 triệu", "Chưa xác định"])
    #         timeline_category = st.selectbox("Khung thời gian dự án", 
    #                                         ["Dưới 1 tháng", "1-3 tháng", "3-6 tháng", "6-12 tháng", "Trên 12 tháng", "Chưa xác định"])
            
    #     elif feedback_type == "Hợp tác":
    #         partnership_type = st.selectbox("Loại hình hợp tác", 
    #                                         ["Đại lý", "Nhà phân phối", "Đối tác công nghệ", "Đối tác triển khai", "Khác"])
    #         industry = st.text_input("Ngành nghề kinh doanh")
    #         partnership_goals = st.text_area("Mục tiêu hợp tác", value='Mô tả ngắn gọn', height=100, max_chars=1000)
            
    #     # Common message field
    #     message = st.text_area("Nội dung phản hồi", height=150)
        
    #     col1, col2 = st.columns([1, 5])
    #     with col1:
    #         submit_button = st.form_submit_button("Gửi phản hồi")
        
    #     if submit_button:
    #         # Tạo entry với ID và thời gian
    #         entry = {
    #             "id": str(uuid.uuid4()),
    #             "created_at": datetime.now().isoformat(),
    #             "feedback_type": feedback_type,
    #             "name": name,
    #             "email": email,
    #             "phone": phone,
    #             "company": company,
    #             "role": role,
    #             "product": product,
    #             "message": message,
    #             "status": "Mới"
    #         }
            
    #         # Thêm các trường đặc thù theo loại phản hồi
    #         if feedback_type == "Đánh giá":
    #             entry.update({
    #                 "rating": rating,
    #                 "product_used": product_used,
    #                 "usage_period": usage_period,
    #                 "pros": pros,
    #                 "cons": cons,
    #                 "would_recommend": would_recommend
    #             })
    #         elif feedback_type == "Câu hỏi":
    #             entry.update({
    #                 "question_category": question_category,
    #                 "urgency": urgency,
    #                 "preferred_contact_method": preferred_contact_method
    #             })
    #         elif feedback_type == "Phản hồi":
    #             entry.update({
    #                 "feedback_category": feedback_category,
    #                 "severity": severity,
    #                 "reproducible": reproducible
    #             })
    #         elif feedback_type == "Tư vấn":
    #             entry.update({
    #                 "topic_category": topic_category,
    #                 "budget_category": budget_category,
    #                 "timeline_category": timeline_category
    #             })
    #         elif feedback_type == "Hợp tác":
    #             entry.update({
    #                 "partnership_type": partnership_type,
    #                 "industry": industry,
    #                 "partnership_goals": partnership_goals
    #             })
            
    #         st.success("Phản hồi của bạn đã được gửi thành công! Chúng tôi sẽ liên hệ lại trong thời gian sớm nhất.")

    import requests
    from google.oauth2 import service_account
    import json
    from datetime import datetime
    import uuid
    import gspread
    
    N8N_WEBHOOK_URL = "https://primary-production-9120.up.railway.app/webhook/b51e9e2a-24ea-409f-8906-a25ad87599e4"
    
    def init_feedback_sheets():
        """Initialize Google Sheets client for feedback"""
        try:
            service_account_info = st.secrets["GCP_SERVICE_ACCOUNT"]
            credentials = service_account.Credentials.from_service_account_info(
                service_account_info,
                scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            )
            gc = gspread.authorize(credentials)
            return gc
        except Exception as e:
            st.error(f"Error initializing Google Sheets: {e}")
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
    
    st.markdown("<h2 style='text-align: center; margin-bottom: 20px; background-image: linear-gradient(to right, #96d9a4, #c23640); color:#061c04;'>"
                "Want to join the ranking system?</h2>", unsafe_allow_html=True) 
    
    # Filter for feedback type
    feedback_types = ["Đánh giá", "Câu hỏi", "Phản hồi", "Tư vấn", "Hợp tác"]
    feedback_type = st.selectbox("Loại phản hồi", feedback_types)
    
    # Feedback form
    st.markdown(f"<h3>Biểu mẫu {feedback_type}</h3>", unsafe_allow_html=True)
    
    def send_to_n8n_webhook(data):
        """Send data to n8n webhook"""
        try:
            response = requests.post(
                N8N_WEBHOOK_URL,
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            response.raise_for_status()
            return True, response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Lỗi kết nối với hệ thống: {str(e)}")
            return False, None
        except Exception as e:
            st.error(f"Lỗi không xác định: {str(e)}")
            return False, None
    
    with st.form("feedback_form"):
        # Common fields
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Họ và tên")
            email = st.text_input("Email")
            phone = st.text_input("Số điện thoại")
        with col2:
            company = st.text_input("Công ty")
            role = st.text_input("Chức vụ")
            product = st.text_input("Sản phẩm quan tâm")
        
        # Specific fields based on feedback type
        if feedback_type == "Đánh giá":
            rating = st.slider("Điểm đánh giá", 1, 5, 5)
            product_used = st.text_input("Sản phẩm đã sử dụng")
            usage_period = st.selectbox("Thời gian sử dụng", 
                                    ["Dưới 1 tháng", "1-3 tháng", "3-6 tháng", "6-12 tháng", "Trên 12 tháng"])
            pros = st.text_area("Điểm mạnh sản phẩm", height=100)
            cons = st.text_area("Điểm cần cải thiện", height=100)
            would_recommend = st.checkbox("Tôi sẵn sàng giới thiệu sản phẩm này cho người khác")
        
        elif feedback_type == "Câu hỏi":
            question_category = st.selectbox("Danh mục câu hỏi", 
                                            ["Sản phẩm", "Dịch vụ", "Giá cả", "Kỹ thuật", "Khác"])
            urgency = st.radio("Mức độ khẩn cấp", ["Thấp", "Trung bình", "Cao"])
            preferred_contact_method = st.selectbox("Phương thức liên hệ ưa thích", 
                                                ["Email", "Điện thoại", "Cuộc họp trực tuyến"])
        
        elif feedback_type == "Phản hồi":
            feedback_category = st.selectbox("Danh mục phản hồi", 
                                            ["Góp ý cải thiện", "Báo lỗi", "Đề xuất tính năng", "Khác"])
            severity = st.selectbox("Mức độ nghiêm trọng (đối với lỗi)", 
                                            ["Thấp", "Trung bình", "Cao", "Nghiêm trọng", "Không áp dụng"])
            reproducible = st.radio("Lỗi có thể tái hiện được không?", 
                                            ["Có","Không"],horizontal=True)
    
        elif feedback_type == "Tư vấn":
            topic_category = st.selectbox("Chủ đề tư vấn", 
                                            ["Sản phẩm phù hợp", "Giải pháp tùy chỉnh", "Chi phí triển khai", "Quá trình triển khai", "Khác"])
            budget_category = st.selectbox("Ngân sách", 
                                            ["Dưới 50 triệu", "50-100 triệu", "100-500 triệu", "Trên 500 triệu", "Chưa xác định"])
            timeline_category = st.selectbox("Khung thời gian dự án", 
                                            ["Dưới 1 tháng", "1-3 tháng", "3-6 tháng", "6-12 tháng", "Trên 12 tháng", "Chưa xác định"])
            
        elif feedback_type == "Hợp tác":
            partnership_type = st.selectbox("Loại hình hợp tác", 
                                            ["Đại lý", "Nhà phân phối", "Đối tác công nghệ", "Đối tác triển khai", "Khác"])
            industry = st.text_input("Ngành nghề kinh doanh")
            partnership_goals = st.text_area("Mục tiêu hợp tác", value='Mô tả ngắn gọn', height=100, max_chars=1000)
            
        # Common message field
        message = st.text_area("Nội dung phản hồi", height=150)
        
        col1, col2 = st.columns([1, 5])
        with col1:
            submit_button = st.form_submit_button("Gửi phản hồi")
        
        if submit_button:
            # Validate required fields
            if not name or not email or not phone:
                st.error("Vui lòng điền đầy đủ thông tin bắt buộc: Họ tên, Email, Số điện thoại")
            else:
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
                
                # Show processing message
                with st.spinner("Đang xử lý phản hồi của bạn..."):
                    # Save to Google Sheets first
                    sheets_success = save_feedback_to_sheets(entry)
                    
                    # Send to n8n webhook
                    webhook_success, response = send_to_n8n_webhook(entry)
                    
                    # Determine overall success
                    if sheets_success and webhook_success:
                        st.success("Phản hồi của bạn đã được gửi thành công! Chúng tôi sẽ liên hệ lại trong thời gian sớm nhất.")
                        
                        # Optional: Show additional info based on urgency or type
                        if feedback_type == "Câu hỏi" and urgency == "Cao":
                            st.info("⚡ Do mức độ khẩn cấp cao, chúng tôi sẽ liên hệ với bạn trong vòng 2 giờ.")
                        elif feedback_type == "Tư vấn":
                            st.info("📞 Đội ngũ tư vấn sẽ liên hệ với bạn trong vòng 24 giờ để thảo luận chi tiết.")
                        
                        # Optional: Clear form by rerunning (you can comment this out if not needed)
                        # st.experimental_rerun()
                    elif sheets_success and not webhook_success:
                        st.warning("Phản hồi đã được lưu thành công! Tuy nhiên, hệ thống tự động liên hệ có thể gặp sự cố. Chúng tôi vẫn sẽ xử lý phản hồi của bạn.")
                    elif not sheets_success and webhook_success:
                        st.warning("Phản hồi đã được gửi thành công! Tuy nhiên, có thể có sự cố với việc lưu trữ dữ liệu. Chúng tôi sẽ liên hệ với bạn sớm nhất.")
                    else:
                        st.error("Có lỗi xảy ra khi gửi phản hồi. Vui lòng thử lại sau hoặc liên hệ trực tiếp với chúng tôi.")
                        st.info("🔍 Vui lòng kiểm tra kết nối internet và thử lại, hoặc liên hệ qua email/điện thoại để được hỗ trợ.")

    # Raw data section
    # st.markdown("<h2 style='text-align: center;'>Dữ liệu thô</h2>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; margin-bottom: 20px; background-image: linear-gradient(to right, #4ced94, #4eabf2); color:#061c04;'>"
                    "Dữ liệu thô</h3>", unsafe_allow_html=True) 
    
    st.write("Dữ liệu xếp hạng được nhúng từ Google Sheet")
    
    # Mock embedded Google Sheet
    st.info("Đang hiển thị dữ liệu được nhúng từ Google Sheet")

    # from google.oauth2.service_account import Credentials
    from google.oauth2 import service_account
    import gspread
    import pandas as pd
    # SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    # SERVICE_ACCOUNT_FILE = 'credentials.json'
    # credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    service_account_info = st.secrets["GCP_SERVICE_ACCOUNT"]
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
    gc = gspread.authorize(credentials)
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/15Eboneu5_6UfUNymCU_Dz1ZrhPCsoKECXY2MsUYBOP8"
    spreadsheet = gc.open_by_url(spreadsheet_url)

    sheet_name = st.radio('Select raw data sheet', ['WEB','APP'], horizontal=True)
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
    st.write(df)

    footer()
