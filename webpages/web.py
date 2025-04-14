import streamlit as st
import pandas as pd
from streamlit_extras.dataframe_explorer import dataframe_explorer
from streamlit_extras.metric_cards import style_metric_cards
from webpages.footer import footer
import sys
from get_data_from_db import execute_sql_to_dataframe

def main_web():
   with open('/Users/vuhainam/Documents/PROJECT_DA/EdtechAgency/RANKING/2025/webpages/web.css')as f:
      st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

   sql_query = f"""
      SELECT DISTINCT segment as Segment FROM dim_ranking_web
      """
   segment = execute_sql_to_dataframe(sql_query)

   sql_query2 = f"""
      SELECT DISTINCT category as Category FROM dim_ranking_web
      """
   category = execute_sql_to_dataframe(sql_query2)

   ddl_sql = """   
   CREATE OR REPLACE VIEW view_transformed_grouped_criteria AS
      SELECT 
      edtech_url,
      (0.3 * LOG10(IFNULL(NULLIF(`target-backlink`, 0), 1))) + 
      (0.34 * LOG10(IFNULL(NULLIF(`target-referring_domain`, 0), 1))) +  
      (0.34 * LOG10(IFNULL(NULLIF(`target-backlink_quality`, 0), 1))) AS backlink,

      (0.5 * LOG10(IFNULL(NULLIF((0.7 * `target-brand_keyword` + 0.3 * `target-non-brand_keyword`), 0), 1))) + 
      (0.5 * LOG10(IFNULL(NULLIF(`target-keyword_difficulty`, 0), 1))) AS keyword,

      (0.35 * LOG10(IFNULL(NULLIF(`target-website_speed_(%)`, 0), 1))) + 
      (0.32 * LOG10(IFNULL(NULLIF(`target-website_authority`, 0), 1))) +  
      (0.33 * LOG10(IFNULL(NULLIF(`target-website_security/privacy`, 0), 1))) AS website_performance_internal,

      (0.6 * LOG10(IFNULL(NULLIF(`target-accessibility_compliance`, 0), 1))) + 
      (0.4 * LOG10(IFNULL(NULLIF(`target-navigation_&_readability`, 0), 1))) AS website_performance_external

      FROM fact_ranking_web;
   """
   execute_sql_to_dataframe(ddl_sql)

   dml_sql = "SELECT * FROM view_transformed_grouped_criteria;"
   data = execute_sql_to_dataframe(dml_sql)

   # SECTIONS
   info_container = st.container()
   scorecard_filter1_container = st.container()
   chart1_container = st.container()
   analysis_header_container = st.container()
   scorecard_filter2_container = st.container()
   chart2_container = st.container()

   with info_container:

      st.markdown("<h2 style='text-align: center;'>Web Dashboard</h2>", unsafe_allow_html=True)
      content1_column, separate_line, content2_column = st.columns([4.95, 0.1, 4.95],gap='small')

      import base64
      def get_img_as_base64(file):
         with open(file, 'rb') as f:
            data = f.read()
         return base64.b64encode(data).decode()
      
      img = get_img_as_base64('/Users/vuhainam/Documents/PROJECT_DA/EdtechAgency/Ranking/2025/webpages/bg2.jpeg')
      page_bg_img = f"""
      <style>
         div[data-testid="stVerticalBlockBorderWrapper"]:nth-of-type(4) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) {{
               background-image: url("data:image/png;base64,{img}"); 
               border-radius: 5px;
            }}
      </style>
      """
      st.markdown(page_bg_img,unsafe_allow_html=True)

      with content1_column:
         st.subheader("""
                  About WEB,   
                  - Ranking Web consists of 381 websites across different industries and sectors
                     
                     - There are over 20 criteria that have been deeply research and implement to assess multiple aspects of a website
                        - Stakeholders: teacher, parent, investor, administrator, analyst 
                           - Objectives: 
                              - 1. Evaluate the overall quality of a single website
                              - 2. Identify the "best" website from a set of criteria 
                              - 3. Benchmark websites against each other or against ideal standards in the edtech domain
                              - 4. Create a scoring system that is transparent and justifiable
                  """)
      
      # with separate_line:
      #    st.markdown(
      #       """
      #       <div style="border-left: 1.5px solid; height: 320px; margin: 10px 0px 20px; background-image: linear-gradient(to right, #c23640, #96d9a4); "></div>
      #       """,
      #       unsafe_allow_html=True
      #    )

      with content2_column:
         st.subheader("""
                  About WEB,   
                  - Ranking Web consists of 381 websites across different industries and sectors
                     
                     - There are over 20 criteria that have been deeply research and implement to assess multiple aspects of a website
                        - Stakeholders: teacher, parent, investor, administrator, analyst 
                           - Objectives: 
                              - 1. Evaluate the overall quality of a single website
                              - 2. Identify the "best" website from a set of criteria 
                  """)
         
      # st.markdown("---")
      # st.markdown(
      #       """
      #       <div style="border-bottom: 2px solid; height: 4px; margin: 10px 0px 20px; background-image: linear-gradient(to right, #96d9a4, #c23640); "></div>
      #       """,
      #       unsafe_allow_html=True
      #    )

   with scorecard_filter1_container:
      ######## MAIN ########
      scorecard_column, separate_line1, complex_column, separate_line2, filter_column = st.columns([2.9, 0.1, 5, 0.1, 1.9],gap='small')
      with separate_line1:
         st.markdown(
            """
            <div style="border-left: 2px solid; height: 200px; margin: 10px 0px 20px; background-image: linear-gradient(to right, #96d9a4, #c23640); "></div>
            """,
            unsafe_allow_html=True
         )
      with separate_line2:
         st.markdown(
            """
            <div style="border-left: 2px solid; height: 200px; margin: 10px 0px 20px; background-image: linear-gradient(to right, #c23640, #96d9a4); "></div>
            """,
            unsafe_allow_html=True
         )
      with filter_column:
         
         selected_Segment = st.selectbox("Segment", segment['Segment'],index=None,key='segment_filter1')
         selected_Category = st.selectbox("Category", category['Category'],index=None,key='category_filter1')

         # Display messages based on user selection
         if selected_Segment and selected_Category:
            st.info(f'You are filtering by Segment: **{selected_Segment}** and Category: **{selected_Category}**')
         elif selected_Segment:
            st.info(f'You are filtering by Segment: **{selected_Segment}**')
         elif selected_Category:
            st.info(f'You are filtering by Category: **{selected_Category}**')

      with scorecard_column:
         sql1 = "SELECT COUNT(edtech_url) AS total_web FROM dim_ranking_web"
         metric1 = execute_sql_to_dataframe(sql1)
         st.metric(label="Total Web", value=metric1['total_web'])

         # sql2 = "SELECT COUNT(edtech_url) AS total_web FROM dim_ranking_web"
         # metric2 = execute_sql_to_dataframe(sql2)
         st.metric(label="Total Web with score >0.8", value='10')

      with complex_column:
         sql2 = """
            SELECT COLUMN_NAME AS criteria
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'fact_ranking_web'
            AND TABLE_SCHEMA = 'EdtechAgency_Ranking2025'
            AND COLUMN_NAME NOT IN ('edtech_url');
         """
         metric2= execute_sql_to_dataframe(sql2)
         selections = st.multiselect('Choose criteria', metric2['criteria'].tolist(), placeholder= 'Max 4 selections', max_selections=4)

         # SQL to fetch average values for selected columns
         if selections:
            # Dynamically build SELECT AVG query
            selected_cols = ", ".join([f"AVG(`{col}`) AS `{col}`" for col in selections])
            
            sql3 = f"""
               SELECT {selected_cols}
               FROM fact_ranking_web
               WHERE `{selections[0]}` IS NOT NULL
            """
            df_metrics = execute_sql_to_dataframe(sql3)

            # Fill metrics safely
            col1, col2, col3, col4 = st.columns(4)

            if len(selections) >= 1:
               val1 = round(df_metrics[selections[0]][0], 2)
               col1.metric(label=f"{selections[0]}", value=val1)
            if len(selections) >= 2:
               val2 = round(df_metrics[selections[1]][0], 2)
               col2.metric(label=f"{selections[1]}", value=val2)

            if len(selections) >= 3:
               val3 = round(df_metrics[selections[2]][0], 2)
               col3.metric(label=f"{selections[2]}", value=val3)

            if len(selections) == 4:
               val4 = round(df_metrics[selections[3]][0], 2)
               col4.metric(label=f"{selections[3]}", value=val4)

            style_metric_cards(border_left_color="#DBF227")
      
      st.markdown("---")
      st.markdown("""
         <style>
               .block-container {
                     padding-bottom: 0.5rem;
                  }
         </style>
         """, unsafe_allow_html=True) 
   
   with chart1_container:
   
      title_column, separate_line, stackedbarchart_column = st.columns([1.4, 0.1, 8.5],gap='medium')
      with title_column:
         # st.markdown("<h4 style='text-align: center;'>Component of ranking score</h4>", unsafe_allow_html=True)
         st.markdown(f"""
                     <h4 style='margin-left: 60px; writing-mode: vertical-rl; text-orientation: mixed; text-align:center; 
                           height: 280px; width: 50px; transform: rotate(270deg);'>
                     Proportion of criteria contribute to web ranking score
                     </h4>
                     """, unsafe_allow_html=True)
         # if selected_Segment is not None and selected_Category is not None:
         #    st.markdown(f"""(filtered by {selected_Segment} and {selected_Category})
         #                """, unsafe_allow_html=True)
         # elif selected_Segment is not None and selected_Category is None:
         #    st.markdown(f"""(filtered by {selected_Segment})
         #                """, unsafe_allow_html=True)
         # elif selected_Segment is None and selected_Category is not None:
         #    st.markdown(f"""(filtered by {selected_Category})
         #                """, unsafe_allow_html=True)
      with separate_line:
         st.markdown(
            """
            <div style="border-left: 2px solid; height: 300px; margin: 10px 0px 20px; background-image: linear-gradient(to right, #c23640, #96d9a4); "></div>
            """,
            unsafe_allow_html=True
         )

      with stackedbarchart_column:

         sql2 = """
            SELECT dim_ranking_web.edtech_name AS edtech_name, 
                  view_transformed_grouped_criteria.backlink AS backlink,
                  view_transformed_grouped_criteria.keyword AS keyword,
                  view_transformed_grouped_criteria.website_performance_external AS performance_external,
                  view_transformed_grouped_criteria.website_performance_internal AS performance_internal
            FROM fact_ranking_web
            INNER JOIN dim_ranking_web 
            ON fact_ranking_web.edtech_url = dim_ranking_web.edtech_url
            INNER JOIN view_transformed_grouped_criteria
            ON dim_ranking_web.edtech_url = view_transformed_grouped_criteria.edtech_url
            WHERE 1=1
         """

         # Add conditions dynamically
         conditions = []
         if selected_Segment:
            conditions.append(f"dim_ranking_web.segment = '{selected_Segment}'")
         if selected_Category:
            conditions.append(f"dim_ranking_web.category = '{selected_Category}'")

         # Append conditions if they exist
         if conditions:
            sql2 += " AND " + " AND ".join(conditions)

         # Add LIMIT
         sql2 += " LIMIT 7"

         # Execute query
         data = execute_sql_to_dataframe(sql2)

         import altair as alt

         # Chuẩn bị dữ liệu
         data_melted = data.melt(id_vars='edtech_name', var_name='variable', value_name='value')
         data_melted['order'] = data_melted['variable'].map({
            'backlink': 1, 
            'keyword': 2, 
            'performance_external': 3, 
            'performance_internal': 4  # Sửa duplicate value
         })

         # Tính tổng giá trị và sắp xếp
         totals = data_melted.groupby('edtech_name')['value'].sum().reset_index()
         totals = totals.sort_values('value', ascending=False)
         ordered_names = totals['edtech_name'].tolist()

         # Tính toán chiều rộng dựa trên số lượng thực thể
         num_entities = len(ordered_names)
         # bar_width = 50  # Chiều rộng cho mỗi cột
         # min_width = 600  # Chiều rộng tối thiểu
         # chart_width = max(min_width, num_entities * bar_width)

         # Tạo biểu đồ với chiều rộng cố định
         chart = alt.Chart(data_melted).mark_bar().encode(
            x=alt.X('edtech_name:N', 
                     sort=ordered_names, 
                     axis=alt.Axis(labelAngle=-45, labelLimit=150, title=None)),
            y=alt.Y('value:Q', title=None
                  #   title="Giá trị"
                    ),
            color=alt.Color('variable:N', 
                           legend=alt.Legend(title="Tiêu chí"),
                           scale=alt.Scale(
                              domain=['backlink', 'keyword', 'performance_external', 'performance_internal'],
                              range=['#5470c6', '#91cc75', '#fac858', '#ee6666']
                           )),
            order='order:Q',
            tooltip=['edtech_name', 'variable', 'value']
         ).properties(
            width=200,
            height=400,
            title="So sánh các tiêu chí theo ứng dụng"
         )
         st.altair_chart(chart, use_container_width=True)

      st.markdown("---")
  

   with analysis_header_container:
      st.markdown("<h3 style='text-align: center;'>Web - Custom Analysis</h3>", unsafe_allow_html=True)

      st.write(""" Features
               
               - Single Web Analysis
               - Compare Web Feature
               """)

      st.markdown("---")
   
   with scorecard_filter2_container:

      # Custom style to add height and vertical divider
      st.markdown("""
         <style>
               div[data-testid="stMetric"]:nth-of-type(2) {
                  height: 100px;
               }
               div[data-testid="stMetric"]:nth-of-type(1),
               div[data-testid="stMetric"]:nth-of-type(3) {
                  padding-top: 0px;
                  padding-bottom: 0px;
                  max-height: 110px;
                  overflow-y: auto;
               }
               div[data-testid="stHorizontalBlock"]:nth-of-type(1),
               div[data-testid="stHorizontalBlock"]:nth-of-type(3) {
                  margin-bottom: 0px;
               }
         </style>
      """, unsafe_allow_html=True)
    
      filter2_column, separate_line, scorecard2_column = st.columns([2, 0.1, 7.9],gap='small')

      with filter2_column:
         col1, col2 = st.columns([4,6])
         with col1:
            segment_filter = st.selectbox("Segment", segment['Segment'],index=None,key='segment_filter2')
            category_filter = st.selectbox("Category", category['Category'],index=None,key='category_filter2')

         with col2:
            # Base query
            sql = """
               SELECT DISTINCT edtech_name
               FROM dim_ranking_web
               WHERE 1=1
            """

            # Optional filters
            conditions = []
            if segment_filter:
               conditions.append(f"dim_ranking_web.segment = '{segment_filter}'")
            if category_filter:
               conditions.append(f"dim_ranking_web.category = '{category_filter}'")

            # Add conditions dynamically
            if conditions:
               sql += " AND " + " AND ".join(conditions)

            # Execute query
            data = execute_sql_to_dataframe(sql)

            # Streamlit UI for selection
            selected_web = st.multiselect("Select 2 web for comparison", data['edtech_name'], max_selections=2)

      with separate_line:
         st.markdown(
            """
            <div style="border-left: 1.5px solid; height: 120px; margin: 10px 0px 20px; background-image: linear-gradient(to right, #c23640, #96d9a4); "></div>
            """,
            unsafe_allow_html=True
         )

      with scorecard2_column:
         selected_web_str = ", ".join(f"'{city}'" for city in selected_web)

         # sql = f"""
         #    SELECT  dim_ranking_web.edtech_name AS edtech_name,
         #          fact_ranking_web.`target-website_speed_(%)` AS website_speed,
         #          fact_ranking_web.`target-website_authority` AS website_authority,
         #          fact_ranking_web.`target-website_security/privacy` AS website_security,
         #          fact_ranking_web.`target-accessibility_compliance` AS accessibility,
         #          fact_ranking_web.`target-navigation_&_readability` AS readability
         #    FROM fact_ranking_web 
         #    INNER JOIN dim_ranking_web
         #    ON fact_ranking_web.edtech_url = dim_ranking_web.edtech_url
         #    WHERE dim_ranking_web.edtech_name IN ({selected_web_str}) AND dim_ranking_web.category = {category_filter} AND dim_ranking_web.segment = {segment_filter}
         # """
         # data = execute_sql_to_dataframe(sql)

         # Base query
         sql = f"""
            SELECT  dim_ranking_web.edtech_name AS edtech_name,
                     fact_ranking_web.`target-website_speed_(%)` AS website_speed,
                     fact_ranking_web.`target-website_authority` AS website_authority,
                     fact_ranking_web.`target-website_security/privacy` AS website_security,
                     fact_ranking_web.`target-accessibility_compliance` AS accessibility,
                     fact_ranking_web.`target-navigation_&_readability` AS readability
            FROM fact_ranking_web 
            INNER JOIN dim_ranking_web
            ON fact_ranking_web.edtech_url = dim_ranking_web.edtech_url
            WHERE dim_ranking_web.edtech_name IN ({selected_web_str})
         """

         # Add optional filters
         conditions = []
         if category_filter:
            conditions.append(f"dim_ranking_web.category = '{category_filter}'")
         if segment_filter:
            conditions.append(f"dim_ranking_web.segment = '{segment_filter}'")

         # Append conditions if any exist
         if conditions:
            sql += " AND " + " AND ".join(conditions)

         # Execute the query
         data = execute_sql_to_dataframe(sql)

         sql_avg = """
            SELECT 
                  AVG(`target-website_speed_(%)`) AS avg_website_speed,
                  AVG(`target-website_authority`) AS avg_website_authority,
                  AVG(`target-website_security/privacy`) AS avg_website_security,
                  AVG(`target-accessibility_compliance`) AS avg_accessibility,
                  AVG(`target-navigation_&_readability`) AS avg_readability
            FROM fact_ranking_web 
         """
         data_avg = execute_sql_to_dataframe(sql_avg)

         # Extract average values
         avg = data_avg.iloc[0]

         # Make sure we have 2 selected websites
         if len(selected_web) == 2:
            # Prepare columns
            col1, col2, col3, col4, col5 = st.columns(5)

            for idx, row in data.iterrows():
               notes = []  # Track missing fields for this edtech_name

               # Website Speed
               if pd.notna(row['website_speed']):
                     col1.metric(
                        label=f"Speed: {row['edtech_name']}",
                        value=row['website_speed'],
                        delta=round(row['website_speed'] - avg['avg_website_speed'], 2)
                     )
               else:
                     notes.append("Speed")

               # Authority
               if pd.notna(row['website_authority']):
                     col2.metric(
                        label=f"Authority: {row['edtech_name']}",
                        value=row['website_authority'],
                        delta=round(row['website_authority'] - avg['avg_website_authority'], 2)
                     )
               else:
                     notes.append("Authority")

               # Security
               if pd.notna(row['website_security']):
                     col3.metric(
                        label=f"Security: {row['edtech_name']}",
                        value=row['website_security'],
                        delta=round(row['website_security'] - avg['avg_website_security'], 2)
                     )
               else:
                     notes.append("Security")

               # Accessibility
               if pd.notna(row['accessibility']):
                     col4.metric(
                        label=f"Accessibility: {row['edtech_name']}",
                        value=row['accessibility'],
                        delta=round(row['accessibility'] - avg['avg_accessibility'], 2)
                     )
               else:
                     notes.append("Accessibility")

               # Readability
               if pd.notna(row['readability']):
                     col5.metric(
                        label=f"Readability: {row['edtech_name']}",
                        value=row['readability'],
                        delta=round(row['readability'] - avg['avg_readability'], 2)
                     )
               else:
                     notes.append("Readability")

               # Optional: Show note for missing data
               if notes:
                     st.warning(f"{row['edtech_name']} is missing data for: {', '.join(notes)}")

            style_metric_cards(border_left_color="#DBF227")

         else:
            st.info("Please select 2 websites to compare.")
      
      st.markdown("---")
   
   with chart2_container:
      title2_column, horizontalchart1_column, horizontalchart2_column = st.columns([1,4.5,4.5],gap='small')

      if len(selected_web) == 2:

         with title2_column:
            st.markdown(
               f"""
               <h4 style="writing-mode: vertical-rl; text-orientation: mixed; text-align:center; 
                           height: 280px; width: 50px; transform: rotate(180deg);">
                  Comparison 

                  Differences among evaluated criteria of <b> {selected_web[0]} </b> and  <b> {selected_web[1]} </b>
               </h4>
               """, 
               unsafe_allow_html=True
            )

         selected_web_str = ", ".join(f"'{city}'" for city in selected_web)
         sql = f"""
            SELECT  dim_ranking_web.edtech_name,
                  fact_ranking_web.`target-backlink` AS backlink,
                  fact_ranking_web.`target-referring_domain` AS referring_domain,
                  fact_ranking_web.`target-backlink_quality` AS backlink_quality,
                  fact_ranking_web.`target-brand_keyword` AS brand_keyword,
                  fact_ranking_web.`target-non-brand_keyword` AS non_brand_keyword,
                  fact_ranking_web.`target-keyword_difficulty` AS keyword_difficulty,
                  fact_ranking_web.`target-website_speed_(%)` AS website_speed,
                  fact_ranking_web.`target-website_authority` AS website_authority,
                  fact_ranking_web.`target-website_security/privacy` AS website_security,
                  fact_ranking_web.`target-accessibility_compliance` AS accessibility,
                  fact_ranking_web.`target-navigation_&_readability` AS readability
            FROM fact_ranking_web 
            INNER JOIN dim_ranking_web
            ON fact_ranking_web.edtech_url = dim_ranking_web.edtech_url
            WHERE dim_ranking_web.edtech_name IN ({selected_web_str})
         """
         data = execute_sql_to_dataframe(sql)

         # Reshape for Altair (wide to long format)
         data_long = data.melt(id_vars='edtech_name', var_name='metric', value_name='value')

         # Separate by edtech
         edtechs = data['edtech_name'].unique()

         with horizontalchart1_column:
            chart1 = alt.Chart(data_long[data_long['edtech_name'] == edtechs[0]]).mark_bar().encode(
                  x='value:Q',
                  y=alt.Y('metric:N', sort='-x')
            ).properties(title=edtechs[0])
            st.altair_chart(chart1, use_container_width=True)

         with horizontalchart2_column:
            chart2 = alt.Chart(data_long[data_long['edtech_name'] == edtechs[1]]).mark_bar().encode(
                  x='value:Q',
                  y=alt.Y('metric:N', sort='-x')
            ).properties(title=edtechs[1])
            st.altair_chart(chart2, use_container_width=True)
        
      else:
         horizontalchart1_column.info("Please select 2 websites to compare.")
         horizontalchart2_column.info("Please select 2 websites to compare.")

   footer()