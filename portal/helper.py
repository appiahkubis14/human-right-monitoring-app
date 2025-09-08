import random
import hashlib

def generate_code(name, prefix="EGL"):
    """
    Generates a code in the format:
      PREFIX - XXHHHH - NN - NNN - NN
    where:
      - PREFIX is passed in (e.g., FARM, ENUM, SOC)
      - XX are the first two letters of the name in uppercase
      - HHHH are the first 5 characters of an MD5 hash of the name
      - NN is a random two-digit number
      - NNN is a random three-digit number
      - NN is a random two-digit number (padded with zero if needed)
    """
    if not name:
        # Fallback in case name is empty.
        name = "Unknown"
    part1 = name[:2].upper()
    hash_obj = hashlib.md5(name.encode())
    part2 = hash_obj.hexdigest()[:5].upper()
    part3 = f"{random.randint(10,99)}"
    part4 = f"{random.randint(100,999)}"
    part5 = f"{random.randint(1,99):02d}"
    return f"{prefix}-{part1}{part2}-{part3}-{part4}-{part5}"
