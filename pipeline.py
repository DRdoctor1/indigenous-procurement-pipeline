# A corrupted row from a government tender feed:
broken_record = "CN-2026-003|Northern BC|NOT_A_NUMBER"


parts = broken_record.split("|")
tender_id = parts[0]
region = parts[1]


try:
    clean_value = float(parts[2])
except ValueError:
    clean_value = 0.0
    pass

# 3. Print the results
print("Tender ID:", tender_id)
print("Region:", region)
print("Clean Value:", clean_value)