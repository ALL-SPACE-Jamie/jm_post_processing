import os
tlm_type = 'Tx'
def find_files_with_qr(directory):
    # List to store file names with "QR" and the next 14 characters
    qr_files = []

    # List all files in the directory
    for file in os.listdir(directory):
        # Check if "QR" is in the file name
        if "QR" in file:
            # Find the position of "QR" in the file name
            qr_index = file.find("QR")
            # Extract "QR" and the next 14 characters
            qr_and_next_chars = file[qr_index:qr_index + 16]  # "QR" + 14 characters
            qr_files.append(qr_and_next_chars)

    return qr_files

# Example usage
directory = r'C:\Users\RyanFairclough\Downloads\P18_TLMs'
qr_files = find_files_with_qr(directory)
print("Files with 'QR' and the next 14 characters:")

unique_nums = set()

for file in qr_files:

    start_index = file.find('QR')
    if start_index != -1:
        num = file[start_index + 2:start_index + 16]
        if num not in unique_nums:
            unique_nums.add(num)
            print(file)
        if tlm_type == 'Rx':
            if '420' in file:
                print('----------------Wrong QR Code Detected----------------')
        if tlm_type == 'Tx':
            if '440' in file:
                print('----------------Wrong QR Code Detected----------------')
        else:
            print('All QR Codes are correct')


