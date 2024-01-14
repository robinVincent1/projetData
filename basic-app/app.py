from pathlib import Path
from shiny import ui, render, App
import pandas as pd

df = pd.read_csv(Path(__file__).parent / "Extraction-finale_enquete-2023DS.csv")

app_ui = ui.page_fluid(
    ui.output_table("salmon_species"),
)

def server(output):
    @output
    @render.table
    def salmon_species():
        return df

app = App(app_ui, server)