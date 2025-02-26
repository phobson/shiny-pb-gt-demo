from shiny import module, reactive, render, ui
from great_tables import GT
from great_tables.shiny import render_gt, output_gt

# ============================================================
# Module: validation
# ============================================================

@module.ui
def validation_ui():
    return ui.navset_card_underline(
        ui.nav_panel("Data Preview", output_gt("data_table")),
        ui.nav_panel("Overall Report", output_gt("report_table")),
        ui.nav_panel("Individual Steps", ui.output_ui("ui_select_step"), output_gt("step_table"))
    )


@module.server
def validation_server(user_in, output, session, num_rows, dataframe, valfxn):

    @render_gt
    def data_table():
        return GT(dataframe().head(num_rows()))

    @reactive.calc
    def valid():
        validated = valfxn()
        return validated

    @render_gt
    def report_table():
        return valid().get_tabular_report(title="MLRC Report")

    @render.ui
    def ui_select_step():
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
    def step_table():
        step = int(user_in.select_step())
        print(f"{step=}")
        return valid().get_step_report(step)
