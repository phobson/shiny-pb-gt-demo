from shiny import App, ui

from modules.aq import airqual_ui, airqual_server
from modules.cars import cars_ui, cars_server


app_ui = ui.page_fluid(
    ui.input_slider("n", "Rows in Data Preview", 0, 50, 10, step=5),
    ui.navset_tab(
        ui.nav_panel("Air Quality", airqual_ui("air")),
        ui.nav_panel("Cars", cars_ui("cars")),
    )
)


def server(user_in, output, session):
    _aq = airqual_server("air", user_in.n)
    _cars = cars_server("cars", user_in.n)


app = App(app_ui, server)
