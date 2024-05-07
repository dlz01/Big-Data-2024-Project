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
        ui.input_text_area("columns", "Columns to filter:"),
        ui.input_radio_buttons(
            "column_type", "Include/Exclude Columns", ["Include", "Exclude", "All"], inline=True
        ),
        ui.download_button("download", "Download Filtered Dataset"),
        ui.download_button("download_filtered_out", "Download Rows Filtered Out"),
        width=320
    ),
    ui.card(
        ui.output_text("text")),
    ui.card(
        ui.card_header("Filtered Dataset"), 
        ui.output_data_frame("filtered"), height="400px"),
    ui.card(
        ui.card_header("Rows Filtered Out"), 
        ui.output_data_frame("filtered_out"), height="400px"),
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
    
    def process_columns(df, columns_string, column_type):
        columns_list = [col.strip() for col in columns_string.split(',')]
        valid_columns = [col for col in columns_list if col in df.columns]

        if not valid_columns or column_type == "All":
            return list(df.columns)
        elif column_type == "Include":
            return valid_columns
        else:
            return [col for col in df.columns if col not in valid_columns]
    
    @render.text
    def text():
        df = parsed_file()

        if df.empty:
            return "Please upload an CSV"
        cols = process_columns(df, input.columns(), input.column_type())
        return f"Columns to filter: {', '.join(cols)}"

    @render.data_frame
    def filtered():
        df = parsed_file()

        if df.empty:
            return render.DataGrid(df)
        cols = process_columns(df, input.columns(), input.column_type())
        processed, _ = process(df, input.filters(), cols)
        return render.DataGrid(processed)
    
    @render.data_frame
    def filtered_out():
        df = parsed_file()

        if df.empty:
            return render.DataGrid(df)
        cols = process_columns(df, input.columns(), input.column_type())
        _, processed_out = process(df, input.filters(), cols)
        return render.DataGrid(processed_out, selection_mode="rows")
    
    @render.download(filename="filtered.csv")
    async def download():
        yield filtered.data_view().to_string(index=False)
    
    @render.download(filename="filtered.csv")
    async def download_filtered_out():
        yield filtered_out.data_view().to_string(index=False)

app = App(app_ui, server)