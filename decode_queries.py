import base64

# Decode các queries từ Augment VIP
count_query_b64 = "U0VMRUNUIENPVU5UKCopIEZST00gSXRlbVRhYmxlIFdIRVJFIGtleSBMSUtFICclYXVnbWVudCUnOw=="
delete_query_b64 = "REVMRVRFIEZST00gSXRlbVRhYmxlIFdIRVJFIGtleSBMSUtFICclYXVnbWVudCUnOw=="

count_query = base64.b64decode(count_query_b64).decode()
delete_query = base64.b64decode(delete_query_b64).decode()

print("Count query:", count_query)
print("Delete query:", delete_query)

# Decode các VSCode keys
vscode_keys = ["dGVsZW1ldHJ5Lm1hY2hpbmVJZA==", "dGVsZW1ldHJ5LmRldkRldmljZUlk", "dGVsZW1ldHJ5Lm1hY01hY2hpbmVJZA==", "c3RvcmFnZS5zZXJ2aWNlTWFjaGluZUlk"]

print("\nVSCode keys:")
for key in vscode_keys:
    decoded = base64.b64decode(key).decode()
    print(f"  {decoded}")
