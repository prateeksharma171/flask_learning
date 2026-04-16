def validate_required(data, fields):
    missing = [f for f in fields if not data.get(f)]

    if missing:
        messages = [f"missing {field} field" for field in missing]

        return {
            "status": "error",
            "messages": messages
        }, 400

    return None