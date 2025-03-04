from typing import Callable
from htmltools import TagList
from great_tables import data
import pointblank as pb
import polars as pl
from shiny import module, reactive, ui, Inputs, Outputs, Session

from .validation import validation_server, validation_ui

# ============================================================
# Module: airqual
# ============================================================

aq_label = "validated_airquality"


@module.ui
def airqual_ui() -> TagList:
    return [ui.h2("Air Quality Data"), validation_ui(aq_label)]


@module.server
def airqual_server(user_in: Inputs, output: Outputs, session: Session, num_rows: Callable):
    @reactive.calc
    def aq_data() -> pl.DataFrame:
        return pl.DataFrame(data.airquality).with_columns(
            pl.col("Wind") * -1,
        )

    @reactive.calc
    def aq_validator() -> pb.Validate:
        schema = pb.Schema(
            columns=[
                ("Ozone", "Float64"),
                ("Solar_R", "Float64"),
                ("Wind", "Float64"),
                ("Temp", "Int64"),
                ("Month", "Int64"),
                ("Day", "Int64"),
            ]
        )
        valid = (
            pb.Validate(aq_data(), thresholds=(0, 0, 0), label="Air Quality Validation")
            .col_schema_match(schema, complete=True)
            .col_vals_ge("Wind", 0)
            .col_vals_between("Month", 6, 12)
            .interrogate()
        )
        return valid

    validation_server(aq_label, num_rows, aq_data, aq_validator)
