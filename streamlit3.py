import streamlit as st
import pandas as pd
import os
import time

file_paths = [
    "Mojoudi-be-hamrahe-mogheiat-va-dastgah.xlsx",
    "Mojoudi-be-hamrahe-gheymat.xlsx",
    "Latest update of Alternative parts.xlsx",
    "Kala-Model-Dastgah.xlsx",
    "stock_overview.xls"
]

@st.cache_data
def load_file(file_path):
    if os.path.isfile(file_path):
        with st.spinner(f"بارگیری فایل: {file_path}..."):
            df = pd.read_excel(file_path)
            return df
    else:
        st.error(f"فایل {file_path} یافت نشد.")

dfs = []
for file_path in file_paths:
    df = load_file(file_path)
    dfs.append(df)

storage = pd.DataFrame()

kala_model_dastgah = dfs[3]
required_columns = ["کد کالا", "نام فارسی کالا", "گروه کالا", "برند", "نام انگلیسی مدل"]
kala_model_dastgah = kala_model_dastgah[required_columns]
gheymat_file_path = "Mojoudi-be-hamrahe-gheymat.xlsx"
gheymat_data = load_file(gheymat_file_path)
storage = pd.concat([storage, kala_model_dastgah], axis=1)

storage["نام کامل قطعه"] = storage["نام فارسی کالا"] + " - " + storage["نام انگلیسی مدل"]

mogheiat_dastgah = dfs[0]
gheymat_dastgah = gheymat_data[["کد کالا", "قیمت اول"]]
anbar_data = load_file("Mojoudi-be-hamrahe-gheymat.xlsx")
anbar_dastgah = anbar_data[["کد کالا", "نام انبار"]]
storage = pd.merge(storage, anbar_dastgah, how="left", on="کد کالا")
storage = pd.merge(storage, gheymat_dastgah, how="left", on="کد کالا")
mogheiat_dastgah = mogheiat_dastgah.groupby("PartNo")["موجودی در دسترس غیر امانی"].sum().reset_index()
storage = pd.merge(storage, mogheiat_dastgah, how="left", left_on="کد کالا", right_on="PartNo")
storage = storage.rename(columns={"موجودی در دسترس غیر امانی": "sum"})

st.dataframe(storage)

brand_filter = st.sidebar.selectbox("فیلتر برند", storage["برند"].unique(), key="brand_filter")
model_filter = st.sidebar.selectbox("فیلتر نام انگلیسی مدل", storage[storage["برند"] == brand_filter]["نام انگلیسی مدل"].unique(), key="model_filter")
group_filter = st.sidebar.multiselect("فیلتر گروه کالا", storage["گروه کالا"].unique(), key="group_filter")

filtered_data = storage[
    (storage["برند"] == brand_filter) &
    (storage["نام انگلیسی مدل"] == model_filter) &
    (storage["گروه کالا"].isin(group_filter))
]

st.dataframe(filtered_data)

filtered_data = filtered_data.drop(columns=["نام فارسی کالا", "کد کالا"])

widget_counter = 0  # شمارنده ویجت‌ها

anbar_filter = st.sidebar.selectbox(
    "فیلتر نام انبار",
    ["انتخاب نشده"] + storage["نام انبار"].fillna("نامشخص").unique(),
    key=f"anbar_filter_{widget_counter}"
)

widget_counter += 1  # افزایش شمارنده برای ویجت بعدی

progress_text = "Operation in progress. Please wait."
my_bar = st.progress(0, text=progress_text)

for percent_complete in range(100):
    time.sleep(0.01)
    my_bar.progress(percent_complete + 1, text=progress_text)

time.sleep(1)
my_bar.empty()

st.button("Rerun")
