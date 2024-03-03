import pandas as pd

# Create your two lists
a = [1, 2]
b = [5, 6, 10]

# Create DataFrames from the lists
df_a = pd.DataFrame(a, columns=["Column_B"])
df_b = pd.DataFrame(b, columns=["Column_B"])

# Add the DataFrames element-wise
result_df = df_a + df_b
print(result_df)
