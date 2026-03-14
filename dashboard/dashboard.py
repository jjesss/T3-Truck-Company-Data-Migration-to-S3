"""Streamlit dashboard for visualizing food truck sales data."""
import pandas as pd
import streamlit as st
from queries import load_data_auto_cache
from graphs import (create_revenue_by_truck_chart, BAN_header,
                    create_payment_method_piechart, create_sales_over_time_chart,
                    create_hourly_revenue_chart,
                    create_atv_by_truck_chart, create_combined_fsa_chart)


def main():
    # Load data from Athena with caching
    t3_data = load_data_auto_cache()
    st.set_page_config(layout="wide")
    # Convert 'at' column to datetime and extract date for easier grouping
    t3_data['date'] = t3_data['at'].dt.date.astype(str)

    # Title
    st.title("Food truck sales data")
    st.divider()

    # # Sidebar for filters
    # with st.sidebar:
    #     time_filter = st.selectbox("View by", ["Day", "Month", "Year"])

    # Display highest performing truck BAN
    BAN_header(t3_data)

    # Charts below
    st.divider()
    with st.container():
        st.subheader("Truck Performance")
        box1, box2 = st.columns(2)
        with box1:
            create_revenue_by_truck_chart(t3_data)
        with box2:
            create_atv_by_truck_chart(t3_data)
    st.divider()
    with st.container():
        box1, box2 = st.columns([3, 1])
        with box1:
            create_sales_over_time_chart(t3_data)
        with box2:
            create_payment_method_piechart(t3_data)

        create_hourly_revenue_chart(t3_data)
    st.divider()
    # create_fsa_rating_chart(t3_data)
    # create_fsa_transaction_count_chart(t3_data)
    create_combined_fsa_chart(t3_data)


main()

# # === Number of transactions by payment method (count)
# transactions_count_by_payment = df['payment_method'].value_counts()
# total_transactions = len(df)
# for payment_method, count in transactions_count_by_payment.items():
#     percentage = (count / total_transactions) * 100
#     print(f"{payment_method}: {count} transactions ({percentage:.2f}%)")

# # Statistical analysis of transaction amounts by payment method

# for payment_method in df['payment_method'].unique():
#     method_data = df[df['payment_method'] == payment_method]['total']

# # === Calculate total revenue across all trucks
# total_revenue = df['total'].sum()


# revenue_by_truck_chart = alt.Chart(revenue_by_truck).mark_bar().encode(
#     x=alt.X('total:Q', title='Total Revenue ($)'),
#     y=alt.Y('truck_name:N', sort='-x', title='Truck Name'),
#     tooltip=['truck_name:N', alt.Tooltip(
#         'total:Q', format='$,', title='Revenue')], color=alt.Color('truck_name:N', legend=None)
# ).properties(
#     title='Total Revenue by Truck',
#     width=600,
#     height=300
# )
# st.altair_chart(revenue_by_truck_chart, use_container_width=True)

# st.metric(label="Top Performing Truck", value=top_truck,
#           delta=f"${top_truck_revenue:,.2f}")


# def load_data_manual_cache():
#     if "loaded_data" not in st.session_state:
#         df = wr.athena.read_sql_query(
#             "SELECT * FROM countries_input;",
#             database="c22-lz-happiness-crawler"
#         )
#         st.session_state['loaded_data'] = df
#     else:
#         df = st.session_state['loaded_data']

#     return df


# @st.cache_data(ttl=300, show_spinner=True)
# def load_data_automatic_cache():
#     return wr.athena.read_sql_query(
#         "SELECT * FROM countries_input;",
#         database="c22-lz-happiness-crawler")


# df = load_data_automatic_cache()


# print(st.session_state)

# st.title("Choose year to analyse")
# year_to_analyse = st.selectbox("Select a year", df["year"].unique())

# st.title("Bar chart of the years of happiness")
# df = df[df['year'] == year_to_analyse]
# behaviour_counts_by_rabbit = df.groupby(["year"]).size(
# ).unstack().fillna(0).sort_values(by="good", ascending=False)

# print(behaviour_counts_by_rabbit)
# st.bar_chart(behaviour_counts_by_rabbit, x_label="Year",
#              y_label="Count", use_container_width=True)
