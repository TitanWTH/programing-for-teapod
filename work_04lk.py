import pandas as pd

source_df = pd.read_csv("products_dirty_v2.csv")
df = source_df.copy()

print("Початковий розмір:", df.shape)
print("Початкові стовпці:", list(df.columns))
print("\nПочаткові типи:")
print(df.dtypes)
print("\nПочаткові пропуски:")
print(df.isna().sum())
print("\nПовні дублікати:", df.duplicated().sum())
print("\nПовторення product_id:")
print(df[df["product_id"].duplicated(keep=False)])

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_", regex=False)
)

for column in ["product", "category", "warehouse"]:
    df[column] = df[column].astype("string").str.strip()

df["product"] = df["product"].str.title()
df["category"] = df["category"].str.upper()
df["warehouse"] = df["warehouse"].str.upper()

df["price"] = pd.to_numeric(df["price"], errors="coerce")
df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")

print("\nПропуски після перетворення чисел:")
print(df.isna().sum())

bad_price = ~df["price"].between(0, 100000, inclusive="right")
df.loc[bad_price, "price"] = pd.NA

bad_quantity = ~df["quantity"].between(0, 500, inclusive="both")
df.loc[bad_quantity, "quantity"] = pd.NA

quantity_median = df["quantity"].median()
df["quantity"] = df["quantity"].fillna(quantity_median)

df = df.dropna(subset=["product_id", "product"])
df = df.drop_duplicates()

products_review = df[df["price"].isna()].copy()

print("\nПісля очищення:")
print("Розмір:", df.shape)
print("\nТипи:")
print(df.dtypes)
print("\nПропуски:")
print(df.isna().sum())
print("\nПовні дублікати:", df.duplicated().sum())
print("\nКатегорії:")
print(df["category"].value_counts(dropna=False))
print("\nСклади:")
print(df["warehouse"].value_counts(dropna=False))
print("\nМінімальна ціна:", df["price"].min())
print("Максимальна ціна:", df["price"].max())
print("Сума quantity:", df["quantity"].sum())
print("\nПовторення product_id після очищення:")
print(df[df["product_id"].duplicated(keep=False)])

df.to_csv("products_clean_v2.csv", index=False, encoding="utf-8-sig")
products_review.to_csv("products_review_v2.csv", index=False, encoding="utf-8-sig")

print("\nФайли збережено:")
print("products_clean_v2.csv")
print("products_review_v2.csv")