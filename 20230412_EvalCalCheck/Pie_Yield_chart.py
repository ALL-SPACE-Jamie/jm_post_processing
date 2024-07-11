import os
import matplotlib.pyplot as plt
import numpy as np

Failed_Folder_Name = "Failed"
colours = ("green", "red")
labels = ["PASS", "Fail"]

# Get the list of all files and directories in the specified path
path = r'C:\Users\RyanFairclough\ALL.SPACE\Engineering - P-Type\Tx_TLM_Rev_175-0182_v1\TLM_Rework\NC-126\Post_rework_eval'
dir_list = os.listdir(path)

# Filter the list to include only items that start with "2024"
filtered_list = [value for value in dir_list if value.startswith("2024")]
print("Filtered List:", filtered_list)

# Define the path to the "archive" subdirectory
archive_path = os.path.join(path, Failed_Folder_Name)

# Check if the "archive" directory exists
if os.path.isdir(archive_path):
    # Get the list of files in the "archive" directory
    archive_files = os.listdir(archive_path)
    print("Files in 'archive' directory:", archive_files)
else:
    print("The 'archive' directory does not exist.")
    archive_files = []

print("Passed_TLMs_in_Folder:", len(filtered_list))
print("Failed_TLMs_in_Folder:", len(archive_files))

y = np.array([len(filtered_list), len(archive_files)])
print(y)

fig, ax = plt.subplots(figsize=(10, 7))

# Add percentage labels to the pie chart
def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct * total / 100.0))
        return f'{pct:.1f}% ({val:d})'
    return my_autopct

ax.pie(y, autopct=make_autopct(y), labels=labels, colors=colours)
plt.show()

fig.savefig(r'C:/Users/RyanFairclough/ALL.SPACE/Engineering - P-Type/Tx_TLM_Rev_175-0182_v1/TLM_Rework\NC-126/Post_rework_eval/pie.png')