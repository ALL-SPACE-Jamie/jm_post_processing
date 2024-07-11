import os
import matplotlib.pyplot as plt
import numpy as np

Failed_Folder_Name = r'C:\Users\RyanFairclough\ALL.SPACE\Engineering - P-Type\Tx_TLM_Rev_175-0182_v1\TLM_Calibration_Measurements\Alg2'
colours = ("green", "red")
labels = ["PASS", "Fail"]


path = r'C:\Users\RyanFairclough\ALL.SPACE\Engineering - P-Type\Tx_TLM_Rev_175-0182_v1\TLM_Calibration_Measurements\Alg2\Batch_3_For_P2\Batch_3_For_P2_BB\Raw_Data'
dir_list = os.listdir(path)


filtered_list = [value for value in dir_list if value.startswith("2024")]
print("Filtered List:", filtered_list)


Failed_path = os.path.join(path, Failed_Folder_Name)


if os.path.isdir(Failed_path):

    archive_files = os.listdir(Failed_path)
    print("Files in 'Failed' directory:", archive_files)
else:
    print("The 'Failed' directory does not exist.")
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

fig.savefig(r'C:\Users\RyanFairclough\ALL.SPACE\Engineering - P-Type\Tx_TLM_Rev_175-0182_v1\TLM_Calibration_Measurements\Alg2\Batch_3_For_P2\Batch_3_For_P2_BB\Raw_Data/pie.png')