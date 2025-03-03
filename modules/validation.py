from collections.abc import Callable
from htmltools import Tag
from shiny import module, reactive, render, ui, Inputs, Outputs, Session
from great_tables import GT, style, loc
from great_tables.shiny import render_gt, output_gt
import pointblank as pb
import polars as pl
import polars.selectors as cs

# ============================================================
# Module: validation
# ============================================================

@module.ui
def validation_ui() -> ui._navs.NavSet:
    return ui.navset_card_underline(
        ui.nav_panel("Data Preview", output_gt("data_table")),
        ui.nav_panel("Overall Report", output_gt("report_table")),
        ui.nav_panel("Individual Steps", ui.output_ui("ui_select_step"), output_gt("step_table"))
    )


@module.server
def validation_server(
    user_in: Inputs,
    output: Outputs,
    session: Session,
    num_rows: Callable[[], int],
    dataframe: Callable[[], pl.DataFrame],
    valfxn: Callable[[], pl.DataFrame],
    table: Callable[[], GT] | None = None
):

    @render_gt
    def data_table() -> GT:
        if table is not None:
            return table()
        else:
            df: pl.DataFrame = dataframe()
            return (
                GT(df.head(num_rows()).with_row_index())
                .tab_style(
                    style.fill("#ebf5fb"),
                    loc.body(columns=cs.all(), rows=~pl.col("index").mod(2).cast(bool)),
                )
                .tab_style(style.text(weight="bold"), loc.column_header())
                .cols_hide("index")
            )

    @reactive.calc
    def valid() -> pb.Validate:
        validated = valfxn()
        return validated

    @render_gt
    def report_table():
        return valid().get_tabular_report(title="MLRC Report")

    @render.ui
    def ui_select_step() -> Tag:
        n_failures = valid().n_failed()

        choices = {
            "Successes": {
                step: f"Step {step}" for step, n in n_failures.items() if n == 0
            },
            "Failures": {
                step: f"Step {step} ({n} failures)" for step, n in n_failures.items() if n > 0
            },
        }
        return ui.input_select("select_step", "Select Validation Step", choices=choices)

    @render_gt
    def step_table() -> GT:
        step = int(user_in.select_step())
        print(f"{step=}")
        return valid().get_step_report(step)
