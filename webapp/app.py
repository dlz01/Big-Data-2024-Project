# pip install Pillow
# pip install shiny
from shiny import App, ui, render, reactive
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
import io
import tempfile
import pandas as pd

from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shiny.types import FileInfo

from process import process

filtered_df = pd.DataFrame()
filtered_out_df = pd.DataFrame()

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_file("file1", "Choose CSV File", accept=[".csv"], multiple=False),
        ui.input_checkbox_group(
            "filters",
            "Filters",
            choices=["Misspelling/Abbreviation", "Invalid value", "NULL value"],
            selected=["Misspelling/Abbreviation", "Invalid value", "NULL value"],
        ), 
        ui.download_button("download", "Download Filtered Dataset"),
        width=300
    ),
    ui.card(
        ui.card_header("Filtered Dataset"), 
        ui.output_data_frame("filtered"), height="400px"),
    ui.card(
        ui.card_header("Rows Filtered Out"), 
        ui.output_data_frame("filtered_out"), height="400px"),
        ui.input_action_button("remove", "Remove"),
)


def server(input: Inputs, output: Outputs, session: Session):
    
    @reactive.calc
    def parsed_file():
        file: list[FileInfo] | None = input.file1()
        if file is None:
            return pd.DataFrame()
        return pd.read_csv(  # pyright: ignore[reportUnknownMemberType]
            file[0]["datapath"]
        )

    @render.data_frame
    def filtered():
        df = parsed_file()

        if df.empty:
            return render.DataGrid(df)
        processed, processed_out = process(df, input.filters())
        return render.DataGrid(processed)
    
    @render.data_frame
    def filtered_out():
        df = parsed_file()

        if df.empty:
            return render.DataGrid(df)
        # processed, processed_out = process(filtered.data_view(), input.filters())
        processed, processed_out = process(df, input.filters())
        return render.DataGrid(processed_out, selection_mode="rows")
    
    @render.download(filename="filtered.csv")
    async def download():
        yield filtered.data_view().to_string(index=False)



app = App(app_ui, server)