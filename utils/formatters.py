from datetime import datetime
import logging


"""
    Utility functions for formatting and converting data types.
"""
def format_dob(dob: str) -> tuple[str, str]:
    """
        Convert date of birth to both YYYY-MM-DD for showing the user in the future and MMDDYY for simple 2FA.
    """
    if dob is None:
        logging.error("Received None for date of birth.")
        raise ValueError("Date of Birth is required but was not provided.")

    try:
        date_obj = datetime.strptime(dob, "%Y-%m-%d") 
        dob_full = date_obj.strftime("%Y-%m-%d")
        dob_6digit = date_obj.strftime("%m%d%y")
        return dob_full, dob_6digit
    except ValueError as e:
        logging.error(f"Error in converting DOB '{dob}': {e}")
        raise ValueError("Invalid Date of Birth format. Expected YYYY-MM-DD.")

def iso_to_datetime(timestamp_str: str) -> datetime:
    """
        Convert an ISO 8601 string to a datetime object.
    """
    try:
        if timestamp_str.endswith("Z"):
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        else:
            timestamp = datetime.fromisoformat(timestamp_str)

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=datetime.timezone.utc)
        
        return timestamp
    except ValueError:
        raise ValueError(f"Invalid timestamp format: {timestamp_str}")
    except Exception as e:
        raise RuntimeError(f"Error converting timestamp: {e}")

def format_data_for_json(attempts: list[dict]) -> list[dict]:
    """
        Format data for JSON output.
    """
    formatted_attempts = [
    {
      "date": date.isoformat(),
      "avg_accuracy": vals[0],
      "avg_reaction_time": vals[1]
    }
    for date, vals in sorted(attempts.items())
]
    return formatted_attempts