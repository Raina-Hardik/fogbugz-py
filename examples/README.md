# FogBugz Python Client Examples

This directory contains standalone examples demonstrating various usage patterns of the FogBugzClient library.

## Running Examples

Each example is a standalone Python script that can be run independently:

```bash
uv run examples/01_fetch_by_id.py
uv run examples/02_search_assigned.py
uv run examples/03_single_filter.py
uv run examples/04_multiple_filters.py
uv run examples/05_custom_search.py
uv run examples/06_iterate_and_group.py
uv run examples/07_date_filtering.py
uv run examples/08_compound_status.py
uv run examples/09_case_events.py
uv run examples/10_case_analysis.py
uv run examples/11_pending_customer_emails.py
uv run examples/12_open_bugs_with_correspondent.py
```

## Example Overview

### 01_fetch_by_id.py
Basic case retrieval by ID. Shows how to fetch a single case and access its fields.

### 02_search_assigned.py
Raw search queries with string patterns. Demonstrates searching for cases assigned to a specific person.

### 03_single_filter.py
Structured filtering with a single parameter. Shows the Pythonic find() API with one filter.

### 04_multiple_filters.py
Combining multiple filters. Demonstrates AND-logic filtering with status, priority, and area.

### 05_custom_search.py
Complex search queries with limits. Shows raw search syntax and pagination.

### 06_iterate_and_group.py
Pythonic iteration and data analysis. Demonstrates list comprehensions, filtering, and grouping cases by status.

### 07_date_filtering.py
Client-side date range filtering. Finds cases updated within a specific time period using datetime parameters.

### 08_compound_status.py
Handling FogBugz compound statuses. Shows error handling when status lookup fails and guidance on available status values.

### 09_case_events.py
Retrieving and analyzing case events. Demonstrates fetching all events for a case, including comments, assignments, and status changes with filtering capabilities.

### 10_case_analysis.py
Comprehensive case lifecycle analysis. Shows how to combine case metadata with event history for detailed analysis of case timeline, contributors, and communication patterns.

### 11_pending_customer_emails.py
Finding tickets awaiting responses. Identifies tickets where the last event was a customer email and calculates how long since the internal team responded.

### 12_open_bugs_with_correspondent.py
List all open bugs with correspondent email. Demonstrates accessing the `sCustomerEmail` field to identify who is corresponding on each case.

## Configuration

All examples use the automatic configuration loading from FogBugzClient. Make sure you have a valid `config.toml` file in the project root with your FogBugz credentials and URL. See `config.example.toml` for the required format.

## Output Format

Examples use `structlog` for structured JSON logging, making output machine-readable and easy to parse.
