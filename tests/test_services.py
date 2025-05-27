import os
from src import services
from google.cloud.bigquery.table import Row
import datetime as dt


def test_irr_pipeline(repository_with_cashflows):
    """
    GIVEN some cashflows on bq
    WHEN they are processed by irr_pipeline() service
    THEN the expected results should be populated into the correct destination table
    """
    services.irr_pipeline(repository_with_cashflows)

    results = repository_with_cashflows.get(
        f"SELECT * FROM {os.environ['DATASET']}.{os.environ['DESTINATION_TABLE']} ORDER BY entity_name, date"
    )
    expected_results = [
        Row(
            ("Test Account 1", 0.1, 2.1384, dt.date(2022, 2, 1)),
            {"entity_name": 0, "irr_monthly": 1, "irr_annual": 2, "date": 3},
        ),
        Row(
            ("Test Account 1", 0.1, 2.1384, dt.date(2022, 3, 1)),
            {"entity_name": 0, "irr_monthly": 1, "irr_annual": 2, "date": 3},
        ),
        Row(
            ("Test Account 1", 0.1, 2.1384, dt.date(2022, 4, 1)),
            {"entity_name": 0, "irr_monthly": 1, "irr_annual": 2, "date": 3},
        ),
        Row(
            ("Test Account 1", 0.1, 2.1384, dt.date(2022, 5, 1)),
            {"entity_name": 0, "irr_monthly": 1, "irr_annual": 2, "date": 3},
        ),
        Row(
            ("Test Account 2", 0.1, 2.1384, dt.date(2022, 4, 1)),
            {"entity_name": 0, "irr_monthly": 1, "irr_annual": 2, "date": 3},
        ),
    ]

    for result, expected_result in zip(results, expected_results):
        assert result == expected_result
