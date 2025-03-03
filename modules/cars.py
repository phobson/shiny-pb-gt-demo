from collections.abc import Callable

from htmltools import TagList
from great_tables import data, GT, loc, style
import pointblank as pb
import polars as pl
import polars.selectors as cs
from shiny import module, reactive, ui, Inputs, Outputs, Session

from .validation import validation_server, validation_ui

# ============================================================
# Module: cars
# ============================================================

cars_label = "validated_cars"


@module.ui
def cars_ui() -> TagList:
    return [
        ui.h2("Cars Data"),
        ui.input_select("select_drivetrain", "Select Drivetrain Type", ["rwd", "awd"]),
        validation_ui(cars_label),
    ]


@module.server
def cars_server(user_in: Inputs, output: Outputs, session: Session, num_rows: Callable[[], int]):
    @reactive.calc
    def car_data() -> pl.DataFrame:
        drivetrain = user_in.select_drivetrain()
        return pl.DataFrame(data.gtcars).with_columns(pl.col("hp") * -1).filter(pl.col("drivetrain").eq(drivetrain))

    @reactive.calc
    def cars_validator() -> pb.Validate:
        schema = pb.Schema(
            columns=[
                ("mfr", "String"),
                ("model", "String"),
                ("year", "Int64"),
                ("trim", "String"),
                ("bdy_style", "String"),
                ("hp", "Float64"),
                ("hp_rpm", "Float64"),
                ("trq", "Float64"),
                ("trq_rpm", "Float64"),
                ("mpg_c", "Float64"),
                ("mpg_h", "Float64"),
                ("drivetrain", "String"),
                ("trsmn", "String"),
                ("ctry_origin", "String"),
                ("msrp", "Float64"),
            ]
        )
        valid = (
            pb.Validate(car_data(), thresholds=(0, 0, 0), label="Cars Validation")
            .col_schema_match(schema, complete=True)
            .col_vals_ge("hp", 0)
            .col_vals_ge("hp_rpm", 5500)
            .col_vals_in_set("bdy_style", ["coupe", "sedan", "convertible"])
            .col_vals_in_set("ctry_origin", ["Germany", "Italy", "United Kingdom", "United States"])
            .interrogate()
        )
        return valid

    @reactive.calc
    def cars_table() -> GT:
        return (
            GT(car_data().head(num_rows()).with_row_index("index"))
            .tab_style(
                style.fill("#ebf5fb"),
                loc.body(columns=cs.all(), rows=~pl.col("index").mod(2).cast(bool)),
            )
            .tab_style(style.text(weight="bold"), loc.column_header())
            .cols_hide("index")
            .fmt_currency("msrp", use_subunits=False)
            .fmt_integer(cs.starts_with("hp") | cs.starts_with("trq"))
            .tab_header("Sports Car Specs and Price")
            .tab_spanner(label="Performance", columns=cs.starts_with("hp") | cs.starts_with("trq"))
            .tab_spanner(label="Economy ({{mpg}})", columns=cs.starts_with("mpg"))
            .tab_spanner(
                label="Model Info", columns=~(cs.starts_with("hp") | cs.starts_with("trq") | cs.starts_with("mpg"))
            )
            .cols_label(
                {
                    "mfr": "Make",
                    "model": "Model",
                    "year": "Year",
                    "trim": "Package",
                    "bdy_style": "Body",
                    "drivetrain": "Drivetrain",
                    "trsmn": "Transmission",
                    "ctry_origin": "Country",
                    "msrp": "MSRP",
                    "hp": "Power ({{hp}})",
                    "hp_rpm": "Engine Speed @ Max. Power ({{rev / min}})",
                    "trq": "Torque ({{ft-lbs}})",
                    "trq_rpm": "Engine Speed @ Max. Torque ({{rev / min}})",
                    "mpg_c": "City",
                    "mpg_h": "Highway",
                }
            )
        )

    validation_server(cars_label, num_rows, car_data, cars_validator, cars_table)
