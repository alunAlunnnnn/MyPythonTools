with open(r'D:\a\0.bin', 'rb') as f:
    data = f.read()
print(data)
with open(r'D:\a\0.txt', 'w') as f:
    f.write(str(data))