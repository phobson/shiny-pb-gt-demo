from great_tables import data
import pointblank as pb
import polars as pl
from shiny import module, reactive, ui

from .validation import validation_server, validation_ui

# ============================================================
# Module: cars
# ============================================================

cars_label = "validated_cars"


@module.ui
def cars_ui():
    return [
        ui.h2("Cars Data"),
        ui.input_select("select_drivetrain", "Select Drivetrain Type", ["rwd", "awd"]),
        validation_ui(cars_label),
    ]


@module.server
def cars_server(user_in, output, session, num_rows):
    @reactive.calc
    def car_data():
        drivetrain = user_in.select_drivetrain()
        return pl.DataFrame(data.gtcars).with_columns(pl.col("hp") * -1).filter(pl.col("drivetrain").eq(drivetrain))

    @reactive.calc
    def cars_validator():
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

    validation_server(cars_label, num_rows, car_data, cars_validator)
