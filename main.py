import streamlit as st
import json
import matplotlib.pyplot as plt

# Load the JSON file
with open('from_Mexico') as file:
    data = json.load(file)

# Extract dates and prices for a specific city
selected_city = st.selectbox('Select a City', list(data.keys()))
city_data = data[selected_city]
dates = list(city_data.keys())
prices = list(city_data.values())

# Create a line chart
fig, ax = plt.subplots()
ax.plot(dates, prices)

# Customize the chart
ax.set_xlabel('Date')
ax.set_ylabel('Price')
ax.set_title(f'Price Trend for {selected_city}')

# Reverse the y-axis
ax.invert_yaxis()

# Display the chart using Streamlit
st.pyplot(fig)
