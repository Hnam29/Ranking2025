import streamlit as st
from webpages.footer import footer

def main_feedback():
    # st.markdown("<h1 style='text-align: center;'>Phản hồi</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; margin-bottom: 20px; background-image: linear-gradient(to right, #96d9a4, #c23640); color:#061c04;'>"
                    "Want to join the ranking system?</h2>", unsafe_allow_html=True) 
    
    # # Filter for feedback type
    # feedback_types = ["Đánh giá", "Câu hỏi", "Phản hồi", "Tư vấn", "Hợp tác"]
    # feedback_type = st.selectbox("Loại phản hồi", feedback_types)
    
    # # Feedback form
    # # st.subheader(f"Biểu mẫu {feedback_type}")
    # st.markdown(f"<h4 style='text-align: center;'>Biểu mẫu {feedback_type}</h4>", unsafe_allow_html=True)

    # # --- Data Definitions (Example) ---
    # # You could store field definitions like this
    # form_structures = {
    #     "Đánh giá": [
    #         {"label": "Họ và tên", "widget": "text_input", "key": "dg_name"},
    #         {"label": "Email", "widget": "text_input", "key": "dg_email"},
    #         {"label": "Sản phẩm/Dịch vụ đánh giá", "widget": "text_input", "key": "dg_product"},
    #         {"label": "Xếp hạng (1-5)", "widget": "slider", "args": [1, 5, 3], "key": "dg_rating"}, # Example: Min, Max, Default
    #         {"label": "Nội dung đánh giá", "widget": "text_area", "kwargs": {"height": 150}, "key": "dg_message"},
    #     ],
    #     "Câu hỏi": [
    #         {"label": "Họ và tên", "widget": "text_input", "key": "ch_name"},
    #         {"label": "Email", "widget": "text_input", "key": "ch_email"},
    #         {"label": "Chủ đề câu hỏi", "widget": "text_input", "key": "ch_subject"},
    #         {"label": "Nội dung câu hỏi", "widget": "text_area", "kwargs": {"height": 150}, "key": "ch_message"},
    #     ],
    #     "Phản hồi": [ # Using your original structure
    #         {"label": "Họ và tên", "widget": "text_input", "key": "ph_name"},
    #         {"label": "Email", "widget": "text_input", "key": "ph_email"},
    #         {"label": "Số điện thoại", "widget": "text_input", "key": "ph_phone"},
    #         {"label": "Công ty", "widget": "text_input", "key": "ph_company"},
    #         {"label": "Chức vụ", "widget": "text_input", "key": "ph_role"},
    #         {"label": "Sản phẩm quan tâm", "widget": "text_input", "key": "ph_product"},
    #         {"label": "Nội dung phản hồi", "widget": "text_area", "kwargs": {"height": 150}, "key": "ph_message"},
    #     ],
    #     "Tư vấn": [
    #         {"label": "Họ và tên", "widget": "text_input", "key": "tv_name"},
    #         {"label": "Email", "widget": "text_input", "key": "tv_email"},
    #         {"label": "Số điện thoại", "widget": "text_input", "key": "tv_phone"},
    #         {"label": "Công ty", "widget": "text_input", "key": "tv_company"},
    #         {"label": "Lĩnh vực cần tư vấn", "widget": "text_input", "key": "tv_topic"},
    #         {"label": "Mô tả yêu cầu tư vấn", "widget": "text_area", "kwargs": {"height": 150}, "key": "tv_message"},
    #     ],
    #     "Hợp tác": [
    #         {"label": "Tên người liên hệ", "widget": "text_input", "key": "ht_contact_name"},
    #         {"label": "Tên công ty", "widget": "text_input", "key": "ht_company"},
    #         {"label": "Email công ty", "widget": "text_input", "key": "ht_email"},
    #         {"label": "Số điện thoại công ty", "widget": "text_input", "key": "ht_phone"},
    #         {"label": "Website công ty", "widget": "text_input", "kwargs":{"placeholder": "https://..."}, "key": "ht_website"},
    #         {"label": "Nội dung đề xuất hợp tác", "widget": "text_area", "kwargs": {"height": 150}, "key": "ht_message"},
    #     ]
    # }

    # # Dictionary to store submitted data
    # submitted_data = {}

    # with st.form(key=f"form_{feedback_type}", clear_on_submit=True): # Unique key for the form

    #     # Get the fields for the selected type, default to empty list if not found
    #     fields_to_render = form_structures.get(feedback_type, [])

    #     # You might want layout columns here, e.g., col1, col2 = st.columns(2)
    #     # and then alternate `with col1:` / `with col2:` based on field index

    #     for field_def in fields_to_render:
    #         label = field_def["label"]
    #         widget_type = field_def["widget"]
    #         key = field_def["key"] # Use the unique key
    #         args = field_def.get("args", []) # Positional arguments for widget
    #         kwargs = field_def.get("kwargs", {}) # Keyword arguments for widget

    #         # Render the widget based on its type
    #         if widget_type == "text_input":
    #             submitted_data[key] = st.text_input(label, *args, key=key, **kwargs)
    #         elif widget_type == "text_area":
    #             submitted_data[key] = st.text_area(label, *args, key=key, **kwargs)
    #         elif widget_type == "slider":
    #             submitted_data[key] = st.slider(label, *args, key=key, **kwargs)
    #         elif widget_type == "selectbox":
    #             submitted_data[key] = st.selectbox(label, *args, key=key, **kwargs)
    #         # Add other widget types (radio, number_input, etc.) as needed
    #         # Example:
    #         # elif widget_type == "number_input":
    #         #     submitted_data[key] = st.number_input(label, *args, key=key, **kwargs)

    #     # Submit button at the end
    #     submit_button = st.form_submit_button("Gửi phản hồi")

    # if submit_button:
    #     # Process the submitted_data dictionary here
    #     # For example, print it or send it somewhere
    #     st.success(f"Phản hồi loại '{feedback_type}' của bạn đã được gửi!")
    #     st.write("Dữ liệu đã gửi:")
    #     st.json(submitted_data) # Display the collected data

    from datetime import datetime
    import uuid

    # Filter for feedback type
    feedback_types = ["Đánh giá", "Câu hỏi", "Phản hồi", "Tư vấn", "Hợp tác"]
    feedback_type = st.selectbox("Loại phản hồi", feedback_types)

    # Feedback form
    st.markdown(f"<h3>Biểu mẫu {feedback_type}</h3>", unsafe_allow_html=True)

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
            # Tạo entry với ID và thời gian
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
            
            # Thêm các trường đặc thù theo loại phản hồi
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
            
            st.success("Phản hồi của bạn đã được gửi thành công! Chúng tôi sẽ liên hệ lại trong thời gian sớm nhất.")

    # Raw data section
    # st.markdown("<h2 style='text-align: center;'>Dữ liệu thô</h2>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; margin-bottom: 20px; background-image: linear-gradient(to right, #4ced94, #4eabf2); color:#061c04;'>"
                    "Dữ liệu thô</h3>", unsafe_allow_html=True) 
    
    st.write("Dữ liệu xếp hạng được nhúng từ Google Sheet")
    
    # Mock embedded Google Sheet
    st.info("Đang hiển thị dữ liệu được nhúng từ Google Sheet")

    import gspread
    from google.oauth2.service_account import Credentials
    import pandas as pd
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = '/Users/vuhainam/Documents/PROJECT_DA/EdtechAgency/Ranking/2025/Criteria-Scrapers/credentials.json'
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
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