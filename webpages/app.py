import streamlit as st
import pandas as pd
from streamlit_extras.dataframe_explorer import dataframe_explorer
from streamlit_extras.metric_cards import style_metric_cards
from webpages.footer import footer
from get_data_from_sqlite import execute_sql_to_dataframe

def main_app():

    with open('./webpages/app.css')as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

    # SECTIONS
    info_container = st.container()
    filter1_chart1_container = st.container()
    scorecard_charts_container = st.container()
    analysis_header_container = st.container()
    filter2_chart4_chart5_container = st.container()

    with info_container:

        st.markdown("<h2 style='text-align: center;'>App Dashboard</h2>", unsafe_allow_html=True)

        import base64
        def get_img_as_base64(file):
            with open(file, 'rb') as f:
                data = f.read()
            return base64.b64encode(data).decode()
        
        img = get_img_as_base64('./webpages/bg2.jpeg')
        page_bg_img = f"""
        <style>
            div[data-testid="stVerticalBlockBorderWrapper"]:nth-of-type(1) > div:nth-child(1) > div[data-testid="stVerticalBlock"] > div:nth-child(4) > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) {{
                background-image: url("data:image/jpeg;base64,{img}"); 
                border-radius: 5px;
                padding: 0 0 15px 10px;
                }}
        </style>
        """
        st.markdown(page_bg_img,unsafe_allow_html=True)
    
        st.subheader("""
                About APP,   
                - Ranking App consists of 590 apps from Google Play and App Store across different sectors
                    
                    - There are nearly 10 criteria that have been deeply research and implement to assess multiple aspects of a website
                        - Stakeholders: teacher, parent, investor, administrator, analyst 
                            - Objectives: 
                            - 1. Evaluate the overall quality of a single website
                            - 2. Identify the "best" website from a set of criteria 
                            - 3. Benchmark websites against each other or against ideal standards in the edtech domain
                            - 4. Create a scoring system that is transparent and justifiable
                """)

        st.markdown("---")

    with filter1_chart1_container:

        ######## MAIN ########
        chart_column, filter_column = st.columns([7.5,2.5],gap='small')
        with filter_column:
            sql_query1 = f"""
                SELECT DISTINCT segment as Segment FROM dim_ranking_app
                """
            segment = execute_sql_to_dataframe(sql_query1)
            segment_sel = st.selectbox("Select segment", segment['Segment'], index=None)

            sql_query2 = f"""
                SELECT DISTINCT category as Category FROM dim_ranking_app
                """
            category = execute_sql_to_dataframe(sql_query2)
            category_sel = st.selectbox("Select category", category['Category'], index=None)

            col1, col2 = st.columns([6,4])
            with col1:
                sql_query3 = f"""
                    SELECT d.edtech_name
                    FROM dim_ranking_app AS d
                    JOIN fact_ranking_app AS f ON d.edtech_url = f.edtech_url
                    WHERE d.app_type = 'Android' AND f.`download_-_11/24` > 0 AND f.`download_-_12/24` > 0 AND f.`download_-_01/25` > 0 AND f.`download_-_02/25` > 0
                    """
                # Add conditions dynamically
                conditions = []
                if segment_sel:
                    conditions.append(f"segment = '{segment_sel}'")
                if category_sel:
                    conditions.append(f"category = '{category_sel}'")

                # Append conditions if they exist
                if conditions:
                    sql_query3 += " AND " + " AND ".join(conditions)

                name = execute_sql_to_dataframe(sql_query3)
                app_name = st.selectbox("Select app", name['edtech_name'], index=None)
            with col2:
                st.warning('Note: IOS app has no download number!')

        with chart_column:

            dml_sql = f"""
                SELECT d.edtech_name, t.*
                FROM dim_ranking_app AS d
                JOIN transformed_app_grouped_criteria AS t ON d.edtech_url = t.edtech_url
                WHERE d.app_type = 'Android'
                """
            # Add conditions dynamically
            conditions = []
            if segment_sel:
                conditions.append(f"segment = '{segment_sel}'")
            if category_sel:
                conditions.append(f"category = '{category_sel}'")
            # if app_name:
            #     conditions.append(f"edtech_name = '{app_name}'")

            # Append conditions if they exist
            if conditions:
                dml_sql += " AND " + " AND ".join(conditions)
                # + " AND "  
            # Add LIMIT
            # dml_sql += " LIMIT 7"
            data4 = execute_sql_to_dataframe(dml_sql)
            
            import altair as alt
            # Bước 1: Tính tổng các cột cần thiết và sắp xếp dữ liệu gốc
            data4['total_score'] = data4['app_popularity'] + data4['app_scalability'] + data4['user_sentiment']
            sorted_data = data4.sort_values('total_score', ascending=False)

            # Bước 2: Tạo dữ liệu dạng dài (melted) với thứ tự đã được sắp xếp
            data_melted = sorted_data.melt(
                id_vars=['edtech_name', 'total_score'],  # Giữ lại cột total_score để sắp xếp
                value_vars=['app_popularity', 'app_scalability', 'user_sentiment'],
                var_name='variable',
                value_name='value'
            )

            # Tạo thứ tự hiển thị cho các biến
            data_melted['order'] = data_melted['variable'].map({
                'app_popularity': 1,
                'app_scalability': 2,
                'user_sentiment': 3
            })

            # Bước 3: Tạo biểu đồ với nhãn giá trị và sắp xếp
            def create_horizontal_stacked_bar_chart(data_melted):
                """Tạo biểu đồ cột chồng ngang với chiều cao động dựa trên số lượng dữ liệu."""
                
                # Sắp xếp tên edtech theo tổng điểm
                sort_order = data_melted['edtech_name'].unique().tolist()
                
                # Tính toán chiều cao dựa trên số lượng edtech_name duy nhất
                num_entities = len(sort_order)
                
                # Tính toán chiều cao động
                # Mỗi thanh có chiều cao cố định, tối thiểu là 300px, tối đa là 900px
                bar_height = 40  # Chiều cao mong muốn cho mỗi thanh
                min_height = 300  # Chiều cao tối thiểu của biểu đồ
                max_height = 900  # Chiều cao tối đa của biểu đồ
                
                # Tính toán chiều cao dựa trên số lượng entity và giới hạn trong khoảng min-max
                chart_height = max(min_height, min(max_height, num_entities * bar_height))
                
                # Tạo biểu đồ cơ bản
                base = alt.Chart(data_melted).encode(
                    y=alt.Y('edtech_name:N', 
                            sort=sort_order, 
                            title=None,
                            axis=alt.Axis(labelLimit=200)),  # Tăng giới hạn độ dài nhãn nếu cần
                    x=alt.X('value:Q', title="Điểm số"),
                    color=alt.Color('variable:N',
                                legend=alt.Legend(title="Tiêu chí"),
                                scale=alt.Scale(
                                    domain=['app_popularity', 'app_scalability', 'user_sentiment'],
                                    range=['#5470c6', '#91cc75', '#fac858']
                                )),
                    order='order:Q',
                    tooltip=['edtech_name', 'variable', 'value']
                )
                
                # Vẽ biểu đồ cột chồng
                bars = base.mark_bar()
                
                # Thêm placeholder cho text (không hiển thị nhãn)
                text = base.mark_text(
                    align='center',
                    baseline='middle',
                    dx=15,
                    color='black',
                    fontSize=10,
                    opacity=0  # Đặt opacity=0 để ẩn text hoàn toàn
                ).encode()
                
                # Kết hợp biểu đồ cột và placeholder text
                chart = (bars + text).properties(
                    width=600,
                    height=chart_height,  # Sử dụng chiều cao đã tính toán
                    title="So sánh ứng dụng theo các tiêu chí",
                    padding={"top": 10, "left": 10, "right": 0, "bottom": 10}
                )
                
                return chart

            # Tạo và hiển thị biểu đồ
            chart = create_horizontal_stacked_bar_chart(data_melted)
            st.altair_chart(chart, use_container_width=True)

        st.markdown('---')

    with scorecard_charts_container:
        scorecard_chart2_column, chart3_column = st.columns([4,6],gap='medium')

        with scorecard_chart2_column:

            if app_name is not None:
                # Fetch data from MySQL
                query = f""" 
                    SELECT 
                        d.edtech_name, 
                        '2024-11' AS month, f.`download_-_11/24` AS downloads, f.average_monthly_download 
                    FROM dim_ranking_app d
                    JOIN fact_ranking_app f ON d.edtech_url = f.edtech_url
                    WHERE d.edtech_name = '{app_name}' AND d.app_type = 'Android' AND f.`download_-_11/24` > 0 

                    UNION ALL

                    SELECT 
                        d.edtech_name, 
                        '2024-12' AS month, f.`download_-_12/24`, f.average_monthly_download 
                    FROM dim_ranking_app d
                    JOIN fact_ranking_app f ON d.edtech_url = f.edtech_url
                    WHERE d.edtech_name = '{app_name}' AND d.app_type = 'Android' AND f.`download_-_12/24` > 0

                    UNION ALL

                    SELECT 
                        d.edtech_name, 
                        '2025-01' AS month, f.`download_-_01/25`, f.average_monthly_download 
                    FROM dim_ranking_app d
                    JOIN fact_ranking_app f ON d.edtech_url = f.edtech_url
                    WHERE d.edtech_name = '{app_name}' AND d.app_type = 'Android' AND f.`download_-_01/25` > 0 

                    UNION ALL

                    SELECT 
                        d.edtech_name, 
                        '2025-02' AS month, f.`download_-_02/25`, f.average_monthly_download 
                    FROM dim_ranking_app d
                    JOIN fact_ranking_app f ON d.edtech_url = f.edtech_url
                    WHERE d.edtech_name = '{app_name}' AND d.app_type = 'Android' AND f.`download_-_02/25` > 0

                    ORDER BY month;
                """
                df = execute_sql_to_dataframe(query)
                if not df.empty:
                    # Convert 'month' to datetime format
                    df["month"] = pd.to_datetime(df["month"])

                    # Step 1: Calculate the average download number among get months
                    # download_columns = [col for col in df.columns if col.startswith('download_')]  # Select download columns
                    # df['avg_download'] = df[download_columns].mean(axis=1)
                    df['avg_download'] = df['downloads'].mean()
                    # Step 2: Get the latest month and the previous month
                    latest_month = df['month'].max()  # Assuming the 'month' column is already in datetime format
                    previous_month = df[df['month'] < latest_month]['month'].max()  # Get the previous month

                    # Get downloads for the latest and previous months
                    latest_download = df[df['month'] == latest_month]['downloads'].values[0]
                    previous_download = df[df['month'] == previous_month]['downloads'].values[0]

                    # Calculate the percentage change
                    percentage_change = ((latest_download - previous_download) / previous_download) * 100

                    # Step 3: Create Streamlit layout for displaying comparisons
                    col1, col2 = st.columns(2)
                    from datetime import datetime
                    latest_month = latest_month.strftime('%m/%y')
                    previous_month = previous_month.strftime('%m/%y')

                    with col1:
                        # Display the overall average download number
                        avg_download_value = df['avg_download'].mean()
                        total_avg_download_value = df['average_monthly_download'].mean()
                        avg_change = avg_download_value - total_avg_download_value
                        
                        # Format the values with periods as thousand separators and break down the label into two lines
                        formatted_avg_download = f"{avg_download_value:,.0f}".replace(",", ".")  # Convert to period-separated format
                        formatted_delta_value = f"{avg_change:,.0f}".replace(",", ".")  # Format delta as well
                        
                        # Add a line break in the label
                        delta_value = f"{formatted_delta_value} (Download number)"
                        col1.metric(label="Average Download\n", value=formatted_avg_download, delta=delta_value, delta_color='normal')

                    with col2:
                        # Calculate and format the percentage change
                        delta_value2 = f"{percentage_change:,.0f}%".replace(",", ".")  # Format with period separator
                        # Display download change with a line break in the label
                        col2.metric(label=f"Download: {latest_month} vs {previous_month}", 
                                    value=f"{latest_download:,.0f}".replace(",", "."), 
                                    delta=delta_value2, 
                                    delta_color='normal')

                    style_metric_cards(border_left_color="#41a327") 

                    # Calculate percentage change
                    df["fluctuation"] = df["downloads"].pct_change() * 100

                    # Format the fluctuation percentage
                    df["fluctuation_display"] = df["fluctuation"].apply(
                        lambda x: f"🟢 +{x:.2f}%" if x > 0 else f"🔴 {x:.2f}%" if pd.notna(x) else ""
                    )
                    import plotly.express as px
                    # Create line chart with annotations
                    fig = px.line(df, x="month", y="downloads", title=f"Download Trend for {app_name}", markers=True)

                    # Add dashed line for avg_download
                    fig.add_hline(y=df["average_monthly_download"].iloc[0], line_dash="dash", annotation_text="Avg Download", annotation_position="top left")

                    # Add labels for fluctuation percentage
                    for i, row in df.iterrows():
                        if i > 0:  # Skip first row since fluctuation can't be calculated
                            fig.add_annotation(
                                x=row["month"],
                                y=row["downloads"],
                                text=row["fluctuation_display"],
                                showarrow=True,
                                arrowhead=2,
                                ax=0,
                                ay=-30,
                                font=dict(color="green" if row["fluctuation"] > 0 else "red", size=12),
                            )

                    # Show chart
                    st.plotly_chart(fig)

                    with st.expander('Insights for you'):
                        # Get latest month's data
                        latest_month = df.iloc[-1]["month"].strftime("%Y-%m")
                        latest_downloads = df.iloc[-1]["downloads"]

                        # Average downloads
                        avg_download = df["average_monthly_download"].iloc[0]

                        # Biggest fluctuation alerts
                        max_increase = df["fluctuation"].max()
                        max_decrease = df["fluctuation"].min()
                        # Extract the month only if max_increase > 0, otherwise set max_increase_month to None
                        max_increase_month_value = df[df["fluctuation"] == max_increase]["month"].values[0] if max_increase > 0 else None
                        # If max_increase_month_value is not None, process it
                        if max_increase_month_value is not None:
                            max_increase_month = pd.to_datetime(max_increase_month_value).strftime("%Y-%m")
                        else:
                            max_increase_month = None  # Or set some default value
                        
                        # Extract the month only if max_decrease < 0, otherwise set max_decrease_month to None
                        max_decrease_month_value = df[df["fluctuation"] == max_decrease]["month"].values[0] if max_decrease < 0 else None
                        # If max_decrease_month_value is not None, process it
                        if max_decrease_month_value is not None:
                            max_decrease_month = pd.to_datetime(max_decrease_month_value).strftime("%Y-%m")
                        else:
                            max_decrease_month = None  # Or set some default value
                            
                        if max_increase > 20:
                            st.success(f"🚀 **Big win!** In {max_increase_month}, downloads increased by **{max_increase:.1f}%**. Find what worked and double down!")
                        if max_decrease < -20:
                            st.error(f"🔻 **Significant drop!** In {max_decrease_month}, downloads fell by **{max_decrease:.1f}%**. Investigate and take action!")
                        
                        # Fluctuation trends
                        if df["fluctuation"].dropna().gt(0).sum() == len(df) - 1:
                            st.info("📈 **Your app has consistently grown in downloads!** Keep up the momentum!")
                        elif df["fluctuation"].dropna().lt(0).sum() == len(df) - 1:
                            st.warning("📉 **Your downloads have been declining over time.** It may be time to rethink your strategy.")
                        elif df["fluctuation"].dropna().abs().mean() > 15:
                            st.warning("⚖️ **Your download numbers fluctuate a lot!** Consider analyzing seasonal effects or user engagement.")

                        # Overall performance insight
                        if latest_downloads > avg_download:
                            st.success(f"🚀 **Good news!** In {latest_month}, your downloads (**{int(latest_downloads)}**) are **above the average ({int(avg_download)})**! Keep up the great work!")
                        else:
                            st.warning(f"⚠️ **Heads up!** In {latest_month}, your downloads (**{int(latest_downloads)}**) dropped **below the average ({int(avg_download)})**. You may want to analyze the cause.")

                else:
                    st.error("DataFrame is empty. Cannot plot the average download line.")
                    
            else:
                st.error('Please select an app to activate this chart')

   
        with chart3_column:
        
            if app_name:
                import plotly.graph_objects as go
                from datetime import datetime, timedelta
                import random
                import numpy as np

                # Fetch the min and max dates from the database
                sql_date_range = f"""
                    SELECT MIN(date) AS min_date, MAX(date) AS max_date
                    FROM fact_ranking_app_review f
                    INNER JOIN dim_ranking_app d
                    ON f.app_id = d.edtech_id
                    WHERE d.edtech_name = '{app_name}' 
                """
                date_range_df = execute_sql_to_dataframe(sql_date_range)

                # Extract min and max date from the result
                # min_available_date = pd.to_datetime(date_range_df['min_date'].iloc[0]).date()
                min_date_value = pd.to_datetime(date_range_df['min_date'].iloc[0])
                if pd.notna(min_date_value):
                    min_available_date = min_date_value.date()
                else:
                    min_available_date = None
                    
                # max_available_date = pd.to_datetime(date_range_df['max_date'].iloc[0]).date()
                max_date_value = pd.to_datetime(date_range_df['max_date'].iloc[0])
                if pd.notna(min_date_value):
                    max_available_date = max_date_value.date()
                else:
                    max_available_date = None
                    
                # Lưu trữ giá trị mặc định trong session state để dùng cho nút reset
                if 'default_min_date' not in st.session_state:
                    st.session_state.default_min_date = min_available_date
                if 'default_max_date' not in st.session_state:
                    st.session_state.default_max_date = max_available_date

                # Tạo hàm reset cho nút
                def reset_dates():
                    st.session_state.start = st.session_state.default_min_date
                    st.session_state.end = st.session_state.default_max_date

                # Streamlit UI: Set date inputs with min/max range
                col1, col2, reset_col = st.columns([2.1, 2.1, 0.7])
                if min_available_date is not None and max_available_date is not None:
                    start_date = col1.date_input('Start date', 
                                                min_value=min_available_date, 
                                                max_value=max_available_date, 
                                                value=min_available_date,  # Default to min_date
                                                format='YYYY-MM-DD', 
                                                key='start')
    
                    end_date = col2.date_input('End date', 
                                            min_value=min_available_date, 
                                            max_value=max_available_date, 
                                            value=max_available_date,  # Default to max_date
                                            format='YYYY-MM-DD', 
                                            key='end')
                else:
                    col1.info('No start date')
                    col2.info('No end date')

                reset_col.button("Reset date", on_click=reset_dates, help="Reset dates to default range",use_container_width=True)

                # Ensure start_date and end_date have valid values
                start_date = start_date if start_date else min_available_date
                end_date = end_date if end_date else max_available_date

                # Validate date inputs
                if end_date < start_date:
                    st.error("End date phải lớn hơn hoặc bằng Start date.")
                    end_date = start_date

                def create_sentiment_timeline_chart(df):
                    """Creates a sentiment timeline chart with stacked bars for sentiment proportions and a line plot."""
                    if df.empty:
                        return None
                        
                    fig = go.Figure()
                    
                    fig.add_trace(go.Bar(
                        x=df['datetime'],
                        y=df['positive_pct'],
                        name='Positive',
                        marker=dict(color='lightgreen'),
                        hovertemplate='%{y:.1%}<extra>Positive</extra>'  # Cải thiện tooltip
                    ))

                    fig.add_trace(go.Bar(
                        x=df['datetime'],
                        y=df['neutral_pct'],
                        name='Neutral',
                        marker=dict(color='yellow'),
                        hovertemplate='%{y:.1%}<extra>Neutral</extra>'
                    ))

                    fig.add_trace(go.Bar(
                        x=df['datetime'],
                        y=df['negative_pct'],
                        name='Negative',
                        marker=dict(color='tomato'),
                        hovertemplate='%{y:.1%}<extra>Negative</extra>'
                    ))

                    # Add the review count line
                    fig.add_trace(go.Scatter(
                        x=df['datetime'],
                        y=df['review_count'],
                        name='Review Count',
                        yaxis='y2',
                        mode='lines+markers',
                        line=dict(color='gray'),
                        hovertemplate='%{y} reviews<extra></extra>'
                    ))

                    # Update layout for dual axes and percentage formatting
                    fig.update_layout(
                        title='Sentiment Timeline (Proportions)',
                        xaxis=dict(title='Date'),
                        yaxis=dict(
                            title='Sentiment Percentage', 
                            side='left', 
                            tickformat=".0%",
                            range=[0, 1]  # Đảm bảo trục y luôn từ 0-100%
                        ),
                        yaxis2=dict(
                            title='Review Count', 
                            side='right', 
                            overlaying='y', 
                            tickmode='linear',
                            dtick=max(1, int(df['review_count'].max() / 10))  # Tối ưu ticks dựa trên data
                        ),
                        legend=dict(
                            x=0, 
                            y=1.1,
                            orientation='h'  # Hiển thị legend ngang để tiết kiệm không gian
                        ),
                        barmode='stack',  # Stack bars
                        height=500,
                        width=700,
                        hovermode='x unified'  # Hiển thị tất cả hover ở cùng một thời điểm
                    )
                    
                    return fig

                # SQL Query with dynamic date filtering
                sql_query_timeline = f"""
                    SELECT f.content AS review_content,
                        f.date,
                        f.`Positive` AS positive_rate,
                        f.`Neutral` AS neutral_rate,
                        f.`Negative` AS negative_rate
                    FROM dim_ranking_app d
                    INNER JOIN fact_ranking_app_review f 
                    ON d.edtech_id = f.app_id
                    WHERE d.edtech_name = '{app_name}' 
                    AND f.date BETWEEN '{start_date}' AND '{end_date}'
                """

                # Fetch and process data
                data_timeline = execute_sql_to_dataframe(sql_query_timeline)

                # Convert date column
                data_timeline['date'] = pd.to_datetime(data_timeline['date'])

                # Apply date filtering
                data_timeline = data_timeline[(data_timeline['date'] >= pd.to_datetime(start_date)) &
                                            (data_timeline['date'] <= pd.to_datetime(end_date))]

                # Aggregate data by date
                df_transformed = data_timeline.groupby('date').agg(
                    review_count=('review_content', 'count'),
                    positive=('positive_rate', 'sum'),
                    neutral=('neutral_rate', 'sum'),
                    negative=('negative_rate', 'sum')
                ).reset_index()

                # Calculate the proportion of each sentiment
                df_transformed['total_reviews'] = df_transformed['positive'] + df_transformed['neutral'] + df_transformed['negative']
                df_transformed['positive_pct'] = (df_transformed['positive'] / df_transformed['total_reviews']).replace(0, np.nan).fillna(0) 
                df_transformed['neutral_pct'] = (df_transformed['neutral'] / df_transformed['total_reviews']).replace(0, np.nan).fillna(0)
                df_transformed['negative_pct'] = (df_transformed['negative'] / df_transformed['total_reviews']).replace(0, np.nan).fillna(0)

                # Rename date column for plotting
                df_transformed.rename(columns={'date': 'datetime'}, inplace=True)
                
                # Create and display the chart
                fig = create_sentiment_timeline_chart(df_transformed)
                if fig:
                    # Hiển thị tổng số đánh giá trong khoảng thời gian
                    total_reviews = df_transformed['review_count'].sum()
                    positive_pct = (df_transformed['positive'].sum() / df_transformed['total_reviews'].sum()) * 100
                    negative_pct = (df_transformed['negative'].sum() / df_transformed['total_reviews'].sum()) * 100
                    neutral_pct = (df_transformed['neutral'].sum() / df_transformed['total_reviews'].sum()) * 100
                    review, pos, neu, neg = st.columns([1,1,1,1],gap='large')
                    review.metric(label="⌛ Total reviews", value=f"{total_reviews:,}")
                    pos.metric(label="😊 Positive rate", value=f"{positive_pct:.1f}%")
                    neu.metric(label="😐 Neutral rate", value=f"{neutral_pct:.1f}%")
                    neg.metric(label="😔 Negative rate", value=f"{negative_pct:.1f}%")

                    st.plotly_chart(fig, use_container_width=True)
                    
                    # # Hiển thị thông tin tổng quan
                    # with st.expander('Insights for you'):
                    #     # st.markdown(f"""
                    #     # **Tổng quan dữ liệu cảm xúc người dùng {app_name} từ {start_date} đến {end_date}**""")
                    #     st.markdown(f"<h4 style='text-align: center;'>Tổng quan dữ liệu cảm xúc người dùng {app_name} (từ {start_date} đến {end_date})</h4>", unsafe_allow_html=True)

                    #     st.info(f'Tổng số đánh giá: **{total_reviews:,}**')
                    #     st.success(f'Tỷ lệ đánh giá tích cực: **{positive_pct:.1f}%**')
                    #     st.warning(f'Tỷ lệ đánh giá trung tính: **{neutral_pct:.1f}%**')
                    #     st.error(f'Tỷ lệ đánh giá tiêu cực: **{negative_pct:.1f}%**')

                subcol1, subcol2 = st.columns([4.5,5.5])
                with subcol1:
                    sql_query_gauge = f"""
                        SELECT f.star_number FROM dim_ranking_app d
                        INNER JOIN fact_ranking_app f 
                        ON d.edtech_url = f.edtech_url
                        WHERE d.edtech_name = '{app_name}'
                        """
                    star_rate = execute_sql_to_dataframe(sql_query_gauge)

                    # st.markdown("<h6 style='text-align: center;'>Sentiment Metric</h6>", unsafe_allow_html=True)
                    import plotly.graph_objects as go

                    def create_gauge_chart(sentiment_score):
                        """Creates a gauge chart for sentiment score (0-5)."""

                        fig = go.Figure(go.Indicator(
                            domain={'x': [0, 1], 'y': [0, 1]},
                            value=sentiment_score,
                            mode="gauge+number",
                            # title={'text': "Sentiment Score (0-5)"},
                            gauge={
                                'axis': {'range': [0, 5]},  # Explicitly setting 0 as lower bound
                                'bar': {'color': "darkblue", 'thickness': 0.3},  # Increase thickness
                                'steps': [
                                    {'range': [0, 1], 'color': "red"},
                                    {'range': [1, 2], 'color': "orange"},
                                    {'range': [2, 3], 'color': "yellow"},
                                    {'range': [3, 4], 'color': "green"},
                                    {'range': [4, 5], 'color': "purple"}],
                                'threshold': {
                                    'line': {'color': "white", 'width': 6},  # Increase width for visibility
                                    'thickness': 0.7,  # Increase thickness
                                    'value': sentiment_score}}))

                        # Update layout for better visibility
                        fig.update_layout(
                            height=200,  # Increase height
                            width=400,   # Increase width
                            margin=dict(l=20, r=20, t=50, b=20)  # Reduce margins slightly
                        )

                        return fig
                    
                    sentiment_score = star_rate["star_number"].iloc[0]  # Convert Series to a single float
                    fig = create_gauge_chart(sentiment_score)
                    st.plotly_chart(fig)

                with subcol2:
                    # Keywords input
                    keywords_input = st.text_input('Type your demand keywords (separate by comma if you have many keywords)')
                    keywords = [kw.strip() for kw in keywords_input.split(',')] if keywords_input else []
                    keywords = [kw for kw in keywords if kw]  # Remove any empty keywords

                    # Simple LIKE condition for initial filtering
                    like_conditions = []
                    for kw in keywords:
                        safe_kw = kw.replace("'", "''")
                        like_conditions.append(f"LOWER(f.content) LIKE LOWER('%{safe_kw}%')")
                    
                    combined_condition = " OR ".join(like_conditions)
                    
                    # Construct SQL query with minimal complexity
                    sql_query_keyword = f"""
                        SELECT 
                            f.content AS review_content,
                            f.date,
                            f.`Positive` AS positive_rate,
                            f.`Neutral` AS neutral_rate,
                            f.`Negative` AS negative_rate
                        FROM dim_ranking_app d
                        INNER JOIN fact_ranking_app_review f 
                        ON d.edtech_id = f.app_id
                        WHERE d.edtech_name = '{app_name}'
                        AND ({combined_condition})
                    """
                    
                    # Fetch data
                    data_keyword = execute_sql_to_dataframe(sql_query_keyword)
                    
                    # Post-process in Python to filter actual matches and add keyword column
                    if data_keyword is not None and not data_keyword.empty:
                        filtered_rows = []
                        
                        for _, row in data_keyword.iterrows():
                            text = row['review_content'].lower()
                            for kw in keywords:
                                kw_lower = kw.lower()
                                # Check if the keyword exists in the review content
                                if kw_lower in text:
                                    # Create a copy to avoid modifying the original row
                                    new_row = row.copy()
                                    new_row['keyword'] = kw
                                    filtered_rows.append(new_row)
                                    break  # Only match the first keyword found
                        
                        if filtered_rows:
                            filtered_df = pd.DataFrame(filtered_rows)
                            
                            import plotly.graph_objects as go

                            # Aggregate sentiment scores and count total reviews
                            keyword_sentiment = filtered_df.groupby('keyword').agg({
                                'positive_rate': 'mean',
                                'neutral_rate': 'mean',
                                'negative_rate': 'mean',
                                'review_content': 'count'  # Count total reviews per keyword
                            }).reset_index()

                            keyword_sentiment.rename(columns={'review_content': 'review_count'}, inplace=True)

                            # Define colors
                            sentiment_colors = {
                                "positive_rate": "#4CAF50",  # Green
                                "neutral_rate": "#FFC107",   # Yellow
                                "negative_rate": "#F44336"   # Red
                            }

                            # Create figure
                            fig = go.Figure()

                            # Track cumulative width for stacking bars
                            for sentiment, color in sentiment_colors.items():
                                # Calculate center position of text
                                keyword_sentiment[f'center_{sentiment}'] = (
                                    keyword_sentiment[[s for s in sentiment_colors.keys() if s <= sentiment]].sum(axis=1) - 
                                    keyword_sentiment[sentiment] / 2
                                )

                                fig.add_trace(go.Bar(
                                    y=keyword_sentiment['keyword'], 
                                    x=keyword_sentiment[sentiment], 
                                    name=sentiment.replace('_rate', ''), 
                                    orientation='h', 
                                    marker=dict(color=color),
                                    text=keyword_sentiment[sentiment].apply(lambda x: f"{x:.2f}" if x > 0 else ""),
                                    textposition='inside',
                                    insidetextanchor='middle',
                                    textfont=dict(color="black", size=10)  # Reduce font size
                                ))

                            # Adjust total review text placement
                            fig.add_trace(go.Scatter(
                                y=keyword_sentiment['keyword'], 
                                x=keyword_sentiment[['positive_rate', 'neutral_rate', 'negative_rate']].sum(axis=1) + 0.05,  # Move further right
                                text=keyword_sentiment['review_count'].apply(lambda x: f"S:{x}"),
                                mode='text',
                                textposition='middle right',  
                                showlegend=False,
                                textfont=dict(color="black", size=10)  # Reduce size for visibility
                            ))

                            # Layout adjustments
                            fig.update_layout(
                                title="Sentiment Analysis by Keyword",
                                barmode='stack',
                                xaxis=dict(showticklabels=False),  # Hide x-axis labels
                                yaxis=dict(title=""),  # Hide y-axis title
                                showlegend=False,  # Hide legend
                                plot_bgcolor='white',
                                margin=dict(l=0, r=85, t=25, b=0),  # Increase left margin to fit labels
                                height=200
                            )

                            # Display in Streamlit
                            st.plotly_chart(fig, use_container_width=True)


                        else:
                            st.warning("No matches found for the given keywords")
                    else:
                        st.warning("Please provide keyword to activate this feature")

            else:
                st.error('Please select an app to activate this chart')

        st.markdown("---")
    
    with analysis_header_container:
        st.markdown("<h3 style='text-align: center;'>App - Custom Analysis</h3>", unsafe_allow_html=True)

        st.write(""" Features
                
                - Single APP Analysis
                - Compare APP Feature
                """)

        st.markdown("---")
    
    with filter2_chart4_chart5_container:
        ######## MAIN ########
        filter2_chart4_column, chart5_column = st.columns([5,5],gap='medium')
        with filter2_chart4_column:
            col1, col2 = st.columns(2)
            with col1:

                sql_comparison = """
                    SELECT d.edtech_name
                    FROM dim_ranking_app AS d
                    JOIN fact_ranking_app AS f ON d.edtech_url = f.edtech_url
                    WHERE d.app_type = 'Android' AND f.`download_-_11/24` > 0 AND f.`download_-_12/24` > 0 AND f.`download_-_01/25` > 0 AND f.`download_-_02/25` > 0
                    """

                app = execute_sql_to_dataframe(sql_comparison)
                app_name = st.multiselect("Select app", app['edtech_name'],key='compare')

            with col2:
                pass

            if len(app_name) == 2:

                # keyword_conditions = " AND ".join([f"d.edtech_name = '{single_app}'" for single_app in app_name])

                app_name_tuple = tuple(app_name)  # Convert list to tuple
                sql_comparison2 = f"""
                    WITH sentiment_agg AS (
                        SELECT app_id, dominant_sentiment, count_sentiment
                        FROM (
                            SELECT 
                                app_id, 
                                dominant_sentiment, 
                                COUNT(*) AS count_sentiment,
                                RANK() OVER (PARTITION BY app_id ORDER BY COUNT(*) DESC) AS rnk
                            FROM fact_ranking_app_review
                            GROUP BY app_id, dominant_sentiment
                        ) ranked
                        WHERE rnk = 1  -- Select only the most frequent sentiment per app
                    )
                    SELECT 
                        d.edtech_name, d.edtech_url, d.app_type, d.segment, d.category,
                        f.star_rate_number AS fact_star_rate_number,
                        f.star_number AS fact_star_number,
                        sa.dominant_sentiment, sa.count_sentiment
                    FROM fact_ranking_app AS f
                    JOIN dim_ranking_app AS d 
                    USING(edtech_url)
                    LEFT JOIN sentiment_agg AS sa 
                    ON d.edtech_id = sa.app_id
                    WHERE d.edtech_name IN {app_name_tuple}
                """

                app2 = execute_sql_to_dataframe(sql_comparison2)
                # Select only numeric columns
                numeric_cols = app2.select_dtypes(include=['int64', 'float64']).columns

                # Apply highlight only for the max value in each numeric column
                def highlight_max(s):
                    is_max = s == s.max()
                    return ['background-color: yellow' if v else '' for v in is_max]

                styled_df = app2.style.apply(highlight_max, subset=numeric_cols)

                st.dataframe(styled_df)
            
            else:
                st.info("Please select 2 apps to compare.")

        with chart5_column:

            if len(app_name) == 2:

                app_name_tuple = tuple(app_name)  # Convert list to tuple

                sql_comparison3 = f"""
                    SELECT 
                        d.edtech_name, d.app_type, d.segment, d.category,
                        f.`download_-_11/24`, f.`download_-_12/24`, f.`download_-_01/25`, f.`download_-_02/25`
                    FROM fact_ranking_app AS f
                    JOIN dim_ranking_app AS d 
                    USING(edtech_url)
                    WHERE d.app_type = 'Android' AND d.edtech_name IN {app_name_tuple}
                """
                app3 = execute_sql_to_dataframe(sql_comparison3)

                import plotly.graph_objects as go
                import random
                from datetime import datetime, timedelta

                # Extract app names
                app_names = app3["edtech_name"].tolist()

                # Extract download columns dynamically
                download_columns = [col for col in app3.columns if col.startswith("download")]

                # Convert DataFrame to dictionary format for plotting
                data = {app_names[i]: app3.iloc[i][download_columns].tolist() for i in range(len(app3))}

                import re
                def extract_datetime(column_name):
                    match = re.search(r'(\d{1,2})/(\d{2})', column_name)
                    if match:
                        month, year = map(int, match.groups())
                        year += 2000  # Convert '24' -> 2024
                        return datetime(year, month, 1)
                    return None

                # Generate x-axis values from column names
                x_values = [extract_datetime(col) for col in download_columns]

                # Plotting function
                def create_line_chart(scores, title, x_values, show_xaxis=True):
                    fig = go.Figure()

                    fig.add_trace(go.Scatter(
                        x=x_values,
                        y=scores,
                        mode='lines+markers',
                        name=title
                    ))

                    fig.update_layout(
                        title=title,
                        xaxis_title="Time" if show_xaxis else "",
                        yaxis_title="Download Count",
                        height=200,
                        width=600,
                        margin=dict(t=22, b=0),
                        xaxis=dict(
                            showticklabels=show_xaxis,
                            tickmode='array',
                            tickvals=x_values,
                            ticktext=[dt.strftime("%b %Y") for dt in x_values] if show_xaxis else []
                        )
                    )

                    return fig

                # Streamlit UI
                st.markdown("<h6 style='text-align: center;'>Download Trend Over Time</h6>", unsafe_allow_html=True)

                # Loop through apps and plot
                for i, app_name in enumerate(data.keys()):
                    scores = data[app_name]  # Already a list of values
                    show_xaxis = (i == len(data) - 1)  # Show x-axis only for last chart
                    fig = create_line_chart(scores, f"App: {app_name}", x_values, show_xaxis)
                    st.plotly_chart(fig, use_container_width=True)

            else:
                st.info("Please select 2 apps to compare.")

    footer()
