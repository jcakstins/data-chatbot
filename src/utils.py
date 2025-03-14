
def convert_to_json(rows, column_names):
    results = []
    for row in rows:
        row_dict = dict(zip(column_names, row))
        results.append(row_dict)

        # Serialize the results and column names into a JSON string
    json_data ={"columns": column_names, "data": results}
    return json_data


def json_to_markdown_table(json_data):
    # Extract columns and data from JSON
    columns = json_data["columns"]
    data = json_data["data"]

    # Generate Markdown table header
    markdown_table = "| " + " | ".join(columns) + " |\n"
    markdown_table += "| " + " | ".join(["---"] * len(columns)) + " |\n"

    # Generate Markdown table rows
    for row in data:
        markdown_table += "| " + " | ".join(str(row[column]) for column in columns) + " |\n"

    return markdown_table
