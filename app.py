import os
from functools import reduce

import pandas as pd
import streamlit as st


class MyDict(dict):
    def __init__(self, *args, **kwargs):
        super(MyDict, self).__init__(*args, **kwargs)
        self.keys_set = set()

    def __setitem__(self, key, value):
        if key in self:
            st.warning(
                f"Warning: Key {key} already exists. Renaming it to {key}_1", icon="❗️"
            )
            key = f"{key}_1"
        self.keys_set.add(key)
        super(MyDict, self).__setitem__(key, value)


st.title("合并数据表格")

uploaded_files = st.file_uploader(
    "上传一个或多个 Excel 或 CSV 文件",
    type=["xlsx", "xls", "csv"],
    accept_multiple_files=True,
)

if uploaded_files:
    dfs = MyDict()
    file_names = []
    for file in uploaded_files:
        file_names.append(file.name)
        if file.name.endswith("xlsx") or file.name.endswith("xls"):
            data = pd.read_excel(file, sheet_name=None)
            data = {
                f"{os.path.splitext(file.name)[0]}-{key}": value
                for key, value in data.items()
            }
            for key, value in data.items():
                dfs[key] = value
        elif file.name.endswith("csv"):
            data = pd.read_csv(file)
            dfs[f"{os.path.splitext(file.name)[0]}"] = data

    tab_titles = list(dfs.keys())
    tabs = st.tabs(tab_titles)

    for tab, df in zip(tabs, dfs.values()):
        with tab:
            st.write(df)

    columns = st.multiselect(
        label="基于哪些列进行合并",
        options=list(dfs.values())[0].columns.tolist(),
        help="参考 [pandas.merge](https://pandas.pydata.org/docs/reference/api/pandas.merge.html) 中的 on 参数",
    )

    how_option = st.radio(
        label="合并方式",
        options=["left", "right", "inner", "outer"],
        index=None,
        horizontal=True,
        help="参考 [pandas.merge](https://pandas.pydata.org/docs/reference/api/pandas.merge.html) 中的 how 参数",
    )

    if columns and how_option:
        merged_df = reduce(
            lambda left, right: pd.merge(left, right, on=columns, how=how_option),
            dfs.values(),
        )

        st.write("合并后的数据表：")
        st.dataframe(merged_df)
        st.balloons()
