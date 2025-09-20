import os
import pandas as pd
from typing import Literal


def merge_and_sort_excel_files_in_folder(folder_path, output_file, sort_by: Literal["loop", "concurrency"] = "loop"):
    all_data = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith((".xlsx", ".xls")):
                file_path = os.path.join(root, file)
                try:
                    df = pd.read_excel(file_path)
                    all_data.append(df)
                except Exception as e:
                    print(f"读取文件 {file_path} 出错: {e}")
                else:
                    print(f"文件 {file_path} 处理完成.")

    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)

        if sort_by == "concurrency":
            combined_df = combined_df.sort_values(by=["Input Length", "Output Length", "Concurrency"])
        elif sort_by == "loop":
            # 多级排序，先按 Input Length、Output Length、Loop 排序，再按 Concurrency 排序
            combined_df = combined_df.sort_values(by=["Input Length", "Output Length", "Loop", "Concurrency"])

        combined_df.to_excel(output_file, index=False)
        print(f"合并后文件: {output_file}")
    else:
        print("未找到有效的 Excel 文件。")


folder_path = "/Users/ryanyang/Downloads/yongsen/results"
output_file = "/Users/ryanyang/Downloads/yongsen/combined_file.xlsx"
merge_and_sort_excel_files_in_folder(folder_path, output_file, sort_by="loop")
