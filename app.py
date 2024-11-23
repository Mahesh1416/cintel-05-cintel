from shiny import reactive, render
from shiny.express import ui
import random
from datetime import datetime
from collections import deque
import plotly.express as px
from shinywidgets import render_plotly
from scipy import stats
from shinyswatch import theme
import pandas as pd
from faicons import icon_svg

# Generating fake time and temperature readings at N seconds

UPDATE_INTERVAL_SECS: int = 3

DEQUE_SIZE: int = 5
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))

@reactive.calc()
def reactive_calc_combined():

    # In order to trigger the updates we are invalidating this calculation every UPDATE_INTERVAL_SEC 
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)

    temp = round(random.uniform(-18, -16), 1)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_dictionary_entry = {"temp": temp, "timestamp": timestamp}

    # In order to get the deque and append the new entry
    reactive_value_wrapper.get().append(new_dictionary_entry)

    deque_snapshot = reactive_value_wrapper.get()

    # We are converting deque to DataFrame for display
    df = pd.DataFrame(deque_snapshot)

    latest_dictionary_entry = new_dictionary_entry

    return deque_snapshot, df, latest_dictionary_entry

    
# We are defining the Shiny UI Page layout

ui.page_opts(title="Use of Pyshiny: Live Data Example using Antarctica data", fillable=True)

with ui.sidebar(open="open"):
    
    ui.h2("Exploring Antarctica data", class_="text-center")
    
    ui.p(
        "Real-time temperature readings in Antarctica.",
        class_="text-center",
    )

    ui.h2()
    ui.h6("Links:")
    ui.a(
        "GitHub Source",
        href="https://github.com/Mahesh1416/cintel-05-cintel",
        target="_blank",
    )


with ui.layout_columns():
    with ui.value_box(
        showcase=icon_svg("sun"),
    ):

        "Current Temperature"
        
        @render.text
        def display_temp():
            """"In order to get the latest reading and return a temperature string"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['temp']} C"

        "warmer than usual"

    with ui.value_box(
        showcase=icon_svg("calendar"),
    ):

        "Current Date and Time"

        @render.text
        def display_time():
            """In order to get the latest reading and return a timestamp string"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['timestamp']}"

with ui.layout_columns():
    # with ui.card(full_screen=True, min_height="40%"):
    with ui.card(full_screen=True):
        ui.card_header("Recent Readings of temperature with timestamps")

        @render.data_frame
        def display_df():
            """Get the latest reading and return a dataframe with current readings"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            pd.set_option('display.width', None)    # Use maximum width
            return render.DataGrid(df,width="100%")

        
@render_plotly
def display_plot():
            # Fetch from the reactive calc function
            deque_snapshot, df, latest_dicitonary_entry = reactive_calc_combined()
    
            # Ensure the DataFrame is not empty before plotting
            if not df.empty:
                # Convert the 'timestamp' column to datetime for better plotting
                df["timestamp"] = pd.to_datetime(df["timestamp"])
    
                # Create scatter plot for readings
                # pass in the df, the name of the x column, the name of the y column,
                # and more
    
                fig = px.scatter(df,
                x="timestamp",
                y="temp",
                title="Real time temperature readings",
                labels={"temp": "Temperature (°C)", "timestamp": "Time"},
                color_discrete_sequence=["blue"])

                fig.update_layout(xaxis_title="Time",yaxis_title="Temperature (°C)")
    
            return fig
