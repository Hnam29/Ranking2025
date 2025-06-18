import streamlit as st
import pandas as pd
from streamlit_extras.metric_cards import style_metric_cards
import altair as alt
from webpages.footer import footer
import sys
from get_data_from_db import execute_sql_to_dataframe

def main_ranking():
    with open('/Users/vuhainam/Documents/PROJECT_DA/EdtechAgency/RANKING/2025/webpages/ranking.css')as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

    # st.markdown("""
    #         <style>
    #             .block-container {
    #                     padding-top: 1rem;
    #                     padding-bottom: 1rem;
    #                 }
    #         </style>
    #         """, unsafe_allow_html=True) 

    # SECTIONS
    info_container = st.container()
    scorecard_filter_container = st.container()
    chart_container = st.container()
    table_container = st.container()

    # Check if the imported function is available (it might be None if engine failed)
    if execute_sql_to_dataframe is None:
        st.error("The database query function could not be imported (engine might have failed).")
        sys.exit() # Exit if we can't query
    

    import base64
    def get_img_as_base64(file):
        with open(file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    
    img = get_img_as_base64('/Users/vuhainam/Documents/PROJECT_DA/EdtechAgency/Ranking/2025/webpages/bg.jpeg')
    page_bg_img = f"""
    <style>
        div[data-testid="stVerticalBlockBorderWrapper"]:nth-of-type(4) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1){{
            background-image: url("data:image/png;base64,{img}"); 
            border-radius: 5px;
            padding: 10px;
            }}
    </style>
    """
    st.markdown(page_bg_img,unsafe_allow_html=True)

    with info_container:

        # st.markdown("<h2 style='text-align: center;'>Ranking Dashboard</h2>", unsafe_allow_html=True)
        st.markdown("""
            <style>
            .bounce-title {
            font-size: 2.5em;
            font-weight: bold;
            color: #4CAF50;
            text-align: center;
            animation: float 3s ease-in-out infinite;
            }
            @keyframes float {
            0%, 100% { transform: translateY(0) }
            50% { transform: translateY(-10px) }
            }
            </style>

            <div class="bounce-title">Ranking Dashboard</div>
            """, unsafe_allow_html=True)
        
        text_column, figure_column = st.columns([7,3],gap='small')

        with text_column:
            st.subheader("""
                    About Ranking,
                    - What: A comprehensive ranking and evaluation system for educational technology platforms operating in the Vietnamese market
                    - Why: To foster quality, innovation, and trust in Vietnam's growing digital education ecosystem
                    - How: To benchmark products based on a robust, multi-dimensional framework
                    """)
        
        with figure_column:
             st.graphviz_chart('''
                digraph {
                    graph[width=500, height=300];
                    ranking -> web
                    ranking -> app
                    ranking -> feedback
                    web -> has_21_criteria
                    app -> has_4_criteria
                    has_21_criteria -> PCA_framework
                    has_4_criteria -> PCA_framework
                    app -> ios
                    app -> android
                    ios -> Sentiment_model 
                    android -> Sentiment_model 
                }
            ''',use_container_width=True)
        
        # st.markdown("""
        # <style>
        #     .block-container {
        #             margin-bottom: 50px;
        #         }
        # </style>
        # """, unsafe_allow_html=True) 
        st.markdown("---")

    with scorecard_filter_container:

        ######## FUNCTIONS ########

        # def style_metric_cards(
        #     color:str = "#232323",
        #     background_color: str = "#FFF",
        #     border_size_px: int = 1,
        #     border_color: str = "#CCC",
        #     border_radius_px: int = 5,
        #     border_left_color: str = "#9AD8E1",
        #     box_shadow: bool = True,
        # ):

        #     box_shadow_str = (
        #         "box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15) !important;"
        #         if box_shadow
        #         else "box-shadow: none !important;"
        #     )
            # st.markdown(
            #     f"""
            #     <style>
            #         div[data-testid="metric-container"] {{
            #             background-color: {background_color};
            #             border: {border_size_px}px solid {border_color};
            #             padding: 5% 5% 5% 10%;
            #             border-radius: {border_radius_px}px;
            #             border-left: 0.5rem solid {border_left_color} !important;
            #             color: {color};
            #             {box_shadow_str}
            #         }}
            #         div[data-testid="metric-container"] p {{
            #         color: {color};
            #         }}
            #     </style>
            #     """,
            #     unsafe_allow_html=True,
            # )

        ######## MAIN ########
        filter_column, scorecard_column = st.columns([3,7],gap='medium')
        with filter_column:

            sql_query = f"""
                SELECT DISTINCT segment as Segment FROM dim_ranking_web WHERE segment != ''
                """
            data = execute_sql_to_dataframe(sql_query)

            sql_query2 = f"""
                SELECT DISTINCT category as Category FROM dim_ranking_web WHERE category != ''
                """
            data2 = execute_sql_to_dataframe(sql_query2)

            edtechtype_filter = st.selectbox("Select Edtech type", ['Web','App'])
            
            col1, col2 = st.columns(2)
            with col1:
                segment_filter = st.selectbox("Select a segment", data['Segment'].tolist())
            
            with col2:
                category_filter = st.selectbox("Select a category", data2['Category'].tolist())

        with scorecard_column:
            sql_query = f"""
                SELECT SUM(row_count) AS total_rows
                FROM (
                    SELECT COUNT(*) AS row_count FROM dim_ranking_web
                    UNION ALL
                    SELECT COUNT(*) AS row_count FROM dim_ranking_app
                ) AS combined_counts;
                """
            data = execute_sql_to_dataframe(sql_query)

            # sql_query2 = f"""
            #     SELECT AVG(`target-backlink`) AS backlink_avg
            #     FROM fact_ranking_web
            #     """
            sql_query2 = f"""
                SELECT AVG(`backlink`) AS backlink_avg
                FROM fact_ranking_web
                """
            data2 = execute_sql_to_dataframe(sql_query2)
            data_for_metric = int(data['total_rows'])
            data_for_metric2 = ...  # <--- FORMULA FOR METRIC 2
            data_for_metric3 = ...  # <--- FORMULA FOR METRIC 3

            col1, col2, col3 = st.columns(3)

            #profit_per_change = grp_year_profit.iloc[-1]
            # col2.metric(label="Profit", value= "$"+millify(total_profit, precision=2), delta=profit_per_change)

            col1.metric(label=f"Total {edtechtype_filter} Edtech Product", value=data_for_metric)
            col2.metric(label="Average Edtech Ranking Product", value='...')
            col3.metric(label="...", value='...')

            style_metric_cards(border_left_color="#DBF227")

        # st.markdown("---")
    
    with chart_container:        

        ######## MAIN ########
        barchart_column, donutchart_column = st.columns([6.5,3.5],gap='small')

        with barchart_column:
            # sql_query = f"""
            #     SELECT 
            #         dim_ranking_web.edtech_name AS edtech_name,
            #         fact_ranking_web.`target-unique_visitor` AS unique_visitor
            #     FROM fact_ranking_web
            #     INNER JOIN dim_ranking_web 
            #     ON fact_ranking_web.edtech_url = dim_ranking_web.edtech_url 
            #     WHERE dim_ranking_web.category = '{category_filter}'
            #     ORDER BY fact_ranking_web.`target-unique_visitor` DESC
            #     LIMIT 5
            #     """
            sql_query = f"""
                SELECT 
                    dim_ranking_web.`WEB NAME` AS edtech_name,
                    fact_ranking_web.`UNIQUE VISITOR` AS unique_visitor
                FROM fact_ranking_web
                INNER JOIN dim_ranking_web 
                ON fact_ranking_web.`WEB URL` = dim_ranking_web.`WEB URL`
                WHERE dim_ranking_web.category = '{category_filter}' AND dim_ranking_web.segment = '{segment_filter}'
                ORDER BY fact_ranking_web.`UNIQUE VISITOR` DESC
                LIMIT 5
                """
            df = execute_sql_to_dataframe(sql_query)
            
            import plotly.express as px
            if not df.empty:
                fig = px.bar(
                    df,
                    x='unique_visitor',
                    y='edtech_name',
                    orientation='h',
                    color='edtech_name',
                    labels={'unique_visitor': 'Unique Visitors', 'edtech_name': 'EdTech Name'},
                    title='Top 5 EdTech Platforms by Ranking score'
                )

                fig.update_layout(
                    showlegend=False,
                    margin=dict(l=0, r=0, t=50, b=0),  # Remove margins (left, right, top, bottom)
                    height=400  
                )

                st.plotly_chart(
                    fig, 
                    use_container_width=True,
                    config={'displayModeBar': False}  # Optional: hide the toolbar
                )
            else:
                st.warning("No data available for the selected category.")

        
        with donutchart_column:

            # sql_query = f"""
            #     SELECT dim_ranking_web.category AS category, 
            #         SUM(fact_ranking_web.`target-unique_visitor`) AS unique_visitor
            #     FROM fact_ranking_web
            #     INNER JOIN dim_ranking_web 
            #     ON fact_ranking_web.edtech_url = dim_ranking_web.edtech_url
            #     GROUP BY dim_ranking_web.category
            #     """
            # df = execute_sql_to_dataframe(sql_query)

            import plotly.express as px

            # Configuration for dimensions
            DIMENSION_CONFIG = {
                "Category": {
                    "column": "category",
                    "sql_field": "dim_ranking_web.category"
                },
                "Segment": {
                    "column": "segment", 
                    "sql_field": "dim_ranking_web.segment"
                }
            }

            options = ["Segment", "Category"]
            selection = st.segmented_control(
                " ", options, selection_mode="single",default='Segment'
            )

            # Only show info message when no selection is made
            if not selection:
                st.info('Please select the dimension to observe the value proportion')

            # Process selection if one is made
            if selection:
                config = DIMENSION_CONFIG[selection]
                
                sql_query = f"""
                    SELECT {config['sql_field']} AS {config['column']},
                        SUM(fact_ranking_web.`unique visitor`) AS unique_visitor
                    FROM fact_ranking_web
                    INNER JOIN dim_ranking_web 
                    ON fact_ranking_web.`web url` = dim_ranking_web.`web url`
                    WHERE {config['sql_field']} != '' 
                    AND {config['sql_field']} IS NOT NULL
                    GROUP BY {config['sql_field']}
                """
                
                df = execute_sql_to_dataframe(sql_query)
                
                # Create donut chart
                fig_px = px.pie(
                    values=df['unique_visitor'],
                    names=df[config['column']],
                    title=f'{selection} Distribution',
                    hole=0.4
                )
                
                fig_px.update_traces(
                    textposition='inside', 
                    textinfo='percent+label', 
                    pull=[0, 0, 0.1, 0, 0]
                )
                fig_px.update_layout(
                    margin=dict(l=0, r=0, t=50, b=0),
                    height=300  
                )
                
                st.plotly_chart(fig_px, use_container_width=True)

        st.markdown("---")

    with table_container:

        import base64
        from pathlib import Path

        def image_to_base64(path):
            if not isinstance(path, str) or not Path(path).exists():
                return None  # or return a default image base64 string
            with open(path, "rb") as img_file:
                b64_string = base64.b64encode(img_file.read()).decode("utf-8")
                suffix = Path(path).suffix.lower().replace('.', '')  # e.g., 'png'
                return f"data:image/{suffix};base64,{b64_string}"

        data_df = pd.read_excel('/Users/vuhainam/Documents/PROJECT_DA/EdtechAgency/Ranking/2025/web_logo_mapping_update.xlsx')

        # Convert local paths to base64 strings
        data_df['logo_base64'] = data_df['logo_path'].apply(image_to_base64)
        
        # st.markdown("<h3 style='text-align: center; margin-bottom: 20px; background-image: linear-gradient(to right, #4ced94, #4eabf2); color:#061c04;'>"
        #             "Ranking Table</h3>", unsafe_allow_html=True)
        
        st.markdown("""
            <style>
            .glow-text {
            font-size: 2.5em;
            font-weight: bold;
            background: linear-gradient(90deg, #ff4b1f, #1fddff, #ff4b1f);
            background-size: 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shine 5s linear infinite;
            }

            .title-container {
            text-align: center;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
            }

            .title-icon {
            font-size: 2.5em;
            }
            @keyframes shine {
            0% { background-position: 0% }
            100% { background-position: 100% }
            }
            </style>

            <div class="title-container">
            <span class="glow-text">Innovating Education with Ranking</span>
            <span class="title-icon">🇻🇳</span>
            </div>
            """, unsafe_allow_html=True)

        
        st.markdown("""
        <style>
            .block-container {
                    padding-bottom: 40px;
                }
        </style>
        """, unsafe_allow_html=True) 

        st.markdown("""
        <p style='text-align: center;'>
            The development of criteria for evaluating educational technology products plays a key role in shaping and enhancing the quality of modern education. These criteria help developers and service providers understand user needs and enable consumers, including teachers, students, and educational institutions, to choose the products that best align with their learning and teaching goals.
            In 2025, EdTech Agency will continue publishing the annual white paper on educational technology and the “Products of the Year” Table. The products will be evaluated based on a set of criteria developed explicitly for the two different platforms: web and app.
        </p>""", unsafe_allow_html=True)

        st.markdown("""
        <style>
            .block-container {
                    padding-bottom: 40px;
                }
        </style>
        """, unsafe_allow_html=True) 
        
        table_col1,table_col2,table_col3,table_col4 = st.columns(4)

        with table_col1:

            data_df_k12 = data_df[data_df['Segment'] == 'K12']
            # Use data_editor with ImageColumn
            st.data_editor(
                data_df_k12[['edtech_name', 'logo_base64']],
                column_config={
                    "logo_base64": st.column_config.ImageColumn("K12",width='medium')
                },
                hide_index=True,
                key='K12'
            )

        with table_col2:

            data_df_he = data_df[data_df['Segment'] == 'HE']
            # Use data_editor with ImageColumn
            st.data_editor(
                data_df_he[['edtech_name', 'logo_base64']],
                column_config={
                    "logo_base64": st.column_config.ImageColumn("HE",width='medium')
                },
                hide_index=True,
                key='HE'
            )

        with table_col3:

            data_df_kd = data_df[data_df['Segment'] == 'Mầm non']
            # Use data_editor with ImageColumn
            st.data_editor(
                data_df_kd[['edtech_name', 'logo_base64']],
                column_config={
                    "logo_base64": st.column_config.ImageColumn("Mầm non",width='medium')
                },
                hide_index=True,
                key='Kindy'
            )

        with table_col4:

            data_df_wk = data_df[data_df['Segment'] == 'Đi làm']
            # Use data_editor with ImageColumn
            st.data_editor(
                data_df_wk[['edtech_name', 'logo_base64']],
                column_config={
                    "logo_base64": st.column_config.ImageColumn("Đi làm",width='medium')
                },
                hide_index=True,
                key='Working'
            )

    # footer()