import streamlit as st
import pandas as pd
from streamlit_extras.metric_cards import style_metric_cards
import altair as alt
from webpages.footer import footer
import sys
from get_data_from_db import execute_sql_to_dataframe

def main_ranking():

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

    with info_container:

        st.markdown("<h2 style='text-align: center;'>Ranking Dashboard</h2>", unsafe_allow_html=True)
        text_column, figure_column = st.columns([7,3],gap='small')

        with text_column:
            st.subheader("""
                    About Ranking - Edtech Agency,
                    - What
                    - Why
                    - How
                         
                        The development of criteria for evaluating educational technology products plays a key role in shaping and enhancing the quality of modern education. These criteria help developers and service providers understand user needs and enable consumers, including teachers, students, and educational institutions, to choose the products that best align with their learning and teaching goals.
                    In 2024, EdTech Agency will continue its activities by publishing the annual white paper on educational technology and the “Products of the Year” Table. Educational technology products in 2024 will include international and domestic products available on both app and web platforms. The products will be evaluated based on a set of criteria developed explicitly for the two different platforms: web and app.
                    """)
        
        with figure_column:
             st.graphviz_chart('''
                digraph {
                    graph[width=500, height=300];
                    ranking -> web
                    ranking -> app
                    ranking -> feedback
                    web -> contain_27_criteria
                    app -> contain_11_criteria
                    contain_27_criteria -> ABC_framework
                    contain_11_criteria -> XYZ_framework
                    app -> ios
                    app -> android
                    ios -> Sentiment_model
                    android -> Sentiment_model
                }
            ''',use_container_width=True)
             
        # st.markdown("""
        # <style>
        #     .block-container {
        #             padding-bottom: 40px;
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
        scorecard_column, filter_column = st.columns([6.5,3.5],gap='small')
        with filter_column:

            sql_query = f"""
                SELECT DISTINCT segment as Segment FROM dim_ranking_web
                """
            data = execute_sql_to_dataframe(sql_query)

            sql_query2 = f"""
                SELECT DISTINCT category as Category FROM dim_ranking_web
                """
            data2 = execute_sql_to_dataframe(sql_query2)
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

            sql_query2 = f"""
                SELECT AVG(`target-backlink`) AS backlink_avg
                FROM fact_ranking_web
                """
            data2 = execute_sql_to_dataframe(sql_query2)
            data_for_metric = int(data['total_rows'])
            data_for_metric2 = round(data2['backlink_avg'],0)

            col1, col2, col3 = st.columns(3)

            #profit_per_change = grp_year_profit.iloc[-1]
            # col2.metric(label="Profit", value= "$"+millify(total_profit, precision=2), delta=profit_per_change)

            col1.metric(label="Total Edtech Ranking Product", value=data_for_metric)
            col2.metric(label="Average Edtech Ranking Product", value=data_for_metric2)

            style_metric_cards(border_left_color="#DBF227")
        
        st.markdown("---")

    
    with chart_container:
        ######## FUNCTION ########
        

        ######## MAIN ########
        barchart_column, donutchart_column = st.columns([6.5,3.5],gap='small')

        with barchart_column:
            sql_query = f"""
                SELECT 
                    dim_ranking_web.edtech_name AS edtech_name,
                    fact_ranking_web.`target-unique_visitor` AS unique_visitor
                FROM fact_ranking_web
                INNER JOIN dim_ranking_web 
                ON fact_ranking_web.edtech_url = dim_ranking_web.edtech_url 
                WHERE dim_ranking_web.category = '{category_filter}'
                ORDER BY fact_ranking_web.`target-unique_visitor` DESC
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
                    title='Top 5 EdTech Platforms by Unique Visitors'
                )
                fig.update_layout(showlegend=False)  # optional: hide legend if you like
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No data available for the selected category.")

            sql_query2 = f"""
                SELECT dim_ranking_web.category, 
                    fact_ranking_web.`target-referring_domain` AS referring_domain, 
                    fact_ranking_web.`target-unique_visitor` AS unique_visitor
                FROM fact_ranking_web
                INNER JOIN dim_ranking_web 
                ON fact_ranking_web.edtech_url = dim_ranking_web.edtech_url
                """
            dATA = execute_sql_to_dataframe(sql_query2)

            top_product_sales = dATA.groupby('category')['referring_domain'].sum()
            top_product_sales = top_product_sales.nlargest(10)
            top_product_sales = pd.DataFrame(top_product_sales).reset_index()
            
            top_product_profit = dATA.groupby('category')['unique_visitor'].sum()
            top_product_profit = top_product_profit.nlargest(10)
            top_product_profit = pd.DataFrame(top_product_profit).reset_index()
        
            chart = alt.Chart(top_product_sales).mark_bar(opacity=0.9,color="#9FC131").encode(
                    x='sum(referring_domain):Q',
                    y=alt.Y('category:N', sort='-x')   
                )
            chart = chart.properties(title="Top 10 Products" )

            st.altair_chart(chart,use_container_width=True)
        
        with donutchart_column:

            sql_query = f"""
                SELECT dim_ranking_web.category AS category, 
                    SUM(fact_ranking_web.`target-unique_visitor`) AS unique_visitor
                FROM fact_ranking_web
                INNER JOIN dim_ranking_web 
                ON fact_ranking_web.edtech_url = dim_ranking_web.edtech_url
                GROUP BY dim_ranking_web.category
                """
            df = execute_sql_to_dataframe(sql_query)
            
            import plotly.express as px

            fig_px = px.pie(values=df['unique_visitor'],
                            names=df['category'],
                            title='Donut Chart (Plotly Express)',
                            hole=0.4)
            fig_px.update_traces(textposition='inside', textinfo='percent+label', pull=[0, 0, 0.1, 0, 0])

            st.plotly_chart(fig_px, use_container_width=True)

        st.markdown("---")

    with table_container:

        table_col1,table_col2,table_col3,table_col4 = st.columns(4)

        with table_col1:
            # Combine the data into ONE dictionary
            data_dict = {
                "apps": [
                    "https://storage.googleapis.com/s4a-prod-share-preview/default/st_app_screenshot_image/5435b8cb-6c6c-490b-9608-799b543655d3/Home_Page.png",
                    "https://storage.googleapis.com/s4a-prod-share-preview/default/st_app_screenshot_image/ef9a7627-13f2-47e5-8f65-3f69bb38a5c2/Home_Page.png",
                    "https://storage.googleapis.com/s4a-prod-share-preview/default/st_app_screenshot_image/31b99099-8eae-4ff8-aa89-042895ed3843/Home_Page.png",
                    "https://storage.googleapis.com/s4a-prod-share-preview/default/st_app_screenshot_image/6a399b09-241e-4ae7-a31f-7640dc1d181e/Home_Page.png",
                ],
                "price": [20, 950, 250, 500],
            }

            # Pass the single dictionary to the DataFrame constructor
            data_df = pd.DataFrame(data_dict)

            st.data_editor(
                data_df,
                column_config={
                    "apps": st.column_config.ImageColumn(
                        "Category 1", help="Streamlit app preview screenshots"
                    ),
                    "price": st.column_config.NumberColumn(
                        "Price (in USD)",
                        help="The price of the product in USD",
                        min_value=0,
                        max_value=1000,
                        step=1,
                        format="$%d",
                    )
                },
                hide_index=True,
                key='category1',
            )

            st.data_editor(
                data_df,
                column_config={
                    "apps": st.column_config.ImageColumn(
                        "Preview Image", help="Streamlit2 app preview screenshots"
                    )
                },
                hide_index=True,
                key='category2',
            )

        with table_col2:
            data_df = pd.DataFrame(
                {
                    "apps": [
                        "https://storage.googleapis.com/s4a-prod-share-preview/default/st_app_screenshot_image/5435b8cb-6c6c-490b-9608-799b543655d3/Home_Page.png",
                        "https://storage.googleapis.com/s4a-prod-share-preview/default/st_app_screenshot_image/ef9a7627-13f2-47e5-8f65-3f69bb38a5c2/Home_Page.png",
                        "https://storage.googleapis.com/s4a-prod-share-preview/default/st_app_screenshot_image/31b99099-8eae-4ff8-aa89-042895ed3843/Home_Page.png",
                        "https://storage.googleapis.com/s4a-prod-share-preview/default/st_app_screenshot_image/6a399b09-241e-4ae7-a31f-7640dc1d181e/Home_Page.png",
                    ],
                }
            )

            st.data_editor(
                data_df,
                column_config={
                    "apps": st.column_config.ImageColumn(
                        "Preview Image", help="Streamlit app preview screenshots"
                    )
                },
                hide_index=True,
                key='category3',
            )

            st.data_editor(
                data_df,
                column_config={
                    "apps": st.column_config.ImageColumn(
                        "Preview Image", help="Streamlit2 app preview screenshots"
                    )
                },
                hide_index=True,
                key='category4',
            )

        with table_col3:
            data_df = pd.DataFrame(
                {
                    "apps": [
                        "https://storage.googleapis.com/s4a-prod-share-preview/default/st_app_screenshot_image/5435b8cb-6c6c-490b-9608-799b543655d3/Home_Page.png",
                        "https://storage.googleapis.com/s4a-prod-share-preview/default/st_app_screenshot_image/ef9a7627-13f2-47e5-8f65-3f69bb38a5c2/Home_Page.png",
                        "https://storage.googleapis.com/s4a-prod-share-preview/default/st_app_screenshot_image/31b99099-8eae-4ff8-aa89-042895ed3843/Home_Page.png",
                        "https://storage.googleapis.com/s4a-prod-share-preview/default/st_app_screenshot_image/6a399b09-241e-4ae7-a31f-7640dc1d181e/Home_Page.png",
                    ],
                }
            )

            st.data_editor(
                data_df,
                column_config={
                    "apps": st.column_config.ImageColumn(
                        "Preview Image", help="Streamlit app preview screenshots"
                    )
                },
                hide_index=True,
                key='category5',
            )

            st.data_editor(
                data_df,
                column_config={
                    "apps": st.column_config.ImageColumn(
                        "Preview Image", help="Streamlit2 app preview screenshots"
                    )
                },
                hide_index=True,
                key='category6',
            )

        with table_col4:
            data_df = pd.DataFrame(
                {
                    "apps": [
                        "https://storage.googleapis.com/s4a-prod-share-preview/default/st_app_screenshot_image/5435b8cb-6c6c-490b-9608-799b543655d3/Home_Page.png",
                        "https://storage.googleapis.com/s4a-prod-share-preview/default/st_app_screenshot_image/ef9a7627-13f2-47e5-8f65-3f69bb38a5c2/Home_Page.png",
                        "https://storage.googleapis.com/s4a-prod-share-preview/default/st_app_screenshot_image/31b99099-8eae-4ff8-aa89-042895ed3843/Home_Page.png",
                        "https://storage.googleapis.com/s4a-prod-share-preview/default/st_app_screenshot_image/6a399b09-241e-4ae7-a31f-7640dc1d181e/Home_Page.png",
                    ],
                }
            )

            st.data_editor(
                data_df,
                column_config={
                    "apps": st.column_config.ImageColumn(
                        "Preview Image", help="Streamlit app preview screenshots"
                    )
                },
                hide_index=True,
                key='category7',
            )

            st.data_editor(
                data_df,
                column_config={
                    "apps": st.column_config.ImageColumn(
                        "Preview Image", help="Streamlit2 app preview screenshots"
                    )
                },
                hide_index=True,
                key='category8',
            )


    footer()