import math
from typing import Optional

def format_bytes_to_pretty_str(size_bytes: Optional[int]) -> Optional[str]:
    """
    Converts a size in bytes to a human-readable string format (e.g., 1.2 MiB).
    Returns None if the input is None.
    Returns '0 Bytes' if the input is 0.
    """
    if size_bytes is None:
        return None
    if size_bytes == 0:
        return "0 Bytes"

    size_name = ("Bytes", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB")
    # Prevent log(0) or log of negative by returning '0 Bytes' or handling negative as error/abs value
    if size_bytes < 0: # Or handle as an error, for now, let's treat as 0 or abs.
        # For simplicity, let's return as if it's 0, or you could raise ValueError
        return "0 Bytes" # Or format_bytes_to_pretty_str(abs(size_bytes))

    i = int(math.floor(math.log(size_bytes, 1024))) if size_bytes > 0 else 0


    p = math.pow(1024, i)
    s = round(size_bytes / p, 1)

    if i == 0: # For Bytes, display as integer without decimal point
        return f"{int(size_bytes)} {size_name[i]}" # Display exact bytes for the 'Bytes' unit
    else:
        return f"{s} {size_name[i]}"

if __name__ == '__main__':
    # Test cases
    print(f"None -> {format_bytes_to_pretty_str(None)}")
    print(f"0 -> {format_bytes_to_pretty_str(0)}")
    print(f"100 -> {format_bytes_to_pretty_str(100)}")
    print(f"1023 -> {format_bytes_to_pretty_str(1023)}")
    print(f"1024 -> {format_bytes_to_pretty_str(1024)}")
    print(f"1500 -> {format_bytes_to_pretty_str(1500)}")
    print(f"1048576 -> {format_bytes_to_pretty_str(1048576)}")
    print(f"1600000 -> {format_bytes_to_pretty_str(1600000)}")
    print(f"2345678901 -> {format_bytes_to_pretty_str(2345678901)}")
    print(f"1 -> {format_bytes_to_pretty_str(1)}")
    print(f"-100 -> {format_bytes_to_pretty_str(-100)}") 