"""Helper functions for creating graphs in the Streamlit dashboard.
This module contains functions for creating graphs to be used in the Streamlit dashboard."""

import altair as alt
import streamlit as st
import pandas as pd


def group_data_by_revenue_by_truck(t3_data):
    """Group data by total revenue by truck."""
    revenue_by_truck = t3_data.groupby('truck_name')[
        'total'].sum().sort_values(ascending=False).reset_index()
    return revenue_by_truck


def create_revenue_by_truck_chart(t3_data) -> None:
    """Creates a bar chart of total revenue by truck."""
    # === Calculate total revenue by truck
    revenue_by_truck = group_data_by_revenue_by_truck(t3_data)

    revenue_by_truck_chart = alt.Chart(revenue_by_truck).mark_bar().encode(
        x=alt.X('total:Q', title='Total Revenue ($)'),
        y=alt.Y('truck_name:N', sort='-x', title='Truck Name'),
        tooltip=['truck_name:N', alt.Tooltip(
            'total:Q', format='$,', title='Revenue')],
        color=alt.Color('truck_name:N', legend=None)
    ).properties(
        title='Total Revenue',
        width=600,
        height=300
    ).configure_axisY(labelLimit=200)
    st.altair_chart(revenue_by_truck_chart)


def get_highest_performing_truck(t3_data) -> str:
    """Calculate the highest performing truck based on total revenue."""
    revenue_by_truck = group_data_by_revenue_by_truck(t3_data)
    top_truck = revenue_by_truck.iloc[0]['truck_name']

    return top_truck


def get_highest_performing_truck_revenue(t3_data) -> float:
    """Calculate the revenue of the highest performing truck."""
    revenue_by_truck = group_data_by_revenue_by_truck(t3_data)
    top_truck_revenue = revenue_by_truck.iloc[0]['total']

    return top_truck_revenue


def get_lowest_performing_truck(t3_data) -> str:
    """Calculate the lowest performing truck based on total revenue."""
    revenue_by_truck = group_data_by_revenue_by_truck(t3_data)
    lowest_truck = revenue_by_truck.iloc[-1]['truck_name']

    return lowest_truck


def BAN_header(t3_data) -> None:
    """Create a header for the BAN section of the dashboard."""
    st.header("📊 Metrics")

    # Top metrics row
    with st.container():
        col1, col2 = st.columns(2)
        col1.metric("💰 Total Revenue",
                    f"${t3_data['total'].sum():,.2f}", border=True)
        col2.metric("🔢 Total Transactions", f"{len(t3_data):,}", border=True)

    # Truck performance row
    with st.container(border=True):
        col3, col4, col5 = st.columns(3)
        with col3:
            st.markdown('<p style="color: green;">🏆 Top Truck</p>',
                        unsafe_allow_html=True)
            st.write(f"**{get_highest_performing_truck(t3_data)}**")
        with col4:
            st.markdown(
                '<p style="color: green;">🚚 Top Truck Revenue</p>', unsafe_allow_html=True)
            st.write(
                f"**${get_highest_performing_truck_revenue(t3_data):,.2f}**")
        with col5:
            st.markdown('<p style="color: red;">🦺 Lowest Truck</p>',
                        unsafe_allow_html=True)
            st.write(f"**{get_lowest_performing_truck(t3_data)}**")

# def filter_data_by_time(t3_data, time_filter):
#     """Filter data by time based on the selected time filter."""
#     if time_filter == "Day":
#         filtered_df = t3_data
#     elif time_filter == "Month":
#         filtered_df = t3_data.groupby(["month", "year"]).sum(
#             numeric_only=True).reset_index()
#     elif time_filter == "Year":
#         filtered_df = t3_data.groupby(['year', 'month']).sum(
#             numeric_only=True).reset_index()
#     return filtered_df


def create_payment_method_piechart(t3_data) -> None:
    """Creates a pie chart of payment method distribution."""
    payment_method_counts = t3_data['payment_method'].value_counts(
    ).reset_index()
    payment_method_counts.columns = ['payment_method', 'count']

    payment_method_chart = alt.Chart(payment_method_counts).mark_arc().encode(
        theta=alt.Theta(field="count", type="quantitative"),
        color=alt.Color(field="payment_method", type="nominal",
                        scale=alt.Scale(scheme='category10'), legend=None),
        tooltip=['payment_method:N', alt.Tooltip('count:Q', title='Count')]
    ).properties(
        title='Payment Methods',
        width=150,
        height=300
    )
    st.altair_chart(payment_method_chart, use_container_width=True)


def slider_filter_by_time(t3_data, time_filter):
    """Filter data by time based on the selected time filter."""
    if time_filter == "Day":
        brush = alt.selection_interval(encodings=['x'])


def create_sales_over_time_chart(t3_data) -> None:
    """Creates a line chart of sales over time."""

    sales_over_time = t3_data.groupby(['date', 'payment_method'])[
        'total'].sum(numeric_only=True).reset_index()

    # Two payment method lines
    lines = alt.Chart(sales_over_time).mark_line().encode(
        x=alt.X('date:T', title='Date'),
        y=alt.Y('total:Q', title='Total Sales ($)'),
        color=alt.Color('payment_method:N',
                        legend=alt.Legend(title="Payment Method"), scale=alt.Scale(scheme='category10')),
    )
    # Total line
    total_over_time = t3_data.groupby('date')['total'].sum(
        numeric_only=True).reset_index()
    total_line = alt.Chart(total_over_time).mark_line(color='white', strokeDash=[5, 5]).encode(
        x=alt.X('date:T'),
        y=alt.Y('total:Q'),
        color=alt.value('#FFD700')
    )
    # Layer them together
    sales_over_time_chart = (lines + total_line).properties(
        title='Sales Over Time',
        height=300
    )
    st.altair_chart(sales_over_time_chart, use_container_width=True)
    st.caption("🟡 Total Revenue  | Other lines = payment methods")


# def create_fsa_rating_chart(t3_data) -> None:
#     """Creates a bar chart of average revenue by FSA rating."""
#     st.subheader("FSA Rating Analysis")
#     st.caption(
#         "FSA Rating: 0 to 5 based on how well they meet hygiene and food safety requirements.")
#     fsa_revenue = t3_data.groupby('fsa_rating')['total'].mean(
#         numeric_only=True).reset_index()
#     chart = alt.Chart(fsa_revenue).mark_bar().encode(
#         x=alt.X('fsa_rating:O', title='FSA Rating'),
#         y=alt.Y('total:Q', title='Avg Revenue ($)'),
#         color=alt.Color('fsa_rating:O', scale=alt.Scale(
#             scheme='redyellowgreen'), legend=None),
#         tooltip=['fsa_rating:O', alt.Tooltip('total:Q', format='$,.2f')]
#     ).properties(title='Average Revenue by FSA Rating', width=400, height=300)
#     st.altair_chart(chart, use_container_width=True)


# def create_fsa_transaction_count_chart(t3_data) -> None:
#     """Creates a bar chart showing the total number of transactions per FSA rating."""
#     # Group by rating and count the number of rows/transactions
#     fsa_counts = t3_data.groupby(
#         'fsa_rating').size().reset_index(name='order_count')

#     chart = alt.Chart(fsa_counts).mark_bar().encode(
#         x=alt.X('fsa_rating:O', title='FSA Rating'),
#         y=alt.Y('order_count:Q', title='Number of Transactions'),
#         color=alt.Color(
#             'fsa_rating:O',
#             scale=alt.Scale(scheme='redyellowgreen'),
#             legend=None
#         ),
#         tooltip=[
#             alt.Tooltip('fsa_rating:O', title='Rating'),
#             alt.Tooltip('order_count:Q', title='Total Orders')
#         ]
#     ).properties(
#         title='Transaction Volume by FSA Rating',
#         height=300
#     )

#     st.altair_chart(chart, use_container_width=True)

def create_combined_fsa_chart(t3_data) -> None:
    """Creates a chart comparing Revenue and Count with independent Y-axes."""
    st.subheader("FSA Performance: Revenue & Volume")

    # 1. Aggregate data
    fsa_stats = t3_data.groupby('fsa_rating').agg(
        avg_revenue=('total', 'mean'),
        order_count=('total', 'count')
    ).reset_index()

    # 2. Create the Base Chart
    base = alt.Chart(fsa_stats).encode(
        x=alt.X('fsa_rating:O', title='FSA Rating')
    )

    # 3. Bar Chart for Order Count (Left Axis)
    # Using alt.condition (lowercase) to fix your error
    bars = base.mark_bar().encode(
        y=alt.Y('order_count:Q', title='Number of Transactions'),
        color=alt.Color('fsa_rating:Q',
                        scale=alt.Scale(
                            scheme='redyellowgreen', domain=[0, 5]),
                        legend=None),
        tooltip=[alt.Tooltip('fsa_rating:O'), alt.Tooltip(
            'order_count:Q', title='Orders')]
    )

    # 4. Line Chart for Avg Revenue (Right Axis)
    # This ensures $15 revenue isn't dwarfed by 500 orders
    line = base.mark_line(color='gold', strokeWidth=3, point=alt.OverlayMarkDef(color='white')).encode(
        y=alt.Y('avg_revenue:Q', title='Avg Revenue ($)',
                scale=alt.Scale(zero=False)),
        tooltip=[alt.Tooltip('fsa_rating:O'), alt.Tooltip(
            'avg_revenue:Q', format='$,.2f')]
    )

    # 5. Layer them and resolve the Y-axis to be independent
    combined_chart = alt.layer(bars, line).resolve_scale(
        y='independent'
    ).properties(
        title='Volume (Bars) vs. Avg Revenue (Line) by Rating',
        height=350
    )

    st.altair_chart(combined_chart, use_container_width=True)
    st.caption("📊 Bars = Transaction Count | 📈 Line = Average Revenue")


def create_hourly_revenue_chart(t3_data) -> None:
    """Creates a line chart showing revenue trends by hour of the day."""
    # Ensure date is datetime and extract hour
    t3_data['hour'] = pd.to_datetime(t3_data['at']).dt.hour

    hourly_data = t3_data.groupby('hour')['total'].sum().reset_index()

    chart = alt.Chart(hourly_data).mark_area(
        line={'color': 'darkgreen'},
        color=alt.Gradient(
            gradient='linear',
            stops=[alt.GradientStop(color='white', offset=0),
                   alt.GradientStop(color='green', offset=1)],
            x1=1, x2=1, y1=1, y2=0
        )
    ).encode(
        x=alt.X('hour:O', title='Hour of Day (24h)'),
        y=alt.Y('total:Q', title='Total Revenue ($)'),
        tooltip=['hour', alt.Tooltip('total:Q', format='$,.2f')]
    ).properties(title='Peak Revenue Hours')

    st.altair_chart(chart, use_container_width=True)


def create_atv_by_truck_chart(t3_data) -> None:
    """Creates a horizontal bar chart of Average Transaction Value per truck."""
    atv_data = t3_data.groupby('truck_name')['total'].mean().reset_index()

    chart = alt.Chart(atv_data).mark_bar().encode(
        x=alt.X('total:Q', title='Avg Transaction Value ($)'),
        y=alt.Y('truck_name:N', sort='-x', title='Truck Name'),
        color=alt.Color('total:Q', scale=alt.Scale(scheme='greens')),
        tooltip=[alt.Tooltip('total:Q', format='$,.2f')]
    ).properties(title='Average Spend per Customer', height=300)

    st.altair_chart(chart, use_container_width=True)
