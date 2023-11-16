from math import ceil

chunk_size = 100
total_amount = 44648
for chunk_low in range(0, ceil(total_amount / chunk_size) * chunk_size, chunk_size):
    chunk_up = min(chunk_low + chunk_size, total_amount)
    print(f"{chunk_up}/{total_amount} ({chunk_up / total_amount * 100:.1f}%)")
