import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random
from datetime import datetime, timedelta
import time

# Set up page config
st.set_page_config(layout="wide", page_title="Analytics Dashboard")

# Function to create a navigation bar
def create_navbar():
    cols = st.columns([1, 1, 1, 1, 1])
    with cols[0]:
        st.button("Trang chủ", key="nav_home", on_click=lambda: st.session_state.update({"page": "home"}))
    with cols[1]:
        st.button("Phân tích Web", key="nav_web", on_click=lambda: st.session_state.update({"page": "web"}))
    with cols[2]:
        st.button("Phân tích App", key="nav_app", on_click=lambda: st.session_state.update({"page": "app"}))
    with cols[3]:
        st.button("Phản hồi", key="nav_feedback", on_click=lambda: st.session_state.update({"page": "feedback"}))
    with cols[4]:
        st.button("Dữ liệu thô", key="nav_raw", on_click=lambda: st.session_state.update({"page": "raw"}))
    st.divider()

# Function to create footer
def create_footer():
    st.divider()
    cols = st.columns(3)
    with cols[0]:
        st.write("© 2023 Analytics Dashboard")
    with cols[1]:
        st.write("Liên hệ: contact@analytics.com")
    with cols[2]:
        st.write("Version 1.0.0")

# Generate fake data for products
def generate_products_data(n=50):
    categories = ["Thương mại điện tử", "Mạng xã hội", "Tin tức", "Giáo dục", "Giải trí"]
    platforms = ["Web", "App", "Cả hai"]
    
    data = {
        "Tên": [f"Sản phẩm {i+1}" for i in range(n)],
        "Loại": [random.choice(platforms) for _ in range(n)],
        "Danh mục": [random.choice(categories) for _ in range(n)],
        "Số người dùng": [random.randint(10000, 1000000) for _ in range(n)],
        "Điểm xếp hạng": [round(random.uniform(1, 10), 1) for _ in range(n)],
        "Trải nghiệm người dùng": [round(random.uniform(1, 10), 1) for _ in range(n)],
        "Hiệu suất": [round(random.uniform(1, 10), 1) for _ in range(n)],
        "Bảo mật": [round(random.uniform(1, 10), 1) for _ in range(n)],
        "Ngày cập nhật": [(datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d") for _ in range(n)]
    }
    
    df = pd.DataFrame(data)
    # Calculate total score
    df["Tổng điểm"] = df[["Điểm xếp hạng", "Trải nghiệm người dùng", "Hiệu suất", "Bảo mật"]].mean(axis=1).round(1)
    # Sort by total score
    df = df.sort_values("Tổng điểm", ascending=False).reset_index(drop=True)
    return df

# Generate sentiment data for apps
def generate_sentiment_data(apps, months=12):
    data = []
    for app in apps:
        for month in range(1, months + 1):
            month_name = datetime(2023, month, 1).strftime("%b")
            data.append({
                "App": app,
                "Tháng": month_name,
                "Tích cực": random.uniform(50, 95),
                "Trung lập": random.uniform(5, 25),
                "Tiêu cực": random.uniform(1, 20)
            })
    return pd.DataFrame(data)

# Generate time series download data for apps
def generate_download_data(apps, days=90):
    data = []
    today = datetime.now()
    for app in apps:
        for day in range(days):
            date = (today - timedelta(days=day)).strftime("%Y-%m-%d")
            data.append({
                "App": app,
                "Ngày": date,
                "Lượt tải": random.randint(1000, 10000)
            })
    return pd.DataFrame(data)

# Initialize session state for page navigation if not exists
if "page" not in st.session_state:
    st.session_state.page = "home"

# Generate data once
if "products_data" not in st.session_state:
    st.session_state.products_data = generate_products_data(50)

# Filter data based on time and category
def filter_data(data, time_option, category_option):
    filtered_data = data.copy()
    
    # Filter by time
    if time_option == "Tháng trước":
        one_month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        filtered_data = filtered_data[filtered_data["Ngày cập nhật"] >= one_month_ago]
    elif time_option == "3 tháng trước":
        three_months_ago = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        filtered_data = filtered_data[filtered_data["Ngày cập nhật"] >= three_months_ago]
    elif time_option == "6 tháng trước":
        six_months_ago = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
        filtered_data = filtered_data[filtered_data["Ngày cập nhật"] >= six_months_ago]
        
    # Filter by category
    if category_option != "Tất cả":
        filtered_data = filtered_data[filtered_data["Danh mục"] == category_option]
        
    return filtered_data

# Function to create a stacked bar chart
def create_stacked_bar(data, dimension_col, metric_cols, title):
    if len(data) == 0:
        return go.Figure()

    top_products = data.sort_values("Tổng điểm", ascending=False).head(10)
    
    # Prepare data for stacked bar
    fig = go.Figure()
    
    for col in metric_cols:
        fig.add_trace(go.Bar(
            y=top_products[dimension_col],
            x=top_products[col],
            name=col,
            orientation='h'
        ))
    
    fig.update_layout(
        title=title,
        barmode='stack',
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

# HOME PAGE
def render_home_page():
    st.title("Bảng xếp hạng và Phân tích")
    
    # Brief info section
    with st.expander("Thông tin về bảng xếp hạng", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("Là gì")
            st.write("Bảng xếp hạng này cung cấp đánh giá toàn diện về các ứng dụng web và di động, dựa trên nhiều tiêu chí như trải nghiệm người dùng, hiệu suất và bảo mật.")
        with col2:
            st.subheader("Tại sao")
            st.write("Giúp người dùng đưa ra quyết định sáng suốt dựa trên đánh giá khách quan và phân tích dữ liệu thay vì tiếp thị hoặc xu hướng.")
        with col3:
            st.subheader("Như thế nào")
            st.write("Dữ liệu được thu thập thông qua công cụ phân tích, đánh giá của chuyên gia và phản hồi từ người dùng thực tế.")
    
    # Filters
    st.subheader("Bộ lọc")
    col1, col2 = st.columns(2)
    with col1:
        time_option = st.selectbox(
            "Thời gian", 
            ["Tất cả", "Tháng trước", "3 tháng trước", "6 tháng trước"],
            key="home_time"
        )
    with col2:
        categories = ["Tất cả"] + list(st.session_state.products_data["Danh mục"].unique())
        category_option = st.selectbox("Danh mục", categories, key="home_category")
    
    # Filter data
    filtered_data = filter_data(st.session_state.products_data, time_option, category_option)
    
    # Metrics Row
    st.subheader("Tổng quan")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Tổng số Web/App", len(filtered_data))
    with col2:
        avg_score = filtered_data["Tổng điểm"].mean()
        st.metric("Điểm trung bình", f"{avg_score:.1f}")
    with col3:
        web_count = len(filtered_data[filtered_data["Loại"].isin(["Web", "Cả hai"])])
        st.metric("Tổng số Web", web_count)
    with col4:
        app_count = len(filtered_data[filtered_data["Loại"].isin(["App", "Cả hai"])])
        st.metric("Tổng số App", app_count)
    
    # Charts Row
    st.subheader("Phân tích hình ảnh")
    col1, col2 = st.columns(2)
    
    with col1:
        # Top products by rank
        top_products = filtered_data.head(10)
        fig = px.bar(
            top_products, 
            y="Tên", 
            x="Tổng điểm", 
            orientation='h',
            title="Top 10 sản phẩm theo xếp hạng",
            color="Tổng điểm",
            color_continuous_scale=px.colors.sequential.Bluered,
            height=400
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Category distribution
        category_counts = filtered_data["Danh mục"].value_counts().reset_index()
        category_counts.columns = ["Danh mục", "Số lượng"]
        
        fig = px.pie(
            category_counts,
            values="Số lượng",
            names="Danh mục",
            title="Phân bố theo danh mục",
            hole=0.4
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Ranking Table
    st.subheader("Bảng xếp hạng sản phẩm")
    st.dataframe(
        filtered_data[["Tên", "Loại", "Danh mục", "Điểm xếp hạng", "Trải nghiệm người dùng", "Hiệu suất", "Bảo mật", "Tổng điểm"]],
        height=400,
        use_container_width=True
    )

# WEB ANALYSIS PAGE
def render_web_page():
    st.title("Phân tích Web")
    
    # Brief info
    st.info("Phân tích chuyên sâu về hiệu suất và xếp hạng của các website. Sử dụng bộ lọc bên dưới để xem thông tin chi tiết theo thời gian và danh mục.")
    
    # Filters
    st.subheader("Bộ lọc")
    col1, col2 = st.columns(2)
    with col1:
        time_option = st.selectbox(
            "Thời gian", 
            ["Tất cả", "Tháng trước", "3 tháng trước", "6 tháng trước"],
            key="web_time"
        )
    with col2:
        categories = ["Tất cả"] + list(st.session_state.products_data["Danh mục"].unique())
        category_option = st.selectbox("Danh mục", categories, key="web_category")
    
    # Filter data for web only
    web_data = st.session_state.products_data[st.session_state.products_data["Loại"].isin(["Web", "Cả hai"])]
    filtered_web_data = filter_data(web_data, time_option, category_option)
    
    # Metrics Row
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Tổng số Web", len(filtered_web_data))
    with col2:
        avg_score = filtered_web_data["Tổng điểm"].mean() if len(filtered_web_data) > 0 else 0
        st.metric("Điểm trung bình", f"{avg_score:.1f}")
    
    # Top Web Products
    st.subheader("Top 10 Web theo tiêu chí")
    
    metric_cols = ["Điểm xếp hạng", "Trải nghiệm người dùng", "Hiệu suất", "Bảo mật"]
    fig = create_stacked_bar(
        filtered_web_data, 
        "Tên", 
        metric_cols, 
        "Top 10 Web với tỷ lệ các tiêu chí"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Web Custom Analysis
    st.subheader("Phân tích tùy chỉnh")
    
    # Name filter
    web_names = list(filtered_web_data["Tên"].unique())
    if len(web_names) > 0:
        selected_web = st.selectbox("Chọn Web", web_names, key="web_name_filter")
        selected_web_data = filtered_web_data[filtered_web_data["Tên"] == selected_web]
        
        # Display metrics
        st.write("Chi tiết điểm số")
        metrics_cols = st.columns(4)
        with metrics_cols[0]:
            st.metric("Điểm xếp hạng", selected_web_data["Điểm xếp hạng"].values[0])
        with metrics_cols[1]:
            st.metric("Trải nghiệm người dùng", selected_web_data["Trải nghiệm người dùng"].values[0])
        with metrics_cols[2]:
            st.metric("Hiệu suất", selected_web_data["Hiệu suất"].values[0])
        with metrics_cols[3]:
            st.metric("Bảo mật", selected_web_data["Bảo mật"].values[0])
    else:
        st.warning("Không có dữ liệu Web phù hợp với bộ lọc.")
    
    # Compare Webs
    st.subheader("So sánh Web")
    
    if len(web_names) >= 2:
        col1, col2 = st.columns(2)
        with col1:
            web_a = st.selectbox("Web A", web_names, key="web_a")
        with col2:
            web_names_b = [name for name in web_names if name != web_a]
            web_b = st.selectbox("Web B", web_names_b, key="web_b")
        
        if web_a and web_b:
            web_a_data = filtered_web_data[filtered_web_data["Tên"] == web_a]
            web_b_data = filtered_web_data[filtered_web_data["Tên"] == web_b]
            
            # Prepare comparison data
            comparison_data = []
            for metric in metric_cols:
                comparison_data.append({
                    "Tiêu chí": metric,
                    f"{web_a}": web_a_data[metric].values[0],
                    f"{web_b}": web_b_data[metric].values[0]
                })
            
            comparison_df = pd.DataFrame(comparison_data)
            
            # Create comparison chart
            fig = go.Figure()
            
            # Add traces for each web
            fig.add_trace(go.Bar(
                y=comparison_df["Tiêu chí"],
                x=comparison_df[web_a],
                name=web_a,
                orientation='h',
                marker=dict(color='#FF4B4B')
            ))
            
            fig.add_trace(go.Bar(
                y=comparison_df["Tiêu chí"],
                x=comparison_df[web_b],
                name=web_b,
                orientation='h',
                marker=dict(color='#1F77B4')
            ))
            
            fig.update_layout(
                barmode='group',
                title="So sánh các tiêu chí",
                height=300,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Vui lòng chọn hai Web khác nhau để so sánh.")
    else:
        st.warning("Cần ít nhất hai Web để thực hiện so sánh.")

# APP ANALYSIS PAGE
def render_app_page():
    st.title("Phân tích Ứng dụng")
    
    # Brief info
    st.info("Phân tích chuyên sâu về hiệu suất và xếp hạng của các ứng dụng di động. Sử dụng bộ lọc bên dưới để xem thông tin chi tiết theo thời gian và danh mục.")
    
    # Filters
    st.subheader("Bộ lọc")
    col1, col2 = st.columns(2)
    with col1:
        time_option = st.selectbox(
            "Thời gian", 
            ["Tất cả", "Tháng trước", "3 tháng trước", "6 tháng trước"],
            key="app_time"
        )
    with col2:
        categories = ["Tất cả"] + list(st.session_state.products_data["Danh mục"].unique())
        category_option = st.selectbox("Danh mục", categories, key="app_category")
    
    # Filter data for apps only
    app_data = st.session_state.products_data[st.session_state.products_data["Loại"].isin(["App", "Cả hai"])]
    filtered_app_data = filter_data(app_data, time_option, category_option)
    
    # Metrics Row
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Tổng số App", len(filtered_app_data))
    with col2:
        avg_score = filtered_app_data["Tổng điểm"].mean() if len(filtered_app_data) > 0 else 0
        st.metric("Điểm trung bình", f"{avg_score:.1f}")
    
    # Top App Products
    st.subheader("Top 10 App theo tiêu chí")
    
    metric_cols = ["Điểm xếp hạng", "Trải nghiệm người dùng", "Hiệu suất", "Bảo mật"]
    fig = create_stacked_bar(
        filtered_app_data, 
        "Tên", 
        metric_cols, 
        "Top 10 App với tỷ lệ các tiêu chí"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Sentiment Analysis
    st.subheader("Phân tích cảm xúc")
    
    # Generate sentiment data for top apps
    top_apps = filtered_app_data.head(5)["Tên"].tolist()
    
    if "sentiment_data" not in st.session_state:
        st.session_state.sentiment_data = generate_sentiment_data(top_apps)
    
    if len(top_apps) > 0:
        # Sentiment gauge
        avg_positive = st.session_state.sentiment_data["Tích cực"].mean()
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=avg_positive,
            title={'text': "Điểm tình cảm tích cực trung bình"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "green"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 75], 'color': "gray"},
                    {'range': [75, 100], 'color': "lightgreen"}
                ]
            }
        ))
        
        fig.update_layout(height=200)
        st.plotly_chart(fig, use_container_width=True)
        
        # Sentiment timeline
        sentiment_timeline = st.session_state.sentiment_data[st.session_state.sentiment_data["App"].isin(top_apps)]
        
        fig = px.bar(
            sentiment_timeline,
            x="Tháng",
            y="Tích cực",
            color="App",
            title="Diễn biến tình cảm tích cực theo thời gian cho Top 5 App",
            barmode="group"
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Không có dữ liệu App phù hợp với bộ lọc.")
    
    # App Custom Analysis
    st.subheader("Phân tích tùy chỉnh")
    
    # Filters for custom analysis
    app_names = list(filtered_app_data["Tên"].unique())
    app_types = ["Android", "iOS", "Cả hai"]
    
    col1, col2 = st.columns(2)
    with col1:
        if len(app_names) > 0:
            selected_app = st.selectbox("Chọn App", app_names, key="app_name_filter")
        else:
            selected_app = None
            st.warning("Không có App phù hợp với bộ lọc.")
    with col2:
        selected_type = st.selectbox("Loại", app_types, key="app_type_filter")
    
    if selected_app:
        selected_app_data = filtered_app_data[filtered_app_data["Tên"] == selected_app]
        
        # Display metrics
        st.write("Chi tiết điểm số")
        metrics_cols = st.columns(4)
        with metrics_cols[0]:
            st.metric("Điểm xếp hạng", selected_app_data["Điểm xếp hạng"].values[0])
        with metrics_cols[1]:
            st.metric("Trải nghiệm người dùng", selected_app_data["Trải nghiệm người dùng"].values[0])
        with metrics_cols[2]:
            st.metric("Hiệu suất", selected_app_data["Hiệu suất"].values[0])
        with metrics_cols[3]:
            st.metric("Bảo mật", selected_app_data["Bảo mật"].values[0])
    
    # Compare Apps
    st.subheader("So sánh App")
    
    if len(app_names) >= 2:
        # For Downloads
        st.write("So sánh lượt tải (Android)")
        
        # Select apps to compare
        selected_apps = st.multiselect("Chọn App để so sánh", app_names, default=app_names[:2] if len(app_names) >= 2 else [], key="compare_apps_download")
        
        if len(selected_apps) >= 2:
            # Generate download data
            if "download_data" not in st.session_state:
                st.session_state.download_data = generate_download_data(app_names)
            
            # Filter download data
            download_data = st.session_state.download_data[st.session_state.download_data["App"].isin(selected_apps)]
            
            # Create time series chart
            fig = px.line(
                download_data,
                x="Ngày",
                y="Lượt tải",
                color="App",
                title="So sánh lượt tải theo thời gian"
            )
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Chọn ít nhất 2 App để so sánh.")
        
        # For Sentiment
        st.write("So sánh tình cảm")
        
        # Select apps to compare
        selected_apps_sentiment = st.multiselect("Chọn App để so sánh", app_names, default=app_names[:2] if len(app_names) >= 2 else [], key="compare_apps_sentiment")
        
        if len(selected_apps_sentiment) >= 2:
            # Filter sentiment data
            sentiment_data = st.session_state.sentiment_data[st.session_state.sentiment_data["App"].isin(selected_apps_sentiment)]
            
            # Create a grouped bar chart
            fig = px.bar(
                sentiment_data,
                x="App",
                y=["Tích cực", "Trung lập", "Tiêu cực"],
                title="So sánh phân bố tình cảm",
                barmode="group"
            )
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Chọn ít nhất 2 App để so sánh.")
    else:
        st.warning("Cần ít nhất hai App để thực hiện so sánh.")

# FEEDBACK PAGE
def render_feedback_page():
    st.title("Phản hồi")
    
    # Filter for feedback type
    feedback_types = ["Đánh giá", "Câu hỏi", "Phản hồi", "Tư vấn", "Hợp tác"]
    feedback_type = st.selectbox("Loại phản hồi", feedback_types)
    
    # Feedback form
    st.subheader("Biểu mẫu phản hồi")
    
    with st.form("feedback_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Họ và tên")
            email = st.text_input("Email")
            phone = st.text_input("Số điện thoại")
        with col2:
            company = st.text_input("Công ty")
            role = st.text_input("Chức vụ")
            product = st.text_input("Sản phẩm quan tâm")
        
        message = st.text_area("Nội dung phản hồi", height=150)
        
        col1, col2 = st.columns([1, 5])
        with col1:
            submit_button = st.form_submit_button("Gửi phản hồi")
        
        if submit_button:
            st.success("Phản hồi của bạn đã được gửi thành công! Chúng tôi sẽ liên hệ lại trong thời gian sớm nhất.")
    
    # Raw data section
    st.subheader("Dữ liệu thô")
    st.write("Dữ liệu xếp hạng được nhúng từ Google Sheet")
    
    # Mock embedded Google Sheet
    st.info("Đang hiển thị dữ liệu được nhúng từ Google Sheet")
    st.dataframe(st.session_state.products_data, use_container_width=True)

# MAIN APP
def main():
    create_navbar()
    
    # Render the appropriate page based on session state
    if st.session_state.page == "home":
        render_home_page()
    elif st.session_state.page == "web":
        render_web_page()
    elif st.session_state.page == "app":
        render_app_page()
    elif st.session_state.page == "feedback":
        render_feedback_page()
    
    create_footer()

if __name__ == "__main__":
    main()