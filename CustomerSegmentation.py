#!/usr/bin/env python
# coding: utf-8

# In[4]:


import pandas as pd 

data = pd.read_excel("Online Retail.xlsx")

data.head()


# In[5]:


import os 
print(os.getcwd())


# In[6]:


data.info()


# In[7]:


data.isnull().sum()


# In[8]:


data_clean = data.dropna(subset = ['CustomerID'])


# In[9]:


data_clean.info()


# In[10]:


data_clean['Revenue'] = data_clean['Quantity'] * data_clean['UnitPrice']
data_clean[['Quantity', 'UnitPrice', 'Revenue']].head()


# In[11]:


data_clean[data_clean['Quantity'] < 0].head()


# In[12]:


(data_clean['Quantity'] < 0).sum()


# In[13]:


data_clean['Revenue'].describe()


# In[18]:


data_clean[data_clean["InvoiceNo"].astype(str).str.startswith("C")].head()


# In[19]:


data_clean["InvoiceNo"].astype(str).str.startswith("C").sum()


# In[20]:


data_rfm = data_clean[data_clean["Quantity"] > 0].copy()


# In[22]:


data_rfm = data_clean["Revenue"] = data_rfm["Quantity"] * data_rfm["UnitPrice"]


# In[23]:


data_rfm = data_clean[data_clean["Quantity"] > 0].copy()


# In[24]:


data_rfm.shape


# In[25]:


data_rfm["Revenue"] = (
    data_rfm["Quantity"] * data_rfm["UnitPrice"]
)


# In[26]:


data_rfm["InvoiceDate"].max()


# In[27]:


snapshot_date = pd.Timestamp("2011-12-10")

rfm = data_rfm.groupby("CustomerID").agg({
    "InvoiceDate": lambda x: (snapshot_date - x.max()).days,
    "InvoiceNo": "nunique",
    "Revenue": "sum"
})

rfm.columns = ["Recency", "Frequency", "Monetary"]

rfm.head()


# In[28]:


rfm.describe()


# In[30]:


rfm.info()


# In[36]:


rfm["R_Score"] = pd.qcut(
    rfm["Recency"],
    5,
    labels = [5,4,3,2,1]
)


# In[40]:


rfm["F_Score"] = pd.qcut(
    rfm["Frequency"].rank(method = "first"),
    5,
    labels = [1,2,3,4,5]
)


# In[41]:


rfm["M_Score"] = pd.qcut(
    rfm["Monetary"],
    5,
    labels = [1,2,3,4,5]
)


# In[42]:


rfm["RFM_Score"] = (
    rfm["R_Score"].astype(str)
    + rfm["F_Score"].astype(str)
    + rfm["M_Score"].astype(str)
)


# In[43]:


rfm.head()


# In[44]:


rfm["RFM_Score"].value_counts().head(10)


# In[47]:


rfm = rfm.drop(columns = ["R_score", "F_score", "M_score"])


# In[48]:


rfm.head()


# In[49]:


def segment_customer(row):
    r = int(row['R_Score'])
    f = int(row['F_Score'])
    m = int(row['M_Score'])

    if r >= 4 and f >= 4 and m >= 4:
        return 'Champions'

    elif r>= 3 and f>= 4:
        return 'Loyal Customers'

    elif r >= 4 and f >= 2:
        return 'Potential Loyalists'

    elif r <= 2 and f>= 3:
        return 'At Risk'

    elif r <= 2 and f <= 2:
        return 'Lost Customers'

    else:
        return 'Other'


# In[50]:


rfm['Segment'] = rfm.apply(segment_customer, axis = 1)


# In[51]:


rfm['Segment'].value_counts()


# In[52]:


segment_percentage = (
    rfm["Segment"]
    .value_counts(normalize = True)
    .mul(100)
    .round(2)
)

segment_percentage


# In[53]:


segment_revenue = (
    rfm.groupby("Segment")["Monetary"]
    .agg(["count", "sum", "mean"])
    .sort_values("sum", ascending = False)
)

segment_revenue


# In[54]:


import matplotlib.pyplot as plt

rfm["Segment"].value_counts().plot(kind = "bar")

plt.title("Customer Segments")
plt.xlabel("Segment")
plt.ylabel("Number of Customers")
plt.xticks(rotation = 45)

plt.show()


# In[55]:


segment_revenue["sum"].plot(kind= "bar")

plt.title("Revneue by Customer Segment")
plt.xlabel("Segment")
plt.ylabel("Revenue")

plt.show()


# In[56]:


rfm.to_csv("rfm_customer_segments.csv")


# In[60]:


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Page Config
st.set_page_config(
    page_title="Customer Segmentation Dashboard",
    page_icon="📊",
    layout="wide"
)

# Load Data
df = pd.read_csv("rfm_customer_segments.csv")

# Title
st.title("📊 Customer Segmentation Dashboard")
st.markdown("RFM Analysis of Retail Customers")

# KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Customers", len(df))

with col2:
    st.metric("Total Revenue", f"£{df['Monetary'].sum():,.0f}")

with col3:
    st.metric("Average Customer Value",
              f"£{df['Monetary'].mean():,.0f}")

with col4:
    champions = len(df[df["Segment"] == "Champions"])
    st.metric("Champions", champions)

# Segment Distribution
st.subheader("Customer Segment Distribution")

segment_counts = df["Segment"].value_counts()

fig, ax = plt.subplots(figsize=(8, 4))
segment_counts.plot(kind="bar", ax=ax)
plt.xticks(rotation=45)

st.pyplot(fig)

# Revenue by Segment
st.subheader("Revenue by Segment")

segment_revenue = (
    df.groupby("Segment")["Monetary"]
    .sum()
    .sort_values(ascending=False)
)

fig, ax = plt.subplots(figsize=(8, 4))
segment_revenue.plot(kind="bar", ax=ax)

st.pyplot(fig)

# Filter
st.subheader("Customer Details")

segment_filter = st.selectbox(
    "Select Segment",
    ["All"] + sorted(df["Segment"].unique())
)

if segment_filter != "All":
    filtered_df = df[df["Segment"] == segment_filter]
else:
    filtered_df = df

st.dataframe(filtered_df)


# In[ ]:





# In[ ]:




