import glob
import os

filePath = r'C:\Users\RyanFairclough\Downloads\Eval060224'

files = glob.glob(os.path.join(filePath,'*'))
sorted_files = sorted(files,key=lambda x: x[-5:])
for file in sorted_files:
    print(file)