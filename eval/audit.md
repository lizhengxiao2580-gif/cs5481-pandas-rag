# Per-question grading audit

Initial model-assisted judgments and evidence-based corrections are preserved separately.

Initial scores were produced with model assistance and checked against source evidence and reproducible examples. A project member subsequently completed human review and confirmed the existing scores. This is model-assisted evaluation with human review, rather than independent blind human ratings.

## Q01 — basic

How can I read only the name and age columns from a CSV file with pandas?

**Gold answer:** Use pd.read_csv(path, usecols=['name', 'age']). usecols selects a subset of columns.

**Required points:** Select columns at read time with usecols=['name', 'age'].

### fixed_size

Use `pd.read_csv` with the `usecols` argument [1]. For example, assuming the CSV header contains columns named `name` and `age`:

```python
import pandas as pd
df = pd.read_csv("file.csv", usecols=["name", "age"])
```

The `usecols` argument allows selecting a subset of columns using column names, position numbers, or a callable [1].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly uses usecols=['name','age'] and explains it. All claims are supported by cited passage.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [user_guide/io](https://pandas.pydata.org/docs/user_guide/io.html#csv-text-files) | The usecols argument allows you to select any subset of the columns in a file, either using the column names, position numbers or a callable: |
| 2 | False | [getting_started/intro_tutorials/03_subset_data](https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html#how-do-i-select-a-subset-of-a-dataframe) | Passage is about selecting columns from a DataFrame, not reading CSV with usecols. |
| 3 | False | [reference/api/pandas.read_csv](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html) | Only function signature and general parameters, no specific usecols explanation. |
| 4 | False | [user_guide/cookbook](https://pandas.pydata.org/docs/user_guide/cookbook.html#data-in-out) | Unrelated CSV parsing examples. |
| 5 | False | [getting_started/intro_tutorials/01_table_oriented](https://pandas.pydata.org/docs/getting_started/intro_tutorials/01_table_oriented.html#what-kind-of-data-does-pandas-handle) | Introductory DataFrame creation, not relevant. |

### structure_aware

You can use the `usecols` argument of `pandas.read_csv` to select only the `"name"` and `"age"` columns by passing them as a list of column names [1][2]:

```python
import pandas as pd

df = pd.read_csv("data.csv", usecols=["name", "age"])
```

`usecols` accepts strings that correspond to column names inferred from the document header row [2]. This assumes the CSV file has a header row containing columns named `name` and `age`; by default, pandas infers column names from the first non-blank line of the file [3]. Element order in `usecols` is ignored, so if you need a specific column order, select after reading [2].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly uses usecols=['name','age'] and explains it. All claims are supported by cited passages.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [user_guide/io](https://pandas.pydata.org/docs/user_guide/io.html#csv-text-files) | The usecols argument allows you to select any subset of the columns in a file, either using the column names, position numbers or a callable: |
| 2 | True | [user_guide/io](https://pandas.pydata.org/docs/user_guide/io.html#csv-text-files) | The usecols argument allows you to select any subset of the columns in a file, either using the column names, position numbers or a callable: |
| 3 | True | [user_guide/io](https://pandas.pydata.org/docs/user_guide/io.html#csv-text-files) | usecolslist-like or callable, default None Return a subset of the columns. If list-like, all elements must either be positional (i.e. integer indices into the document columns) or strings that correspond to column names provided either by the user in names or inferred from the document header row(s). |
| 4 | False | [reference/api/pandas.read_csv](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html) | Only function signature and general parameters, no specific usecols explanation. |
| 5 | False | [getting_started/intro_tutorials/03_subset_data](https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html#how-do-i-select-a-subset-of-a-dataframe) | Title only, no substantive content. |

## Q02 — basic

How do I write a DataFrame to CSV without writing the row index?

**Gold answer:** Use df.to_csv(path, index=False); index controls writing the row names, and defaults to True.

**Required points:** Set index=False when calling to_csv.

### fixed_size

To write a DataFrame to CSV without the row index, pass `index=False` to `DataFrame.to_csv` [1].

```python
df.to_csv("out.csv", index=False)
```

This creates a CSV file without row indices [2]. The `index` parameter defaults to `True`, which is why row names are written unless you disable it [1].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly states index=False and explains the default. All claims are supported by cited passages.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [reference/api/pandas.DataFrame.to_csv](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html) | indexbool, default True Write row names (index). |
| 2 | True | [reference/api/pandas.DataFrame.to_csv](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html) | Create ‘out.csv’ containing ‘df’ without indices >>> df = pd.DataFrame( ... [["Raphael", "red", "sai"], ["Donatello", "purple", "bo staff"]], ... columns=["name", "mask", "weapon"], ... ) >>> df.to_csv("out.csv", index=False) |
| 3 | False | [user_guide/io](https://pandas.pydata.org/docs/user_guide/io.html#csv-text-files) | Text discusses to_string and JSON writing, not CSV index control. |
| 4 | False | [user_guide/io](https://pandas.pydata.org/docs/user_guide/io.html#parquet) | Text is about Parquet serialization, not CSV. |
| 5 | False | [reference/api/pandas.DataFrame.to_excel](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_excel.html) | Text is about Excel writing, not CSV. |

### structure_aware

To write a DataFrame to CSV without writing the row index, pass `index=False` to `DataFrame.to_csv()` [1][2]. The `index` parameter defaults to `True`, which writes row names [1][3].

```python
df.to_csv("out.csv", index=False)
```

The documentation example creates `out.csv` containing `df` without indices using this argument [2].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly states index=False and explains the default. All claims are supported by cited passages.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [reference/api/pandas.DataFrame.to_csv](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html) | indexbool, default True Write row names (index). |
| 2 | True | [reference/api/pandas.DataFrame.to_csv](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html) | Create ‘out.csv’ containing ‘df’ without indices >>> df = pd.DataFrame( ... [["Raphael", "red", "sai"], ["Donatello", "purple", "bo staff"]], ... columns=["name", "mask", "weapon"], ... ) >>> df.to_csv("out.csv", index=False) |
| 3 | False | [reference/api/pandas.DataFrame.to_excel](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_excel.html) | Text is about Excel writing, not CSV. |
| 4 | True | [user_guide/io](https://pandas.pydata.org/docs/user_guide/io.html#csv-text-files) | index: whether to write row (index) names (default True) |
| 5 | False | [user_guide/10min](https://pandas.pydata.org/docs/user_guide/10min.html#importing-and-exporting-data) | Text shows CSV writing without index=False and does not explain how to omit the index. |

## Q03 — basic

How can I keep rows whose country column is either UK or JP?

**Gold answer:** Use df[df['country'].isin(['UK', 'JP'])]. isin returns a Boolean membership mask.

**Required points:** Use isin with the list of allowed values and use its Boolean mask to filter rows.

### fixed_size

Assuming `df` has a string column named `country`, use:

```python
df[df["country"].isin(["UK", "JP"])]
```

This works because `Series.isin` returns a boolean mask that is `True` where the series element is in the supplied list, and putting that mask inside `[]` selects the matching rows [1][2].

An equivalent form using an OR condition is:

```python
df[(df["country"] == "UK") | (df["country"] == "JP")]
```

The docs show this equivalence for filtering rows where a column is either of two values [2].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly uses isin with a list and boolean mask to filter rows, satisfying the required point. The alternative OR condition is also supported by cited passages.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [user_guide/indexing](https://pandas.pydata.org/docs/user_guide/indexing.html#boolean-indexing) | Consider the isin() method of Series, which returns a boolean vector that is true wherever the Series elements exist in the passed list. |
| 2 | True | [getting_started/intro_tutorials/03_subset_data](https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html#how-do-i-filter-specific-rows-from-a-dataframe) | Similar to the conditional expression, the isin() conditional function returns a True for each row the values are in the provided list. |
| 3 | True | [user_guide/10min](https://pandas.pydata.org/docs/user_guide/10min.html#selection) | Using isin() method for filtering: |
| 4 | False | [user_guide/io](https://pandas.pydata.org/docs/user_guide/io.html#hdf5-pytables) | Passage discusses HDFStore query syntax, not relevant to isin filtering. |
| 5 | True | [user_guide/indexing](https://pandas.pydata.org/docs/user_guide/indexing.html#indexing-with-isin) | row_mask = df.isin(values).all(axis=1) |

### structure_aware

Use boolean indexing inside the selection brackets. Assuming `df` is a DataFrame with a `country` column, you can use `isin` to keep rows where `country` is either `"UK"` or `"JP"` [1][2]:

```python
filtered = df[df["country"].isin(["UK", "JP"])]
```

`isin()` returns `True` for each row whose value is in the provided list [2].

Alternatively, combine two equality conditions with the `|` operator; each condition must be surrounded by parentheses, and you cannot use `or` [2][3]:

```python
filtered = df[(df["country"] == "UK") | (df["country"] == "JP")]
```

The parenthesis and `|` usage is also documented for boolean indexing [3].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **2**.

Answer correctly uses isin with a list and boolean mask to filter rows, satisfying the required point. The alternative OR condition is also supported by cited passages.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | False | [getting_started/intro_tutorials/03_subset_data](https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html#how-do-i-select-a-subset-of-a-dataframe) | Passage only contains a heading 'How do I select a subset of a DataFrame?' with no substantive evidence about isin or filtering. |
| 2 | True | [getting_started/intro_tutorials/03_subset_data](https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html#how-do-i-filter-specific-rows-from-a-dataframe) | In [16]: class_23 = titanic[titanic["Pclass"].isin([2, 3])] |
| 3 | True | [getting_started/intro_tutorials/03_subset_data](https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html#how-do-i-filter-specific-rows-from-a-dataframe) | Similar to the conditional expression, the isin() conditional function returns a True for each row the values are in the provided list. |
| 4 | True | [user_guide/indexing](https://pandas.pydata.org/docs/user_guide/indexing.html#boolean-indexing) | Using a boolean vector to index a Series works exactly as in a NumPy ndarray: |
| 5 | False | [user_guide/io](https://pandas.pydata.org/docs/user_guide/io.html#hdf5-pytables) | Passage discusses HDFStore query syntax, not relevant to isin filtering. |

## Q04 — basic

How do I drop a row if either its name or age is missing, while ignoring missing values in other columns?

**Gold answer:** Use df.dropna(subset=['name', 'age'], how='any'). subset restricts considered columns; any drops rows with at least one missing value.

**Required points:** Use subset=['name','age'] to restrict missing-value checks.; Use how='any' to remove a row if either selected value is missing.

### fixed_size

Use `df.dropna(subset=["name", "age"])` to drop rows where either the `name` or `age` column has a missing value, while ignoring missing values in all other columns [1][2]. By default, `how='any'` drops a row if any of the subset columns contain NA values [2].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly uses df.dropna(subset=['name','age']) and explains default how='any'. Both required points are covered and supported by cited passages.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [reference/api/pandas.DataFrame.dropna](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.dropna.html) | Define in which columns to look for missing values. >>> df.dropna(subset=["name", "toy"]) |
| 2 | True | [reference/api/pandas.DataFrame.dropna](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.dropna.html) | how{‘any’, ‘all’}, default ‘any’ Determine if row or column is removed from DataFrame, when we have at least one NA or all NA. ‘any’ : If any NA values are present, drop that row or column. |
| 3 | False | [getting_started/intro_tutorials/03_subset_data](https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html#how-do-i-filter-specific-rows-from-a-dataframe) | Passage discusses notna() and boolean indexing, not dropna with subset. |
| 4 | False | [user_guide/indexing](https://pandas.pydata.org/docs/user_guide/indexing.html#boolean-indexing) | Passage discusses DataFrame.filter, unrelated to dropna. |
| 5 | True | [user_guide/10min](https://pandas.pydata.org/docs/user_guide/10min.html#missing-data) | DataFrame.dropna() drops any rows that have missing data: |

### structure_aware

Use `DataFrame.dropna` with the `subset` parameter to restrict missing-value checking to only the `"name"` and `"age"` columns [1][2]:

```python
df.dropna(subset=["name", "age"])
```

By default, `axis=0` drops rows and `how="any"` drops a row if any of the specified subset columns is missing [2]. Columns not listed in `subset` are ignored, as shown in the example where missing values in `"born"` do not affect dropping based on `"name"` and `"toy"` [1].

This assumes your columns are named exactly `"name"` and `"age"` and that `df` is the DataFrame [1][2].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly uses df.dropna(subset=['name','age']) and explains default how='any'. Both required points are covered and supported by cited passages.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [reference/api/pandas.DataFrame.dropna](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.dropna.html) | Define in which columns to look for missing values. >>> df.dropna(subset=["name", "toy"]) |
| 2 | True | [reference/api/pandas.DataFrame.dropna](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.dropna.html) | how{‘any’, ‘all’}, default ‘any’ Determine if row or column is removed from DataFrame, when we have at least one NA or all NA. ‘any’ : If any NA values are present, drop that row or column. |
| 3 | False | [user_guide/missing_data](https://pandas.pydata.org/docs/user_guide/missing_data.html#dropping-missing-data) | Passage only shows basic dropna usage without subset or how='any' explanation relevant to the required points. |
| 4 | False | [getting_started/intro_tutorials/03_subset_data](https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html#how-do-i-filter-specific-rows-from-a-dataframe) | Passage discusses notna() and boolean indexing, not dropna with subset. |
| 5 | False | [user_guide/indexing](https://pandas.pydata.org/docs/user_guide/indexing.html#boolean-indexing) | Passage discusses DataFrame.filter, unrelated to dropna. |

## Q05 — basic

How can I fill missing values in column A with 0 and column B with 'unknown', leaving other columns alone?

**Gold answer:** Use df.fillna({'A': 0, 'B': 'unknown'}). A mapping supplies per-column replacement values; unspecified columns are not filled.

**Required points:** Pass a per-column dictionary to fillna.; Columns absent from the mapping remain unfilled.

### fixed_size

Use `DataFrame.fillna` with a dictionary mapping column names to fill values [1][2]. The `value` parameter accepts a dict specifying which value to use for each column, and values not in the dict are not filled, so other columns remain unchanged [2].

```python
df = df.fillna(value={"A": 0, "B": "unknown"})
```

Or modify in place:

```python
df.fillna(value={"A": 0, "B": "unknown"}, inplace=True)
```

This assumes column B can accept the string `"unknown"` [2][3].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **2**.

Answer correctly uses df.fillna with a dictionary and states unspecified columns are not filled. Both required points are supported by cited passages. The optional assumption about dtype is not a material factual error and is not required to be cited.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | False | [reference/api/pandas.DataFrame.fillna](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.fillna.html) | Passage discusses filling with a DataFrame and notes column D is not affected, but does not mention per-column dictionary filling or that unspecified columns remain unfilled. |
| 2 | True | [reference/api/pandas.DataFrame.fillna](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.fillna.html) | Value to use to fill holes (e.g. 0), alternately a dict/Series/DataFrame of values specifying which value to use for each index (for a Series) or column (for a DataFrame). Values not in the dict/Series/DataFrame will not be filled. |
| 3 | True | [reference/api/pandas.DataFrame.fillna](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.fillna.html) | Replace all NaN elements in column ‘A’, ‘B’, ‘C’, and ‘D’, with 0, 1, 2, and 3 respectively. >>> values = {"A": 0, "B": 1, "C": 2, "D": 3} >>> df.fillna(value=values) |
| 4 | False | [user_guide/missing_data](https://pandas.pydata.org/docs/user_guide/missing_data.html#filling-missing-data) | Passage discusses filling with None, np.nan, pd.NA, and ffill/bfill, not per-column dictionary filling. |
| 5 | False | [user_guide/basics](https://pandas.pydata.org/docs/user_guide/basics.html#flexible-binary-operations) | Passage discusses arithmetic fill_value and missing data operations, not per-column dictionary filling. |

### structure_aware

Use `DataFrame.fillna` with a dictionary that maps column names to replacement values:

```python
df = df.fillna({"A": 0, "B": "unknown"})
```

`fillna` accepts a dict of values specifying which value to use for each column, and values not in the dict will not be filled [1]. This means column `A` is filled with `0`, column `B` is filled with `'unknown'`, and any other columns are left unchanged [1][2]. The same column-specific filling is shown in the pandas missing-data documentation using a dictionary such as `{"np": 0, "arrow": 1}` [2].

Assumption: column `B` has an object/string dtype or can otherwise accept the string `'unknown'` [2].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **2**.

Answer correctly uses df.fillna with a dictionary and states unspecified columns are not filled. Both required points are supported by cited passages. The optional assumption about dtype is not a material factual error and is not required to be cited.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | False | [reference/api/pandas.DataFrame.fillna](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.fillna.html) | Passage discusses filling with a DataFrame and notes column D is not affected, but does not mention per-column dictionary filling or that unspecified columns remain unfilled. |
| 2 | True | [reference/api/pandas.DataFrame.fillna](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.fillna.html) | Value to use to fill holes (e.g. 0), alternately a dict/Series/DataFrame of values specifying which value to use for each index (for a Series) or column (for a DataFrame). Values not in the dict/Series/DataFrame will not be filled. |
| 3 | True | [user_guide/missing_data](https://pandas.pydata.org/docs/user_guide/missing_data.html#filling-missing-data) | Replace NA with column-specific values using a dict In [103]: df.fillna({"np": 0, "arrow": 1}) |
| 4 | False | [getting_started/comparison/comparison_with_stata](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_stata.html#missing-data) | Passage discusses dropna, ffill, and filling with mean, not per-column dictionary filling. |
| 5 | True | [reference/api/pandas.DataFrame.fillna](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.fillna.html) | Replace all NaN elements in column ‘A’, ‘B’, ‘C’, and ‘D’, with 0, 1, 2, and 3 respectively. >>> values = {"A": 0, "B": 1, "C": 2, "D": 3} >>> df.fillna(value=values) |

## Q06 — basic

How do I calculate mean sales separately for each combination of region and product?

**Gold answer:** Use df.groupby(['region', 'product'])['sales'].mean(). A list of grouping column names forms combination groups.

**Required points:** Group by both columns using a list, select sales, and compute mean.

### fixed_size

Use `groupby` with a list of the grouping columns, then calculate the mean for the sales column:

```python
mean_sales = df.groupby(["region", "product"])["sales"].mean()
```

The docs show that grouping by multiple columns and calling `mean()` produces means for each combination, such as each `Store`-`Product` combination for revenue and quantity [1]. You can also use `.agg` with a dictionary to apply `"mean"` to a specific column, as shown with `tips.groupby(["smoker", "day"]).agg({"tip": ["size", "mean"]})` [2].

This assumes the columns are named `"region"`, `"product"`, and `"sales"` and that you want the mean of `"sales"` for each unique `"region"`-`"product"` combination [1][2].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly uses groupby with a list of columns and mean, and the .agg alternative is supported by retrieved passages. All material claims are cited.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [user_guide/groupby](https://pandas.pydata.org/docs/user_guide/groupby.html#other-useful-features) | df.groupby(["Store", "Product"]).pipe(mean) |
| 2 | True | [getting_started/comparison/comparison_with_sql](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_sql.html#group-by) | Grouping by more than one column is done by passing a list of columns to the groupby() method. |
| 3 | False | [user_guide/cookbook](https://pandas.pydata.org/docs/user_guide/cookbook.html#grouping) | Passage discusses pivot_table with sum and margins, not mean for multiple column combinations. |
| 4 | False | [getting_started/comparison/comparison_with_sas](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_sas.html#groupby) | Passage shows groupby with sum and transformation, not mean for multiple columns. |
| 5 | True | [reference/api/pandas.DataFrame.pivot_table](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.pivot_table.html) | >>> table = pd.pivot_table( ... df, ... values=["D", "E"], ... index=["A", "C"], ... aggfunc={"D": "mean", "E": ["min", "max", "mean"]}, ... ) |

### structure_aware

Assuming your DataFrame has columns `region`, `product`, and numeric `sales`:

```python
df.groupby(["region", "product"])["sales"].mean()
```

Grouping by more than one column is done by passing a list of columns to `groupby()` [1]. This computes the mean for each combination of the grouping columns by using the split-apply-combine approach [1][2]. Alternatively, you can use `pivot_table`:

```python
pd.pivot_table(df, values="sales", index=["region", "product"], aggfunc="mean")
```

A pivot table can calculate aggregations such as `"mean"` for a value column by combinations of the specified index columns [3].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **2**.

Answer provides the correct groupby syntax with a list of columns and mean, and the pivot_table alternative is supported by retrieved passages. All material claims are cited.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | False | [getting_started/intro_tutorials/09_timeseries](https://pandas.pydata.org/docs/getting_started/intro_tutorials/09_timeseries.html#using-pandas-datetime-properties) | Passage discusses grouping by datetime hour and computing mean, but does not mention grouping by multiple columns or selecting a specific column for mean. |
| 2 | True | [getting_started/comparison/comparison_with_sql](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_sql.html#group-by) | Grouping by more than one column is done by passing a list of columns to the groupby() method. |
| 3 | False | [user_guide/io](https://pandas.pydata.org/docs/user_guide/io.html#json) | Passage contains unrelated JSON data and no evidence about grouping or mean calculation. |
| 4 | True | [reference/api/pandas.DataFrame.pivot_table](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.pivot_table.html) | >>> table = pd.pivot_table( ... df, ... values=["D", "E"], ... index=["A", "C"], ... aggfunc={"D": "mean", "E": ["min", "max", "mean"]}, ... ) |
| 5 | False | [getting_started/comparison/comparison_with_sas](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_sas.html#groupby) | Passage shows groupby with multiple columns and sum, not mean, and does not directly support the required mean calculation. |

## Q07 — basic

How do I reshape a wide table into long format while keeping id as an identifier and unpivoting only Jan and Feb?

**Gold answer:** Use pd.melt(df, id_vars=['id'], value_vars=['Jan', 'Feb']). id_vars stay as identifiers; value_vars select measured columns to unpivot.

**Required points:** Set id_vars=['id'] to preserve the identifier.; Set value_vars=['Jan','Feb'] to select the unpivoted columns.

### fixed_size

Use `pandas.melt` / `DataFrame.melt` and specify:

- `id_vars='id'` to keep `id` as the identifier column [1][2]
- `value_vars=['Jan', 'Feb']` to unpivot only those two columns [1][2]

By default, the unpivoted result will have two non-identifier columns named `variable` and `value` [1][3]. You can rename them with `var_name` and `value_name` [1][2].

Assuming your DataFrame has columns named `id`, `Jan`, and `Feb`:

```python
long = df.melt(id_vars='id', value_vars=['Jan', 'Feb'])
```

With custom output column names:

```python
long = df.melt(
    id_vars='id',
    value_vars=['Jan', 'Feb'],
    var_name='month',
    value_name='amount',
)
```

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly uses pd.melt with id_vars='id' and value_vars=['Jan','Feb'], satisfying both required points. All material claims are supported by cited passages [1], [2], and [3].

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [reference/api/pandas.melt](https://pandas.pydata.org/docs/reference/api/pandas.melt.html) | id_varsscalar, tuple, list, or ndarray, optional Column(s) to use as identifier variables. |
| 2 | True | [getting_started/intro_tutorials/07_reshape_table_layout](https://pandas.pydata.org/docs/getting_started/intro_tutorials/07_reshape_table_layout.html#wide-to-long-format) | value_vars=["BETR801", "FR04014", "London Westminster"] |
| 3 | True | [user_guide/reshaping](https://pandas.pydata.org/docs/user_guide/reshaping.html#stack-and-unstack) | cheese.melt(id_vars=["first", "last"]) |
| 4 | False | [user_guide/io](https://pandas.pydata.org/docs/user_guide/io.html#json) | Passage contains unrelated JSON data and does not provide evidence for the required points. |
| 5 | False | [user_guide/reshaping](https://pandas.pydata.org/docs/user_guide/reshaping.html#reshaping-and-pivot-tables) | Passage is a general overview of reshaping methods and does not specifically support id_vars or value_vars for Jan/Feb. |

### structure_aware

Use `pandas.melt()` with `id_vars="id"` and `value_vars=["Jan", "Feb"]`.

Assuming the wide table has columns `id`, `Jan`, and `Feb`:

```python
long = pd.melt(df, id_vars="id", value_vars=["Jan", "Feb"])
```

This keeps `id` as an identifier and unpivots only the `Jan` and `Feb` columns [1][2]. `value_vars` defines which columns to melt; if omitted, all columns not listed in `id_vars` are used [1][2]. The result contains the `id` column plus the two generated columns: a variable column and a value column, with defaults `variable` and `value` [1]. You can rename those generated columns with `var_name` and `value_name` [1][2].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly uses pd.melt with id_vars='id' and value_vars=['Jan','Feb'], satisfying both required points. All material claims are supported by cited passages [1] and [2].

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [getting_started/intro_tutorials/07_reshape_table_layout](https://pandas.pydata.org/docs/getting_started/intro_tutorials/07_reshape_table_layout.html#wide-to-long-format) | The method will melt all columns NOT mentioned in id_vars together into two columns: |
| 2 | True | [reference/api/pandas.melt](https://pandas.pydata.org/docs/reference/api/pandas.melt.html) | id_varsscalar, tuple, list, or ndarray, optional Column(s) to use as identifier variables. |
| 3 | False | [user_guide/reshaping](https://pandas.pydata.org/docs/user_guide/reshaping.html#melt-and-wide-to-long) | Passage is about wide_to_long, not melt, and does not mention id_vars or value_vars for Jan/Feb. |
| 4 | False | [user_guide/reshaping](https://pandas.pydata.org/docs/user_guide/reshaping.html#pivot-and-pivot-table) | Passage is about pivot, not melt, and does not contain evidence for the required points. |
| 5 | True | [getting_started/intro_tutorials/07_reshape_table_layout](https://pandas.pydata.org/docs/getting_started/intro_tutorials/07_reshape_table_layout.html#wide-to-long-format) | value_vars defines which columns to melt together |

## Q08 — basic

How can I convert only column age to int64 and column score to float64 in a DataFrame?

**Gold answer:** Use df.astype({'age': 'int64', 'score': 'float64'}). A dtype mapping specifies column-specific types; other columns remain unchanged.

**Required points:** Pass a mapping of column names to dtypes to astype.

### fixed_size

Use `DataFrame.astype()` with a dict that maps column names to dtypes:

```python
df = df.astype({"age": "int64", "score": "float64"})
```

`astype()` accepts a mapping of column name to dtype for casting one or more columns [1]. Columns whose labels are absent from the mapping are left unchanged [1]. The same pattern is shown in the docs with `dft1.astype({"a": np.bool_, "c": np.float64})`, where the unlisted column `b` keeps its original dtype [2].

Since `astype()` returns the cast object, assign the result back to the DataFrame [1].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly uses astype with a column-to-dtype mapping and all claims are supported by cited passages.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [user_guide/basics](https://pandas.pydata.org/docs/user_guide/basics.html#dtypes) | Convert certain columns to a specific dtype by passing a dict to astype(). |
| 2 | True | [reference/api/pandas.DataFrame.astype](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.astype.html) | Alternatively, use a mapping, e.g. {col: dtype, …}, where col is a column label and dtype is a numpy.dtype or Python type to cast one or more of the DataFrame’s columns to column-specific types. |
| 3 | False | [user_guide/basics](https://pandas.pydata.org/docs/user_guide/basics.html#dtypes) | Discusses apply and to_numeric, not the astype mapping. |
| 4 | False | [user_guide/basics](https://pandas.pydata.org/docs/user_guide/basics.html#dtypes) | Discusses default dtypes and upcasting, not the mapping to astype. |
| 5 | False | [user_guide/basics](https://pandas.pydata.org/docs/user_guide/basics.html#dtypes) | Discusses select_dtypes and other topics, not the astype mapping. |

### structure_aware

Use `DataFrame.astype()` with a mapping of column names to target dtypes:

```python
df = df.astype({"age": "int64", "score": "float64"})
```

This casts `age` to `int64` and `score` to `float64`; columns not present in the mapping are left unchanged [1][2]. The method returns a new pandas object, so assign the result back to the DataFrame if you want to keep the change [2]. You can also use NumPy dtypes, e.g. `df.astype({"age": np.int64, "score": np.float64})` [1][2].

Avoid assigning through `.loc` for this subset conversion; the docs show `.loc` assignment can upcast and leave the original dtypes unchanged [1].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly uses astype with a column-to-dtype mapping and all claims are supported by cited passages.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [user_guide/basics](https://pandas.pydata.org/docs/user_guide/basics.html#dtypes) | Convert certain columns to a specific dtype by passing a dict to astype(). |
| 2 | True | [user_guide/basics](https://pandas.pydata.org/docs/user_guide/basics.html#dtypes) | Convert a subset of columns to a specified type using astype(). |
| 3 | True | [reference/api/pandas.DataFrame.astype](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.astype.html) | Alternatively, use a mapping, e.g. {col: dtype, …}, where col is a column label and dtype is a numpy.dtype or Python type to cast one or more of the DataFrame’s columns to column-specific types. |
| 4 | False | [user_guide/basics](https://pandas.pydata.org/docs/user_guide/basics.html#dtypes) | Discusses default dtypes and upcasting, not the mapping to astype. |
| 5 | False | [user_guide/basics](https://pandas.pydata.org/docs/user_guide/basics.html#dtypes) | Covers to_numeric and apply, not the astype mapping. |

## Q09 — parameter

With DataFrame.drop_duplicates, how can I remove every occurrence of duplicate ids rather than keeping one? Does this method compare index labels?

**Gold answer:** Use df.drop_duplicates(subset=['id'], keep=False). It removes all duplicate-id rows; index labels are ignored.

**Required points:** subset=['id'] with keep=False removes all occurrences of duplicated ids.; Index labels are ignored by drop_duplicates.

### fixed_size

To remove every occurrence of duplicate values in an `id` column, pass that column as `subset` and use `keep=False`:

```python
df.drop_duplicates(subset=["id"], keep=False)
```

`keep=False` means “Drop all duplicates” [1][2]. If duplicates should be identified using multiple columns, pass a list of those columns as `subset` [1][2].

`DataFrame.drop_duplicates` does not compare index labels. The documentation states: “Indexes, including time indexes are ignored” [1]. It also says: “Duplicates in the index are not considered” [3].

To remove every occurrence of duplicate index labels instead, use `Index.duplicated(keep=False)` with boolean indexing:

```python
df.loc[~df.index.duplicated(keep=False), :]
```

This keeps only rows whose index label occurs once [4][5].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly uses subset=['id'] with keep=False and states index labels are ignored. All claims are supported by cited passages.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [reference/api/pandas.DataFrame.drop_duplicates](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop_duplicates.html) | Indexes, including time indexes are ignored. |
| 2 | True | [reference/api/pandas.DataFrame.drop_duplicates](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop_duplicates.html) | Duplicates in the index are not considered. |
| 3 | True | [user_guide/indexing](https://pandas.pydata.org/docs/user_guide/indexing.html#duplicate-data) | df2.drop_duplicates('a', keep=False) |
| 4 | True | [user_guide/duplicates](https://pandas.pydata.org/docs/user_guide/duplicates.html#duplicate-label-detection) | If you want to remove all occurrences of duplicated labels, you can use keep=False |
| 5 | True | [user_guide/indexing](https://pandas.pydata.org/docs/user_guide/indexing.html#duplicate-data) | df3[~df3.index.duplicated(keep=False)] |

### structure_aware

To remove every occurrence of duplicate ids with `DataFrame.drop_duplicates`, use `keep=False` with `subset` set to the id column:

```python
df.drop_duplicates(subset='id', keep=False)
```

This drops all rows whose `id` value is duplicated, leaving only ids that appear once, assuming `id` is a column label [1][2][3].

`DataFrame.drop_duplicates` does **not** compare index labels. The method ignores indexes, including time indexes [1]. To remove all rows with duplicated index labels, use `Index.duplicated(keep=False)` with boolean indexing [4][5]:

```python
df.loc[~df.index.duplicated(keep=False), :]
```

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly uses subset='id' with keep=False and states index labels are ignored. All claims are supported by cited passages.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [reference/api/pandas.DataFrame.drop_duplicates](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop_duplicates.html) | Indexes, including time indexes are ignored. |
| 2 | True | [reference/api/pandas.DataFrame.drop_duplicates](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop_duplicates.html) | Duplicates in the index are not considered. |
| 3 | True | [user_guide/indexing](https://pandas.pydata.org/docs/user_guide/indexing.html#duplicate-data) | df2.drop_duplicates('a', keep=False) |
| 4 | True | [user_guide/duplicates](https://pandas.pydata.org/docs/user_guide/duplicates.html#duplicate-label-detection) | If you want to remove all occurrences of duplicated labels, you can use keep=False |
| 5 | True | [user_guide/indexing](https://pandas.pydata.org/docs/user_guide/indexing.html#duplicate-data) | keep=False: mark / drop all duplicates. |

## Q10 — parameter

How can Series.value_counts report proportions and include missing values as a counted category?

**Gold answer:** Use s.value_counts(normalize=True, dropna=False). normalize returns relative frequencies and dropna=False includes missing values.

**Required points:** normalize=True returns relative frequencies.; dropna=False includes NA values in the counts.

### fixed_size

To report proportions, set `normalize=True`; this returns relative frequencies of the unique values [1]. To include missing values as a counted category, set `dropna=False`; by default `dropna=True` excludes NaN counts [1], and the documentation shows NaN appearing in the result when `dropna=False` is used [2].

```python
s.value_counts(normalize=True, dropna=False)
```

This combines the documented `normalize` parameter for proportions [1] with the documented `dropna=False` behavior for including NaN [2].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly states normalize=True for proportions and dropna=False for including missing values, both supported by cited passages [1] and [2]. No material factual errors.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [reference/api/pandas.Series.value_counts](https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html) | normalizebool, default False If True then the object returned will contain the relative frequencies of the unique values. |
| 2 | True | [reference/api/pandas.Series.value_counts](https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html) | With dropna set to False we can also see NaN index values. >>> s.value_counts(dropna=False) 3.0 2 1.0 1 2.0 1 4.0 1 NaN 1 |
| 3 | False | [user_guide/reshaping](https://pandas.pydata.org/docs/user_guide/reshaping.html#crosstab) | Passage discusses crosstab, not Series.value_counts; no evidence for required points. |
| 4 | False | [user_guide/basics](https://pandas.pydata.org/docs/user_guide/basics.html#descriptive-statistics) | Passage discusses value_counts on DataFrames and mode, not the normalize/dropna parameters for Series. |
| 5 | False | [getting_started/intro_tutorials/06_calculate_statistics](https://pandas.pydata.org/docs/getting_started/intro_tutorials/06_calculate_statistics.html#count-number-of-records-by-category) | Passage mentions dropna argument in a note but does not provide substantive evidence for the required points. |

### structure_aware

Use `Series.value_counts(normalize=True, dropna=False)` [1][2].

- Set `normalize=True` to report relative frequencies/proportions instead of raw counts [1].
- Set `dropna=False` to include missing values as a counted category [1][2].
- By default, `dropna=True`, so missing values are excluded unless you explicitly set it to `False` [1].

Example:

```python
s.value_counts(normalize=True, dropna=False)
```

This combination returns proportions while also counting NaN values where present [1][2].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly states normalize=True for proportions and dropna=False for including missing values, both supported by cited passages [1] and [2]. No material factual errors.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [reference/api/pandas.Series.value_counts](https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html) | normalizebool, default False If True then the object returned will contain the relative frequencies of the unique values. |
| 2 | False | [user_guide/categorical](https://pandas.pydata.org/docs/user_guide/categorical.html#operations) | Passage discusses categorical data and value_counts showing unused categories, not the dropna parameter for missing values. |
| 3 | False | [user_guide/reshaping](https://pandas.pydata.org/docs/user_guide/reshaping.html#crosstab) | Passage discusses crosstab, not Series.value_counts; no evidence for required points. |
| 4 | True | [reference/api/pandas.Series.value_counts](https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html) | With dropna set to False we can also see NaN index values. >>> s.value_counts(dropna=False) 3.0 2 1.0 1 2.0 1 4.0 1 NaN 1 |
| 5 | False | [getting_started/intro_tutorials/06_calculate_statistics](https://pandas.pydata.org/docs/getting_started/intro_tutorials/06_calculate_statistics.html#count-number-of-records-by-category) | Passage mentions dropna argument in a note but does not provide substantive evidence for the required points. |

## Q11 — parameter

When both merge key columns contain null values, can pandas match those rows together, and is this the same as typical SQL joins?

**Gold answer:** Yes, pandas matches rows whose merge keys are null on both sides. This differs from usual SQL join behavior.

**Required points:** Null keys on both sides can match each other.; This differs from usual SQL join behavior.

### fixed_size

Yes, when both key columns contain rows where the key is null, pandas will match those rows against each other [1][2]. This behavior is not the same as typical SQL joins; the documentation states it is different from usual SQL join behaviour and can lead to unexpected results [1][2].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly states both required points and is fully supported by cited passages.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [getting_started/comparison/comparison_with_sql](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_sql.html#join) | If both key columns contain rows where the key is a null value, those rows will be matched against each other. This is different from usual SQL join behaviour and can lead to unexpected results. |
| 2 | True | [reference/api/pandas.DataFrame.merge](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html) | If both key columns contain rows where the key is a null value, those rows will be matched against each other. This is different from usual SQL join behaviour and can lead to unexpected results. |
| 3 | False | [getting_started/comparison/comparison_with_sql](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_sql.html#join) | No mention of null key matching or SQL difference. |
| 4 | False | [getting_started/comparison/comparison_with_sas](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_sas.html#merging) | No mention of null key matching or SQL difference. |
| 5 | False | [getting_started/comparison/comparison_with_stata](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_stata.html#merging) | No mention of null key matching or SQL difference. |

### structure_aware

Yes. The pandas documentation warns that if both key columns contain rows where the key is a null value, those rows will be matched against each other [1][2]. This is explicitly described as different from usual SQL join behaviour and can lead to unexpected results [1][2].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly states both required points and is fully supported by cited passages.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [getting_started/comparison/comparison_with_sql](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_sql.html#join) | If both key columns contain rows where the key is a null value, those rows will be matched against each other. This is different from usual SQL join behaviour and can lead to unexpected results. |
| 2 | True | [reference/api/pandas.DataFrame.merge](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html) | If both key columns contain rows where the key is a null value, those rows will be matched against each other. This is different from usual SQL join behaviour and can lead to unexpected results. |
| 3 | False | [user_guide/merging](https://pandas.pydata.org/docs/user_guide/merging.html#merge) | No mention of null key matching or SQL difference. |
| 4 | False | [getting_started/comparison/comparison_with_spreadsheets](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_spreadsheets.html#merging) | No mention of null key matching or SQL difference. |
| 5 | False | [getting_started/comparison/comparison_with_sql](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_sql.html#join) | No mention of null key matching or SQL difference. |

## Q12 — parameter

If a nullable Boolean indexing mask contains pd.NA, are those rows selected? How can I retain those rows?

**Gold answer:** Mask NA entries are treated as False. Use mask.fillna(True) before indexing to retain those positions.

**Required points:** NA entries in a Boolean mask are treated as False.; Fill mask NA entries with True to keep those rows.

### fixed_size

With a nullable Boolean indexing mask, rows where the mask is `pd.NA` are **not selected**. pandas treats `NA` values in a boolean array as `False` [1]. For example:

```python
s[mask]  # where mask = pd.array([True, False, pd.NA], dtype="boolean")
```

returns only the row where the mask is `True` [1].

To retain those rows, fill the mask with `True` before indexing:

```python
s[mask.fillna(True)]
```

This keeps the rows where the mask was `pd.NA` [1].

Alternatively, if you are using `DataFrame.filter` with `cond=`, missing values in the mask are treated as `False` by default, but you can pass `na=True` to keep the corresponding rows [2].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly states NA treated as False and provides fillna(True) to retain rows, both supported by cited passage [1]. The optional DataFrame.filter alternative is supported by [2].

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [user_guide/boolean](https://pandas.pydata.org/docs/user_guide/boolean.html#indexing-with-na-values) | pandas allows indexing with NA values in a boolean array, which are treated as False. In [1]: s = pd.Series([1, 2, 3])  In [2]: mask = pd.array([True, False, pd.NA], dtype="boolean")  In [3]: s[mask] Out[3]: 0 1 dtype: int64 If you would prefer to keep the NA values you can manually fill them with fillna(True). |
| 2 | True | [user_guide/indexing](https://pandas.pydata.org/docs/user_guide/indexing.html#boolean-indexing) | Missing values in the mask are treated as False by default, matching df[mask] for a mask with nullable boolean dtype. Pass na=True to keep the corresponding rows instead |
| 3 | False | [user_guide/missing_data](https://pandas.pydata.org/docs/user_guide/missing_data.html#na-semantics) | Discusses NA in boolean context and TypeError, not indexing mask behavior or retaining rows. |
| 4 | False | [user_guide/missing_data](https://pandas.pydata.org/docs/user_guide/missing_data.html#na-semantics) | Discusses Kleene logic and NA propagation, not indexing mask behavior or retaining rows. |
| 5 | False | [user_guide/missing_data](https://pandas.pydata.org/docs/user_guide/missing_data.html#na-semantics) | Discusses NumPy ufuncs and conversion, not indexing mask behavior or retaining rows. |

### structure_aware

No, rows with `pd.NA` in a nullable Boolean mask are not selected; `NA` values are treated as `False` during indexing [1][2].

To retain those rows:

- For direct Boolean indexing, fill the mask with `True` before indexing: `df[mask.fillna(True)]` [1].
- For `DataFrame.filter`, pass `na=True`: `df.filter(cond=mask, na=True)` [2].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly states NA treated as False and provides fillna(True) to retain rows, both supported by cited passage [1]. The optional DataFrame.filter alternative is supported by [2].

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [user_guide/boolean](https://pandas.pydata.org/docs/user_guide/boolean.html#indexing-with-na-values) | pandas allows indexing with NA values in a boolean array, which are treated as False. In [1]: s = pd.Series([1, 2, 3])  In [2]: mask = pd.array([True, False, pd.NA], dtype="boolean")  In [3]: s[mask] Out[3]: 0 1 dtype: int64 If you would prefer to keep the NA values you can manually fill them with fillna(True). |
| 2 | False | [user_guide/missing_data](https://pandas.pydata.org/docs/user_guide/missing_data.html#na-semantics) | Discusses NA in boolean context and TypeError, not indexing mask behavior or retaining rows. |
| 3 | False | [user_guide/10min](https://pandas.pydata.org/docs/user_guide/10min.html#missing-data) | Discusses isna() and missing data, not indexing mask behavior or retaining rows. |
| 4 | True | [user_guide/indexing](https://pandas.pydata.org/docs/user_guide/indexing.html#boolean-indexing) | Missing values in the mask are treated as False by default, matching df[mask] for a mask with nullable boolean dtype. Pass na=True to keep the corresponding rows instead |
| 5 | False | [user_guide/missing_data](https://pandas.pydata.org/docs/user_guide/missing_data.html#na-semantics) | Discusses NumPy ufuncs and conversion, not indexing mask behavior or retaining rows. |

## Q13 — parameter

How do I construct a Series of integers with missing values without converting it to floating point? Is 'Int64' the same spelling as NumPy 'int64'?

**Gold answer:** Specify dtype='Int64', for example pd.Series([1, None], dtype='Int64'). The capital I distinguishes the nullable integer dtype from NumPy int64; missing values become pandas.NA.

**Required points:** Explicitly use nullable Int64 with a capital I.; Missing values are represented by pandas.NA.

### fixed_size

To construct a Series of integers with missing values without converting to floating point, use the nullable integer dtype `"Int64"` (capital `"I"`) in the Series constructor:

```python
pd.Series([1, 2, None], dtype="Int64")
```

This produces:

```
0       1
1       2
2    <NA>
dtype: Int64
```

The missing value is represented as `pandas.NA`, not `NaN` [1][2]. If you omit the `dtype`, `pd.Series([1, None])` infers `float64` with `NaN` [2].

`"Int64"` is not the same spelling as NumPy’s lowercase `"int64"`; the capital `"I"` differentiates pandas’ nullable integer dtype from NumPy’s dtype [1].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly specifies dtype='Int64' with capital I and states missing values are pandas.NA. Both required points are met and supported by cited passages.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [user_guide/integer_na](https://pandas.pydata.org/docs/user_guide/integer_na.html#nullable-integer-data-type) | Or the string alias "Int64" (note the capital "I") to differentiate from NumPy’s 'int64' dtype: |
| 2 | True | [user_guide/gotchas](https://pandas.pydata.org/docs/user_guide/gotchas.html#missing-value-representation-for-numpy-types) | If you need to represent integers with possibly missing values, use one of the nullable-integer extension dtypes provided by pandas or pyarrow |
| 3 | True | [user_guide/integer_na](https://pandas.pydata.org/docs/user_guide/integer_na.html#construction) | In [11]: pd.Series([1, None], dtype="Int64") Out[11]: 0 1 1 <NA> dtype: Int64 |
| 4 | True | [user_guide/integer_na](https://pandas.pydata.org/docs/user_guide/integer_na.html#operations) | In [15]: s = pd.Series([1, 2, None], dtype="Int64") |
| 5 | True | [user_guide/missing_data](https://pandas.pydata.org/docs/user_guide/missing_data.html#values-considered-missing) | NA for StringDtype, Int64Dtype (and other bit widths), Float64Dtype (and other bit widths), BooleanDtype and ArrowDtype. |

### structure_aware

Use the nullable integer extension dtype explicitly when constructing the `Series`, because by default `pd.Series([1, None])` infers `float64` [1][2].

```python
pd.Series([1, None], dtype="Int64")
```

This returns a series with `dtype: Int64` and missing value `<NA>` rather than `NaN`/float [2]. You can also create an `IntegerArray` with `pd.array(..., dtype=pd.Int64Dtype())` and then pass it to `pd.Series()` [1]. All NA-like values are replaced with `pandas.NA` [1][3].

No, `"Int64"` is not the same spelling as NumPy `"int64"`. pandas uses the capital-`"I"` alias `"Int64"` specifically to differentiate from NumPy’s lowercase `'int64'` dtype [1]. The nullable dtype appears as `Int64`, while an ordinary NumPy-backed integer Series appears as `int64` [1][2].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly specifies dtype='Int64' with capital I and states missing values are pandas.NA. Both required points are met and supported by cited passages.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [user_guide/integer_na](https://pandas.pydata.org/docs/user_guide/integer_na.html#construction) | Or the string alias "Int64" (note the capital "I") to differentiate from NumPy’s 'int64' dtype: |
| 2 | True | [user_guide/integer_na](https://pandas.pydata.org/docs/user_guide/integer_na.html#operations) | In [15]: s = pd.Series([1, 2, None], dtype="Int64") |
| 3 | True | [user_guide/gotchas](https://pandas.pydata.org/docs/user_guide/gotchas.html#missing-value-representation-for-numpy-types) | If you need to represent integers with possibly missing values, use one of the nullable-integer extension dtypes provided by pandas or pyarrow |
| 4 | True | [user_guide/integer_na](https://pandas.pydata.org/docs/user_guide/integer_na.html#nullable-integer-data-type) | arrays.IntegerArray uses pandas.NA as its missing value. |
| 5 | True | [user_guide/integer_na](https://pandas.pydata.org/docs/user_guide/integer_na.html#construction) | In [11]: pd.Series([1, None], dtype="Int64") Out[11]: 0 1 1 <NA> dtype: Int64 |

## Q14 — parameter

In Series.map with an ordinary dictionary, what happens to values that have no matching key? How do I avoid applying a function to existing missing values?

**Gold answer:** Unmatched values become NaN for an ordinary dict. Set na_action='ignore' to propagate existing missing values without calling the mapping function on them.

**Required points:** Values absent from an ordinary dictionary become NaN.; na_action='ignore' skips existing missing values.

### fixed_size

With an ordinary dictionary, Series values that are not present as keys in the dictionary are converted to `NaN` [1][2]. Existing missing values are also `NaN` in the result because they are not keys in the dictionary [1].

To avoid applying a function to existing missing values, pass `na_action="ignore"`. This propagates `NaN` values without passing them to the function, keeping them as `NaN` [1][2]:

```python
s.map("I am a {}".format, na_action="ignore")
```

In the example, `NaN` at index 2 stays `NaN` instead of becoming `"I am a nan"` [1].

Correct: **False**; faithful: **False**; refused: **False**; first relevant rank: **1**.

Both required points are present, but the extra statement about existing missing values being absent from dictionary keys is not generally true or established by the cited example. pandas 3.1.1 maps pd.Series([np.nan]) through {np.nan: 7} to [7]. Strict whole-answer correctness and citation faithfulness therefore fail.

Unsupported claims: The additional claim that existing missing values also remain NaN because they are not dictionary keys is overgeneralized: an ordinary dictionary can contain a NaN key.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [reference/api/pandas.Series.map](https://pandas.pydata.org/docs/reference/api/pandas.Series.map.html) | Values that are not found in the dict are converted to NaN, unless the dict has a default value (e.g. defaultdict) |
| 2 | True | [reference/api/pandas.Series.map](https://pandas.pydata.org/docs/reference/api/pandas.Series.map.html) | If ‘ignore’, propagate NaN values, without passing them to the mapping correspondence. |
| 3 | False | [user_guide/gotchas](https://pandas.pydata.org/docs/user_guide/gotchas.html#mutating-with-user-defined-function-udf-methods) | Passage is a traceback from DataFrame.apply, unrelated to Series.map dictionary behavior or na_action. |
| 4 | False | [user_guide/dsintro](https://pandas.pydata.org/docs/user_guide/dsintro.html#series) | Passage discusses Series construction from dict, not Series.map behavior. |
| 5 | False | [user_guide/basics](https://pandas.pydata.org/docs/user_guide/basics.html#function-application) | Passage discusses DataFrame.transform, not Series.map dictionary behavior or na_action. |

### structure_aware

With an ordinary dictionary, `Series.map` converts values that are not found as keys in the dictionary to `NaN` [1][2]. If the dictionary is a `dict` subclass that defines `__missing__`, that default is used instead of `NaN` [1][2].

To avoid applying a function to existing missing values, pass `na_action="ignore"`; `NaN` values are propagated without being passed to the mapping or function [1][2].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Both required points are correctly stated and supported by cited passages. The additional note about dict subclass __missing__ is also supported by the cited text.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [reference/api/pandas.Series.map](https://pandas.pydata.org/docs/reference/api/pandas.Series.map.html) | Values that are not found in the dict are converted to NaN, unless the dict has a default value (e.g. defaultdict) |
| 2 | True | [reference/api/pandas.Series.map](https://pandas.pydata.org/docs/reference/api/pandas.Series.map.html) | If ‘ignore’, propagate NaN values, without passing them to the mapping correspondence. |
| 3 | False | [user_guide/basics](https://pandas.pydata.org/docs/user_guide/basics.html#function-application) | Passage discusses Series.map with a function and linking series, but does not mention unmatched dictionary values or na_action. |
| 4 | False | [user_guide/gotchas](https://pandas.pydata.org/docs/user_guide/gotchas.html#mutating-with-user-defined-function-udf-methods) | Passage is a traceback from DataFrame.apply, unrelated to Series.map dictionary behavior or na_action. |
| 5 | False | [user_guide/basics](https://pandas.pydata.org/docs/user_guide/basics.html#function-application) | Passage discusses DataFrame.transform, not Series.map dictionary behavior or na_action. |

## Q15 — parameter

Does DataFrame.groupby include groups whose grouping keys are NA by default? How do I include them?

**Gold answer:** The default dropna=True excludes rows with NA group keys. Set dropna=False to include NA as a group key.

**Required points:** dropna=True excludes NA group keys by default; dropna=False includes them.

### fixed_size

No. `DataFrame.groupby` excludes grouping keys that are NA by default: the `dropna` parameter defaults to `True`, so any “NA group” is dropped [1][2][3][4]. Here “NA” includes `NA`, `NaN`, `NaT`, and `None` [3].

To include NA groups, set `dropna=False` [1][2][3][5]:

```python
df.groupby("key", dropna=False)
```

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly states default dropna=True excludes NA and dropna=False includes them. All claims are supported by cited passages.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [user_guide/groupby](https://pandas.pydata.org/docs/user_guide/groupby.html#splitting-an-object-into-groups) | By default NA values are excluded from group keys during the groupby operation. However, in case you want to include NA values in group keys, you could pass dropna=False to achieve it. |
| 2 | True | [user_guide/groupby](https://pandas.pydata.org/docs/user_guide/groupby.html#splitting-an-object-into-groups) | The default setting of dropna argument is True which means NA are not included in group keys. |
| 3 | True | [user_guide/groupby](https://pandas.pydata.org/docs/user_guide/groupby.html#other-useful-features) | any “NA group” will be dropped. You can include NA groups by specifying dropna=False. |
| 4 | True | [reference/api/pandas.DataFrame.groupby](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html) | df.groupby(by=["b"], dropna=False).sum() |
| 5 | True | [reference/api/pandas.DataFrame.groupby](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html) | We can also choose to include NA in group keys or not by setting dropna parameter, the default setting is True. |

### structure_aware

No. By default, `DataFrame.groupby` excludes groups whose grouping keys are NA; the default `dropna` setting is `True`, so NA values are not included in group keys [1][2]. This applies to any NA values, including NA, NaN, NaT, and None [3].

To include them, pass `dropna=False` [1][4][3][5]:

```python
df.groupby("key", dropna=False).sum()
```

This creates a separate NA/NaN group in the result [1][2][5].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly states default dropna=True excludes NA and dropna=False includes them. All claims are supported by cited passages.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [user_guide/groupby](https://pandas.pydata.org/docs/user_guide/groupby.html#splitting-an-object-into-groups) | By default NA values are excluded from group keys during the groupby operation. However, in case you want to include NA values in group keys, you could pass dropna=False to achieve it. |
| 2 | True | [user_guide/groupby](https://pandas.pydata.org/docs/user_guide/groupby.html#splitting-an-object-into-groups) | The default setting of dropna argument is True which means NA are not included in group keys. |
| 3 | True | [user_guide/groupby](https://pandas.pydata.org/docs/user_guide/groupby.html#other-useful-features) | any “NA group” will be dropped. You can include NA groups by specifying dropna=False. |
| 4 | True | [user_guide/groupby](https://pandas.pydata.org/docs/user_guide/groupby.html#other-useful-features) | If there are any NA values in the grouping key, by default these will be excluded. In other words, any “NA group” will be dropped. You can include NA groups by specifying dropna=False. |
| 5 | True | [reference/api/pandas.DataFrame.groupby](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html) | df.groupby(by=["b"], dropna=False).sum() |

## Q16 — parameter

Does read_csv(low_memory=True) return an iterator of chunks? Which option should I use to process 1000 rows at a time?

**Gold answer:** No. low_memory controls internal parsing; the entire file is still returned in one DataFrame. Use chunksize=1000 to return a TextFileReader for iteration.

**Required points:** low_memory does not itself produce an iterable of output chunks.; chunksize=1000 yields an iterable TextFileReader of row chunks.

### fixed_size

No. `read_csv(low_memory=True)` does **not** return an iterator of chunks. With `low_memory=True`, pandas internally processes the file in chunks to reduce memory, but the entire file is still read into a single `DataFrame` [1].

To process 1000 rows at a time, use `chunksize=1000`. This returns an iterable `TextFileReader` object [2][3][1]:

```python
reader = pd.read_csv("file.csv", chunksize=1000)
for chunk in reader:
    # process each 1000-row chunk
    ...
```

Alternatively, use `iterator=True` and call `get_chunk(1000)` [3][1]:

```python
reader = pd.read_csv("file.csv", iterator=True)
chunk = reader.get_chunk(1000)
```

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Both required points are correctly addressed and supported by cited passages. The answer accurately states low_memory does not return an iterator and chunksize=1000 returns an iterable TextFileReader. All material claims are citation-supported.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [user_guide/io](https://pandas.pydata.org/docs/user_guide/io.html#csv-text-files) | By specifying a chunksize to read_csv() as a context manager, the return value will be an iterable object of type TextFileReader: |
| 2 | True | [user_guide/io](https://pandas.pydata.org/docs/user_guide/io.html#csv-text-files) | Specifying iterator=True will also return the TextFileReader object: |
| 3 | True | [user_guide/io](https://pandas.pydata.org/docs/user_guide/io.html#csv-text-files) | low_memoryboolean, default True Internally process the file in chunks, resulting in lower memory use while parsing, but possibly mixed type inference. To ensure no mixed types either set False, or specify the type with the dtype parameter. Note that the entire file is read into a single DataFrame regardless, use the chunksize or iterator parameter to return the data in chunks. |
| 4 | False | [user_guide/io](https://pandas.pydata.org/docs/user_guide/io.html#hdf5-pytables) | Passage discusses read_hdf and HDF5 chunking, not read_csv low_memory or chunksize. |
| 5 | False | [reference/api/pandas.read_csv](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html) | A signature listing low_memory=True, iterator=False and chunksize=None plus a general introduction does not establish the output behavior of the options; substantive explanatory evidence is required. |

### structure_aware

No. `low_memory=True` is the default value and does not by itself make `read_csv` return an iterator of chunks; the signature shows `low_memory=True` with `iterator=False` and `chunksize=None` [1]. To process 1000 rows at a time, use `chunksize=1000`. Passing `chunksize` makes `read_csv` return an iterable `TextFileReader`, which can be used as a context manager and iterated in chunks [2][3]. Alternatively, `iterator=True` also returns a `TextFileReader`, whose `get_chunk(n)` method can retrieve chunks [2].

```python
with pd.read_csv("file.csv", chunksize=1000) as reader:
    for chunk in reader:
        ...
```

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Both required points are correctly addressed and supported by cited passages. The answer accurately states low_memory does not return an iterator and chunksize=1000 returns an iterable TextFileReader. All material claims are citation-supported.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [user_guide/io](https://pandas.pydata.org/docs/user_guide/io.html#csv-text-files) | By specifying a chunksize to read_csv() as a context manager, the return value will be an iterable object of type TextFileReader: |
| 2 | True | [user_guide/cookbook](https://pandas.pydata.org/docs/user_guide/cookbook.html#data-in-out) | pd.concat(  .....: (chunk.query("col_1 >= 1000") for chunk in pd.read_csv(StringIO(data), chunksize=2)),  .....: ignore_index=True,  .....: ) |
| 3 | True | [user_guide/io](https://pandas.pydata.org/docs/user_guide/io.html#csv-text-files) | By specifying a chunksize to read_csv() as a context manager, the return value will be an iterable object of type TextFileReader: |
| 4 | False | [user_guide/io](https://pandas.pydata.org/docs/user_guide/io.html#hdf5-pytables) | Passage discusses read_hdf and HDF5 chunking, not read_csv low_memory or chunksize. |
| 5 | False | [reference/api/pandas.read_csv](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html) | The identical API-signature passage is not substantive evidence of low_memory/chunksize return behavior; apply the same relevance criterion to both strategies. |

## Q17 — comparison

Why can DataFrame.pivot fail on repeated index/column combinations, and when should I use pivot_table instead?

**Gold answer:** pivot does not aggregate and raises ValueError for duplicate index/column pairs. pivot_table aggregates repeated pairs using aggfunc (mean by default; select a suitable explicit function such as sum).

**Required points:** pivot requires unique index/column pairs and raises ValueError for duplicates.; pivot_table aggregates repeated combinations using aggfunc.

### fixed_size

`DataFrame.pivot` uses unique values from the specified `index`/`columns` to form the result axes and does **not** support data aggregation [1]. Therefore, if the data contains repeated or duplicate `index`/`columns` combinations, `pivot()` raises a `ValueError`: “A ValueError is raised if there are any duplicates” [2], specifically “When there are any index, columns combinations with multiple values” [1]. The reshaping docs state that `pivot()` can only handle unique rows specified by `index` and `columns` [3].

Use `pivot_table()` instead when the data contains duplicates or when aggregation is needed [3][1]. `DataFrame.pivot_table` is a “Generalization of pivot that can handle duplicate values for one index/column pair” [1], and it performs pivoting with aggregation; its default `aggfunc` is `'mean'` [4].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly states pivot raises ValueError for duplicates and pivot_table handles duplicates with aggregation, including default aggfunc mean. Both required points are supported by cited passages.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [user_guide/reshaping](https://pandas.pydata.org/docs/user_guide/reshaping.html#pivot-and-pivot-table) | pivot() can only handle unique rows specified by index and columns. If your data contains duplicates, use pivot_table(). |
| 2 | True | [reference/api/pandas.DataFrame.pivot](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.pivot.html) | A ValueError is raised if there are any duplicates. |
| 3 | True | [reference/api/pandas.DataFrame.pivot](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.pivot.html) | When there are any index, columns combinations with multiple values. DataFrame.pivot_table when you need to aggregate. |
| 4 | False | [user_guide/reshaping](https://pandas.pydata.org/docs/user_guide/reshaping.html#pivot-and-pivot-table) | Contains pivot_table examples but no explicit statement about aggregation or handling duplicates. |
| 5 | True | [reference/api/pandas.DataFrame.pivot_table](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.pivot_table.html) | aggfuncfunction, list of functions, dict, default “mean” |

### structure_aware

`DataFrame.pivot` raises a `ValueError` when there are any `index`/`columns` combinations with multiple values because it does not support data aggregation [1][2]. For example, duplicate rows for the same `index` and `columns` arguments lead to `ValueError: Index contains duplicate entries, cannot reshape` [1].

Use `pivot_table` instead when your data contains duplicates [3]. `pivot_table` is a generalization of `pivot` that can handle duplicate values for one index/column pair and pivots with aggregation of numeric data [3][2].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly states pivot raises ValueError for duplicates and pivot_table handles duplicates with aggregation. Both required points are supported by cited passages.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [reference/api/pandas.DataFrame.pivot](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.pivot.html) | A ValueError is raised if there are any duplicates. |
| 2 | True | [user_guide/reshaping](https://pandas.pydata.org/docs/user_guide/reshaping.html#pivot-and-pivot-table) | pivot() can only handle unique rows specified by index and columns. If your data contains duplicates, use pivot_table(). |
| 3 | False | [user_guide/10min](https://pandas.pydata.org/docs/user_guide/10min.html#reshaping) | Contains pivot_table examples but no explicit statement about aggregation or handling duplicates. |
| 4 | False | [user_guide/10min](https://pandas.pydata.org/docs/user_guide/10min.html#reshaping) | Contains pivot_table examples but no explicit statement about aggregation or handling duplicates. |
| 5 | True | [reference/api/pandas.DataFrame.pivot](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.pivot.html) | When there are any index, columns combinations with multiple values. DataFrame.pivot_table when you need to aggregate. |

## Q18 — comparison

How do .loc and .iloc differ, and do their slice stop endpoints get included? Assume unique sorted labels and valid slice bounds.

**Gold answer:** .loc selects by label and includes both label endpoints. .iloc selects by integer position with Python-style slicing that excludes the stop position.

**Required points:** loc is label-based and includes both label slice endpoints.; iloc is integer-position based and excludes the slice stop.

### fixed_size

`.loc` is **label-based** selection. It is a strict inclusion-based protocol: labels must exist in the index, and integers are treated as labels, not positions [1]. With `.loc`, slice endpoints are **inclusive**: both the start and stop labels are included when present in the index [1]. Under your assumption of unique sorted labels and valid slice bounds, this means the stop endpoint is included [2][1]. For stepped `.loc` slices, start and stop remain inclusive label boundaries, while the step is applied positionally within that label range [2][3].

`.iloc` is **purely positional / integer-based** indexing. It follows Python and NumPy slicing semantics, is 0-based, and trying to use a non-integer, even a valid label, raises an `IndexError` [3]. With `.iloc`, the start bound is **included**, but the stop/upper bound is **excluded** [3].

The Cookbook summarizes the distinction as: positional-oriented slicing is Python-style and **exclusive of the end**, while label-oriented slicing is non-Python-style and **inclusive of the end** [4].

Correct: **False**; faithful: **True**; refused: **False**; first relevant rank: **1**.

The required label/position and slice-endpoint distinctions are correct. However, the answer also says a non-integer label raises IndexError. For pd.Series([1], index=['a']).iloc['a'], installed pandas 3.1.1 raises TypeError. The cited guide itself says IndexError, so the answer is source-faithful but fails strict whole-answer factual correctness. This is a source-versus-runtime discrepancy, not an unsupported model invention.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [user_guide/indexing](https://pandas.pydata.org/docs/user_guide/indexing.html#selection-by-label) | When using .loc with slices, if both the start and the stop labels are present in the index, then elements located between the two (including them) are returned |
| 2 | True | [user_guide/indexing](https://pandas.pydata.org/docs/user_guide/indexing.html#selection-by-label) | When using .loc with slices, if both the start and the stop labels are present in the index, then elements located between the two (including them) are returned |
| 3 | True | [user_guide/indexing](https://pandas.pydata.org/docs/user_guide/indexing.html#selection-by-label) | When slicing, both the start bound AND the stop bound are included, if present in the index. |
| 4 | True | [user_guide/cookbook](https://pandas.pydata.org/docs/user_guide/cookbook.html#selection) | Positional-oriented (Python slicing style : exclusive of end) |
| 5 | True | [user_guide/indexing](https://pandas.pydata.org/docs/user_guide/indexing.html#selection-by-label) | When slicing, the start bound is included, while the upper bound is excluded. |

### structure_aware

`.loc` is label-oriented; `.iloc` is positional [1]. For `.loc` label slices, both the start and stop labels are included when present in the index [2][3]. For `.iloc`, integer slices behave like Python/NumPy, so the stop position is excluded [1][3].

Example: `df.loc["bar":"kar"]` includes `"bar"`, `"boo"`, and `"kar"` [1]. `df.iloc[3:5, 0:2]` returns row positions 3 and 4 but not 5 [3].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly states .loc is label-based with inclusive endpoints and .iloc is positional with exclusive stop. Both required points are supported by cited passages. The example df.loc["bar":"kar"] is supported by rank 3 passage showing inclusive labels. The example df.iloc[3:5, 0:2] is supported by rank 5 passage showing Python-style slicing. No unsupported claims.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [user_guide/indexing](https://pandas.pydata.org/docs/user_guide/indexing.html#selection-by-label) | Note that contrary to usual Python slices, both the start and the stop are included, when present in the index! |
| 2 | True | [user_guide/indexing](https://pandas.pydata.org/docs/user_guide/indexing.html#selection-by-label) | s.loc[3:5] Out[75]: 3 b 2 c 5 d |
| 3 | True | [user_guide/cookbook](https://pandas.pydata.org/docs/user_guide/cookbook.html#selection) | Positional-oriented (Python slicing style : exclusive of end) |
| 4 | True | [user_guide/indexing](https://pandas.pydata.org/docs/user_guide/indexing.html#selection-by-label) | When using .loc with slices, if both the start and the stop labels are present in the index, then elements located between the two (including them) are returned |
| 5 | True | [user_guide/10min](https://pandas.pydata.org/docs/user_guide/10min.html#selection) | Integer slices act similar to NumPy/Python |

## Q19 — comparison

With no explicit join keys, what does DataFrame.join match on and what is its default join type? How does this differ from DataFrame.merge?

**Gold answer:** join defaults to index-on-index and how='left'. merge defaults to how='inner' and, without index flags or on, uses the intersection of column names as merge keys.

**Required points:** join defaults to index-on-index with a left join.; merge defaults to inner and common column names when no keys/index flags are supplied.

### fixed_size

With no explicit join keys (`on=None`), `DataFrame.join` joins on the DataFrame indices, performing an index-on-index join [1][2]. Its default join type is `'left'`, so it uses only the calling frame’s index keys [2][3].

`DataFrame.merge` differs: its default join type is `'inner'` [1][4]. When `on=None` and indexes are not being used as merge keys, `merge` defaults to the intersection of columns found in both DataFrames [4]. So with no explicit keys, `join` matches on indices and does a left join, whereas `merge` matches on common columns and does an inner join [1][4][2][3].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly states join defaults to index-on-index left join and merge defaults to inner with common columns. All claims are supported by cited passages.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [getting_started/comparison/comparison_with_sql](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_sql.html#join) | By default, join() will join the DataFrames on their indices. |
| 2 | True | [reference/api/pandas.DataFrame.merge](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html) | how{‘left’, ‘right’, ‘outer’, ‘inner’, ‘cross’, ‘left_anti’, ‘right_anti’}, default ‘inner’ Type of merge to be performed. |
| 3 | True | [reference/api/pandas.DataFrame.join](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.join.html) | onstr, list of str, or array-like, optional Column or index level name(s) in the caller to join on the index in other, otherwise joins index-on-index. |
| 4 | False | [user_guide/merging](https://pandas.pydata.org/docs/user_guide/merging.html#dataframe-join) | Passage contains examples but no substantive evidence for required points. |
| 5 | True | [reference/api/pandas.DataFrame.merge](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html) | If on is None and not merging on indexes then this defaults to the intersection of the columns in both DataFrames. |

### structure_aware

With no explicit join keys, `DataFrame.join` joins on the DataFrames’ indices. The `on` parameter documentation says it “otherwise joins index-on-index” [1]. The SQL comparison likewise states, “By default, `join()` will join the DataFrames on their indices” [2]. Its default join type is `how='left'` [1].

By contrast, `DataFrame.merge` with no explicit join keys defaults to `how='inner'` [3][4]. When `on` is `None` and it is not merging on indexes, `on` “defaults to the intersection of the columns in both DataFrames” [3][4]. So the main difference is that `join` defaults to an index-on-index left join, while `merge` defaults to a common-column inner join.

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly states join defaults to index-on-index left join and merge defaults to inner with common columns. All claims are supported by cited passages.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [getting_started/comparison/comparison_with_sql](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_sql.html#join) | By default, join() will join the DataFrames on their indices. |
| 2 | True | [reference/api/pandas.DataFrame.merge](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html) | how{‘left’, ‘right’, ‘outer’, ‘inner’, ‘cross’, ‘left_anti’, ‘right_anti’}, default ‘inner’ Type of merge to be performed. |
| 3 | True | [reference/api/pandas.DataFrame.join](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.join.html) | onstr, list of str, or array-like, optional Column or index level name(s) in the caller to join on the index in other, otherwise joins index-on-index. |
| 4 | True | [reference/api/pandas.DataFrame.merge](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html) | If on is None and not merging on indexes then this defaults to the intersection of the columns in both DataFrames. |
| 5 | False | [getting_started/comparison/comparison_with_stata](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_stata.html#merging) | Passage discusses Stata merge examples, not relevant to required points. |

## Q20 — comparison

For grouped data, how does aggregation differ from transform, and which should I use to add each group's mean back to every original row?

**Gold answer:** Aggregation reduces groups to summaries. transform preserves the original row index and broadcasts group summaries; use df.groupby('group')['value'].transform('mean') to align group means with original rows.

**Required points:** Aggregation reduces groups to summary results.; transform preserves the original index and broadcasts a group aggregation to its rows.

### fixed_size

For grouped data, aggregation returns a group-level summary, such as one row per group from `tips.groupby(["sex", "smoker"])[["total_bill", "tip"]].sum()` [1]. Transformation, by contrast, returns a result that can be aligned back to the original rows; unlike aggregations, the groupings used to split the original object are not included in the transformed result [2].

To add each group’s mean back to every original row, use `transform("mean")` rather than aggregation [3][4]. Passing a built-in aggregation method such as `"mean"` to `transform()` broadcasts that group value across the group’s rows [4].

```python
tips["group_mean"] = tips.groupby("smoker")["total_bill"].transform("mean")
```

The evidence shows the same mechanism used to subtract a group mean: `tips["adj_total_bill"] = tips["total_bill"] - gb.transform("mean")` [3][1].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly distinguishes aggregation (group-level summary) and transform (broadcasts group value to original rows), and recommends transform('mean') to add group mean back. Both required points are supported by cited passages.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [getting_started/comparison/comparison_with_sas](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_sas.html#groupby) | pandas provides a Transformation mechanism that allows these type of operations to be succinctly expressed in one operation. In [1]: gb = tips.groupby("smoker")["total_bill"] In [2]: tips["adj_total_bill"] = tips["total_bill"] - gb.transform("mean") |
| 2 | False | [user_guide/cookbook](https://pandas.pydata.org/docs/user_guide/cookbook.html#grouping) | Text discusses expanding, replacing values, sorting groups, and creating multiple aggregated columns; no substantive evidence for aggregation vs transform or broadcasting group mean. |
| 3 | True | [getting_started/comparison/comparison_with_stata](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_stata.html#missing-data) | pandas provides a flexible groupby mechanism that allows similar aggregations. See the groupby documentation for more details and examples. In [65]: tips_summed = tips.groupby(["sex", "smoker"])[["total_bill", "tip"]].sum() |
| 4 | True | [user_guide/groupby](https://pandas.pydata.org/docs/user_guide/groupby.html#transformation) | Unlike aggregations, the groupings that are used to split the original object are not included in the result. Note Since transformations do not include the groupings that are used to split the result, the arguments as_index and sort in DataFrame.groupby() and Series.groupby() have no effect. A common use of a transformation is to add the result back into the original DataFrame. |
| 5 | True | [user_guide/groupby](https://pandas.pydata.org/docs/user_guide/groupby.html#transformation) | In addition, passing any built-in aggregation method as a string to transform() (see the next section) will broadcast the result across the group, producing a transformed result. |

### structure_aware

In grouped data, aggregation reduces each group to a single summary row/value, such as `sum` by group [1][2]. Transformation returns a result indexed the same as the object being grouped, so the computed group value is broadcast back to the original rows [3][2]. Transform does not include the grouping keys in the result, and a common use is adding the result back into the original DataFrame [3]. When you pass a built-in aggregation method to `transform()`, the aggregate is broadcast across each group [4].

To add each group’s mean back to every original row, use `transform`, not aggregation [1][3][4]. For example, assuming a numeric column such as `total_bill`:

```python
gb = tips.groupby("smoker")["total_bill"]

# Attach each group's mean to every original row
tips["group_mean"] = gb.transform("mean")

# Or use it in arithmetic with the original values
tips["total_bill_plus_group_mean"] = tips["total_bill"] + gb.transform("mean")
```

This follows the same transform pattern shown with `gb.transform("mean")` in the grouped-data example [1].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly distinguishes aggregation and transform, and recommends transform('mean') to add group mean back. Both required points are supported by cited passages.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [getting_started/comparison/comparison_with_stata](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_stata.html#groupby) | pandas provides a Transformation mechanism that allows these type of operations to be succinctly expressed in one operation. In [67]: gb = tips.groupby("smoker")["total_bill"] In [68]: tips["adj_total_bill"] = tips["total_bill"] - gb.transform("mean") |
| 2 | True | [user_guide/groupby](https://pandas.pydata.org/docs/user_guide/groupby.html#transformation) | A transformation is a GroupBy operation whose result is indexed the same as the one being grouped. Common examples include cumsum() and diff(). |
| 3 | True | [getting_started/comparison/comparison_with_sas](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_sas.html#groupby) | pandas provides a flexible groupby mechanism that allows similar aggregations. See the groupby documentation for more details and examples. In [1]: tips_summed = tips.groupby(["sex", "smoker"])[["total_bill", "tip"]].sum() |
| 4 | True | [user_guide/user_defined_functions](https://pandas.pydata.org/docs/user_guide/user_defined_functions.html#methods-that-support-user-defined-functions) | The transform method is similar to an aggregation, with the difference that the result is broadcasted to the original data. |
| 5 | True | [user_guide/groupby](https://pandas.pydata.org/docs/user_guide/groupby.html#transformation) | In addition, passing any built-in aggregation method as a string to transform() (see the next section) will broadcast the result across the group, producing a transformed result. |

## Q21 — comparison

In pd.concat, how do ignore_index=True and keys=['left','right'] differ when combining two DataFrames along rows?

**Gold answer:** ignore_index=True discards the concatenation-axis index labels and creates 0..n-1. keys adds outer levels to a hierarchical index that identify the inputs; it is not simple index renumbering.

**Required points:** ignore_index=True renumbers the concatenation axis from 0 to n-1.; keys constructs an outer level of a hierarchical index.

### fixed_size

When concatenating two DataFrames along rows (`axis=0`):

- `ignore_index=True` does not use the existing index values along the concatenation axis. The resulting row index is labeled `0, …, n - 1`, so overlapping original index labels are not preserved [1]. In a row-wise `concat`, this resets the row index [2][1].

- `keys=['left', 'right']` adds another axis level to the resulting row index, creating a `MultiIndex`. The keys become the outermost level, and each DataFrame’s original row index values remain as the inner level [2][1]. This associates each row with its source DataFrame, for example allowing `result.loc['left']` [2].

So `ignore_index=True` replaces the row index with a fresh integer index, while `keys=['left','right']` preserves the original row labels under an added hierarchical key level [2][1].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Both required points are correctly explained and supported by cited passages. No material factual errors.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [user_guide/merging](https://pandas.pydata.org/docs/user_guide/merging.html#concat) | The keys argument adds another axis level to the resulting index or column (creating a MultiIndex) associate specific keys with each original DataFrame. |
| 2 | True | [reference/api/pandas.concat](https://pandas.pydata.org/docs/reference/api/pandas.concat.html) | ignore_indexbool, default False If True, do not use the index values along the concatenation axis. The resulting axis will be labeled 0, …, n - 1. |
| 3 | True | [reference/api/pandas.concat](https://pandas.pydata.org/docs/reference/api/pandas.concat.html) | Clear the existing index and reset it in the result by setting the ignore_index option to True. >>> pd.concat([s1, s2], ignore_index=True) 0 a 1 b 2 c 3 d |
| 4 | True | [user_guide/merging](https://pandas.pydata.org/docs/user_guide/merging.html#concat) | For DataFrame objects which don’t have a meaningful index, the ignore_index ignores overlapping indexes. |
| 5 | False | [user_guide/merging](https://pandas.pydata.org/docs/user_guide/merging.html#concat) | Passage discusses general concatenation and index preservation but does not contain substantive evidence for either required point. |

### structure_aware

When combining DataFrames along rows (`axis=0`), `ignore_index=True` and `keys=['left','right']` affect the resulting row index differently.

- `ignore_index=True` **resets** the row index. The original index values from the two DataFrames are not used, and the resulting row axis is labeled `0, …, n - 1` as a single flat integer index [1]. It also drops name references [2].

- `keys=['left','right']` **adds a hierarchical level** instead of resetting. It creates a `MultiIndex` with the passed keys as the outermost level [2][1]. The inner level still contains the original row index values from each input [2][3]. This can be useful when the original row labels are the same or overlapping between the inputs [1].

For example, assuming two DataFrames with their own row indexes:

```python
# Flat integer index
pd.concat([df1, df2], ignore_index=True)

# MultiIndex with outer keys 'left' and 'right'
pd.concat([df1, df2], keys=['left', 'right'])
```

The `keys` approach allows selecting each original DataFrame’s rows using the key, such as `.loc['left']` [2].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Both required points are correctly explained and supported by cited passages. No material factual errors.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [user_guide/merging](https://pandas.pydata.org/docs/user_guide/merging.html#concat) | The keys argument adds another axis level to the resulting index or column (creating a MultiIndex) associate specific keys with each original DataFrame. |
| 2 | True | [reference/api/pandas.concat](https://pandas.pydata.org/docs/reference/api/pandas.concat.html) | ignore_indexbool, default False If True, do not use the index values along the concatenation axis. The resulting axis will be labeled 0, …, n - 1. |
| 3 | True | [reference/api/pandas.concat](https://pandas.pydata.org/docs/reference/api/pandas.concat.html) | Clear the existing index and reset it in the result by setting the ignore_index option to True. >>> pd.concat([s1, s2], ignore_index=True) 0 a 1 b 2 c 3 d |
| 4 | True | [user_guide/merging](https://pandas.pydata.org/docs/user_guide/merging.html#concat) | The MultiIndex created has levels that are constructed from the passed keys and the index of the DataFrame pieces: |
| 5 | False | [user_guide/10min](https://pandas.pydata.org/docs/user_guide/10min.html#merge) | Passage discusses general concatenation but does not contain substantive evidence for either required point. |

## Q22 — comparison

When working with a DatetimeIndex, when should I use tz_localize and when should I use tz_convert?

**Gold answer:** Use tz_localize to attach a time zone to timezone-naive timestamps. Use tz_convert to convert already timezone-aware timestamps into another time zone, preserving their underlying instants.

**Required points:** tz_localize assigns a timezone to naive timestamps.; tz_convert converts timezone-aware timestamps between zones.

### fixed_size

Use `tz_localize` when the DatetimeIndex is tz-naive and you need to attach a timezone to the existing datetime values without changing the local/clock representation [1][2].

Use `tz_convert` when the DatetimeIndex is already tz-aware and you need to change it to another timezone [3]. For example, this chain first attaches UTC, then converts to US/Eastern [2]:

```python
s.dt.tz_localize("UTC").dt.tz_convert("US/Eastern")
```

For removing timezone information from an aware DatetimeIndex [4]:

- `tz_localize(None)` removes the timezone and keeps the local time representation.
- `tz_convert(None)` converts to UTC first, then removes the timezone.

```python
didx.tz_localize(None)  # local wall time as naive
didx.tz_convert(None)   # UTC time as naive
```

If localizing a naive index across DST transitions, `tz_localize` may need the `ambiguous` or `nonexistent` arguments to handle ambiguous or nonexistent times [5][1].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly distinguishes tz_localize for naive and tz_convert for aware, with accurate optional details. All claims are supported by cited passages.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [user_guide/basics](https://pandas.pydata.org/docs/user_guide/basics.html#dt-accessor) | s.dt.tz_localize("UTC").dt.tz_convert("US/Eastern") |
| 2 | True | [user_guide/timeseries](https://pandas.pydata.org/docs/user_guide/timeseries.html#time-zone-handling) | dti.tz_localize("Europe/Warsaw", nonexistent="shift_forward") |
| 3 | True | [user_guide/timeseries](https://pandas.pydata.org/docs/user_guide/timeseries.html#time-zone-handling) | Localize tz-naive Datetime Array/Index to tz-aware Datetime Array/Index. |
| 4 | True | [user_guide/10min](https://pandas.pydata.org/docs/user_guide/10min.html#time-series) | Series.tz_convert() converts a timezone aware time series to another time zone: |
| 5 | True | [user_guide/timeseries](https://pandas.pydata.org/docs/user_guide/timeseries.html#time-zone-handling) | To remove time zone information, use tz_localize(None) or tz_convert(None). tz_localize(None) will remove the time zone yielding the local time representation. tz_convert(None) will remove the time zone after converting to UTC time. |

### structure_aware

- Use `tz_localize` when the `DatetimeIndex` is **timezone-naive** and you want to attach a timezone, turning it into a timezone-aware index. The method “Localize[s] tz-naive Datetime Array/Index to tz-aware Datetime Array/Index” [1]. For example, `rng_hourly.tz_localize('US/Eastern')` interprets the naive values as US/Eastern times [2].

- Use `tz_convert` when the `DatetimeIndex` is **already timezone-aware** and you want to change it to another timezone, converting the actual timestamps [3][4]. The typical pattern is to localize naive data first, then convert: `s_naive.dt.tz_localize("UTC").dt.tz_convert("US/Eastern")` [4].

- With `tz_localize`, be aware of DST-related ambiguous and nonexistent times; you may need to specify `ambiguous` or `nonexistent` to avoid errors [1][2][5][4].

- As a special case, on an already aware index, `tz_localize(None)` removes the timezone while keeping the local wall-clock values, whereas `tz_convert(None)` converts to UTC first, then removes the timezone [3].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer correctly distinguishes tz_localize for naive and tz_convert for aware, with accurate optional details. All claims are supported by cited passages.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [user_guide/timeseries](https://pandas.pydata.org/docs/user_guide/timeseries.html#time-zone-handling) | Localize tz-naive Datetime Array/Index to tz-aware Datetime Array/Index. |
| 2 | True | [user_guide/timeseries](https://pandas.pydata.org/docs/user_guide/timeseries.html#time-zone-handling) | rng_hourly.tz_localize('US/Eastern') |
| 3 | True | [user_guide/timeseries](https://pandas.pydata.org/docs/user_guide/timeseries.html#time-zone-handling) | didx.tz_localize(None) Out[504]: DatetimeIndex(['2014-08-01 09:00:00', '2014-08-01 10:00:00',  '2014-08-01 11:00:00'],  dtype='datetime64[us]', freq=None)  In [505]: didx.tz_convert(None) Out[505]: DatetimeIndex(['2014-08-01 13:00:00', '2014-08-01 14:00:00',  '2014-08-01 15:00:00'], |
| 4 | True | [user_guide/timeseries](https://pandas.pydata.org/docs/user_guide/timeseries.html#time-zone-handling) | rng_hourly.tz_localize("US/Eastern", ambiguous="infer") |
| 5 | True | [user_guide/timeseries](https://pandas.pydata.org/docs/user_guide/timeseries.html#time-zone-handling) | s_naive.dt.tz_localize("UTC").dt.tz_convert("US/Eastern") |

## Q23 — comparison

How does a rolling window differ from an expanding window when computing statistics over a Series?

**Gold answer:** A rolling window moves over a fixed-size or variable-size subset. An expanding window accumulates observations from the start up to the current position.

**Required points:** Rolling uses a sliding window.; Expanding uses an accumulating window.

### fixed_size

A rolling window is a “generic fixed or variable sliding window over the values,” while an expanding window is an “accumulating window over the values” [1]. For rolling calculations, “the windows are formed by looking back the length of the window from the current observation”; for example, `pd.Series(range(5)).rolling(window=2).sum()` produces `NaN`, then `1.0`, `3.0`, `5.0`, `7.0` because it sums the current and previous value once two observations are available [1]. In contrast, an expanding window “yields the value of an aggregation statistic with all the data available up to that point in time” [2]. So a rolling window is limited to the specified lookback window, whereas an expanding window accumulates from the start through the current point [1][2].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Both required points are explicitly stated and supported by cited passages. The optional rolling example is also supported by passage 1.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [user_guide/window](https://pandas.pydata.org/docs/user_guide/window.html#windowing-operations) | Rolling window: Generic fixed or variable sliding window over the values. |
| 2 | True | [user_guide/window](https://pandas.pydata.org/docs/user_guide/window.html#overview) | Generic rolling windows support specifying windows as a fixed number of observations or variable number of observations based on an offset. |
| 3 | False | [user_guide/window](https://pandas.pydata.org/docs/user_guide/window.html#rolling-window) | Passage discusses custom window rolling with BaseIndexer, not the core rolling vs expanding distinction. |
| 4 | True | [user_guide/window](https://pandas.pydata.org/docs/user_guide/window.html#rolling-window) | # Window with 2 observations In [25]: s.rolling(window=2).sum() |
| 5 | True | [user_guide/window](https://pandas.pydata.org/docs/user_guide/window.html#rolling-window) | An expanding window yields the value of an aggregation statistic with all the data available up to that point in time. |

### structure_aware

A rolling window is a sliding window over a fixed or variable number of observations, or over a time-based offset [1][2]. An expanding window is an accumulating window that uses all data available up to the current point [3][2].

Expanding windows are a special case of rolling windows. These two calls are equivalent [3]:

```python
df = pd.DataFrame(range(5))

df.rolling(window=len(df), min_periods=1).mean()
df.expanding(min_periods=1).mean()
```

So the key difference is window behavior: an expanding window grows from the start through the current point, while a rolling window uses a bounded sliding lookback defined by a fixed size or an offset [3][1][2]. Rolling supports time-based windows; expanding does not [2].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Both required points are explicitly stated and supported by cited passages. The optional equivalence example is supported by passage 1.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [user_guide/window](https://pandas.pydata.org/docs/user_guide/window.html#expanding-window) | An expanding window yields the value of an aggregation statistic with all the data available up to that point in time. |
| 2 | True | [user_guide/window](https://pandas.pydata.org/docs/user_guide/window.html#rolling-window) | Generic rolling windows support specifying windows as a fixed number of observations or variable number of observations based on an offset. |
| 3 | True | [user_guide/window](https://pandas.pydata.org/docs/user_guide/window.html#overview) | Rolling window: Generic fixed or variable sliding window over the values. |
| 4 | False | [user_guide/window](https://pandas.pydata.org/docs/user_guide/window.html#rolling-window) | Passage discusses rolling centering and endpoints, not the core rolling vs expanding distinction. |
| 5 | False | [user_guide/window](https://pandas.pydata.org/docs/user_guide/window.html#rolling-window) | Passage discusses custom window rolling with BaseIndexer, not the core rolling vs expanding distinction. |

## Q24 — comparison

For Series.apply with a callable, what changes between by_row='compat' and by_row=False?

**Gold answer:** With by_row='compat', a callable receives individual elements, like Series.map. With by_row=False it receives the whole Series at once.

**Required points:** With compat a callable is applied to individual elements.; With by_row=False the callable receives the entire Series.

### fixed_size

For a callable, `by_row='compat'` passes each element of the Series to `func`, like `Series.map`, while `by_row=False` passes the whole Series to `func` at once [1].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer accurately states both required points and is fully supported by cited passage [1].

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [reference/api/pandas.Series.apply](https://pandas.pydata.org/docs/reference/api/pandas.Series.apply.html) | If "compat" and func is a callable, func will be passed each element of the Series, like Series.map. If func is a list or dict of callables, will first try to translate each func into pandas methods. If that doesn’t work, will try call to apply again with by_row="compat" and if that fails, will call apply again with by_row=False (backward compatible). If False, the func will be passed the whole Series at once. |
| 2 | False | [user_guide/user_defined_functions](https://pandas.pydata.org/docs/user_guide/user_defined_functions.html#methods-that-support-user-defined-functions) | Discusses DataFrame.apply with axis=1, not Series.apply by_row. |
| 3 | False | [user_guide/basics](https://pandas.pydata.org/docs/user_guide/basics.html#function-application) | Discusses DataFrame.apply vectorized alternatives, not Series.apply by_row. |
| 4 | False | [user_guide/user_defined_functions](https://pandas.pydata.org/docs/user_guide/user_defined_functions.html#methods-that-support-user-defined-functions) | Discusses map and DataFrame.apply, not Series.apply by_row. |
| 5 | False | [user_guide/basics](https://pandas.pydata.org/docs/user_guide/basics.html#function-application) | Discusses DataFrame.apply row/column-wise, not Series.apply by_row. |

### structure_aware

For a callable `func`, the difference is:

- With `by_row='compat'`, `func` is passed each element of the `Series`, like `Series.map` [1].
- With `by_row=False`, `func` is passed the whole `Series` at once [1].

Correct: **True**; faithful: **True**; refused: **False**; first relevant rank: **1**.

Answer accurately states both required points and is fully supported by cited passage [1].

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | True | [reference/api/pandas.Series.apply](https://pandas.pydata.org/docs/reference/api/pandas.Series.apply.html) | If "compat" and func is a callable, func will be passed each element of the Series, like Series.map. If func is a list or dict of callables, will first try to translate each func into pandas methods. If that doesn’t work, will try call to apply again with by_row="compat" and if that fails, will call apply again with by_row=False (backward compatible). If False, the func will be passed the whole Series at once. |
| 2 | False | [user_guide/basics](https://pandas.pydata.org/docs/user_guide/basics.html#function-application) | Discusses DataFrame.apply, not Series.apply by_row behavior. |
| 3 | False | [user_guide/basics](https://pandas.pydata.org/docs/user_guide/basics.html#function-application) | Discusses DataFrame.apply return types and examples, not Series.apply by_row. |
| 4 | False | [user_guide/user_defined_functions](https://pandas.pydata.org/docs/user_guide/user_defined_functions.html#methods-that-support-user-defined-functions) | Discusses pipe and DataFrame.apply, not Series.apply by_row. |
| 5 | False | [user_guide/basics](https://pandas.pydata.org/docs/user_guide/basics.html#function-application) | Discusses DataFrame.apply vectorized alternatives, not Series.apply by_row. |

## Q25 — private_data

How many rows in my company's private customers.csv have a missing age? I have not uploaded or provided that file.

**Gold answer:** INSUFFICIENT_EVIDENCE

**Required points:** Explicitly decline to give the unsupported answer.

### fixed_size

I couldn't find enough evidence in the pandas documentation to answer this.

Correct: **True**; faithful: **None**; refused: **True**; first relevant rank: **0**.

The question is unanswerable because the private file was not provided. System Y explicitly declines to give an unsupported answer, satisfying the required point. Retrieval passages are all irrelevant as expected.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | False | [getting_started/intro_tutorials/03_subset_data](https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html#how-do-i-filter-specific-rows-from-a-dataframe) | Passage discusses filtering Titanic data for known ages, not the private customers.csv missing age count. |
| 2 | False | [reference/api/pandas.read_csv](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html) | Passage describes read_csv parameters, not the private file's missing age count. |
| 3 | False | [user_guide/10min](https://pandas.pydata.org/docs/user_guide/10min.html#missing-data) | Passage shows missing data operations on a sample DataFrame, not the private file's missing age count. |
| 4 | False | [getting_started/comparison/comparison_with_spss](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_spss.html#copies-vs-in-place-operations) | Passage compares SPSS and pandas operations, unrelated to the private data question. |
| 5 | False | [user_guide/io](https://pandas.pydata.org/docs/user_guide/io.html#csv-text-files) | Passage shows parser error handling, unrelated to the private data question. |

### structure_aware

I couldn't find enough evidence in the pandas documentation to answer this.

Correct: **True**; faithful: **None**; refused: **True**; first relevant rank: **0**.

The question is unanswerable because the private file was not provided. System X explicitly declines to give an unsupported answer, satisfying the required point. Retrieval passages are all irrelevant as expected.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | False | [getting_started/intro_tutorials/03_subset_data](https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html#how-do-i-filter-specific-rows-from-a-dataframe) | Passage discusses filtering Titanic data for known ages, not the private customers.csv missing age count. |
| 2 | False | [reference/api/pandas.read_csv](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html) | Passage describes read_csv parameters, not the private file's missing age count. |
| 3 | False | [user_guide/io](https://pandas.pydata.org/docs/user_guide/io.html#csv-text-files) | Passage shows parser error handling, unrelated to the private data question. |
| 4 | False | [user_guide/index](https://pandas.pydata.org/docs/user_guide/index.html#guides) | Passage is a table of contents, no substantive evidence for the required answer. |
| 5 | False | [user_guide/io](https://pandas.pydata.org/docs/user_guide/io.html#csv-text-files) | Passage shows usecols error handling, unrelated to the private data question. |

## Q26 — private_data

What was the exact total revenue in our team's unpublished 2026 sales DataFrame? No data or values have been supplied.

**Gold answer:** INSUFFICIENT_EVIDENCE

**Required points:** Explicitly decline to give the unsupported answer.

### fixed_size

I couldn't find enough evidence in the pandas documentation to answer this.

Correct: **True**; faithful: **None**; refused: **True**; first relevant rank: **0**.

The question is unanswerable because the private revenue values are absent. The answer explicitly declines to provide the unsupported answer, satisfying the required point. Retrieval passages are all irrelevant as expected.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | False | [user_guide/style](https://pandas.pydata.org/docs/user_guide/style.html#Other-Fun-and-Useful-Stuff) | Contains only numeric data; no evidence about the requested private revenue DataFrame. |
| 2 | False | [user_guide/dsintro](https://pandas.pydata.org/docs/user_guide/dsintro.html#dataframe) | Contains baseball DataFrame info and to_string output; no evidence about the requested private revenue DataFrame. |
| 3 | False | [user_guide/dsintro](https://pandas.pydata.org/docs/user_guide/dsintro.html#dataframe) | Contains baseball DataFrame loading and info; no evidence about the requested private revenue DataFrame. |
| 4 | False | [user_guide/style](https://pandas.pydata.org/docs/user_guide/style.html#Other-Fun-and-Useful-Stuff) | Contains numeric data; no evidence about the requested private revenue DataFrame. |
| 5 | False | [user_guide/style](https://pandas.pydata.org/docs/user_guide/style.html#Other-Fun-and-Useful-Stuff) | Contains numeric data; no evidence about the requested private revenue DataFrame. |

### structure_aware

I couldn't find enough evidence in the pandas documentation to answer this.

Correct: **True**; faithful: **None**; refused: **True**; first relevant rank: **0**.

The question is unanswerable because the private revenue values are absent. The answer explicitly declines to provide the unsupported answer, satisfying the required point. Retrieval passages are all irrelevant as expected.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | False | [user_guide/indexing](https://pandas.pydata.org/docs/user_guide/indexing.html#fast-scalar-value-getting-and-setting) | Contains only numeric data and NaN values; no evidence about the requested private revenue DataFrame. |
| 2 | False | [user_guide/style](https://pandas.pydata.org/docs/user_guide/style.html#Styler-Object-and-HTML) | Contains model evaluation metrics and styling examples; no evidence about the requested private revenue DataFrame. |
| 3 | False | [getting_started/overview](https://pandas.pydata.org/docs/getting_started/overview.html#development-team) | Mentions Core Team members; no evidence about the requested private revenue DataFrame. |
| 4 | False | [getting_started/intro_tutorials/03_subset_data](https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html#how-do-i-select-a-subset-of-a-dataframe) | Only a question title about selecting a subset; no substantive evidence about the requested private revenue DataFrame. |
| 5 | False | [user_guide/io](https://pandas.pydata.org/docs/user_guide/io.html#json) | Contains JSON-like numeric data; no evidence about the requested private revenue DataFrame. |

## Q27 — unsupported_api

What are the documented parameters of the pandas function pd.teleport_to_mars, and how do I call it?

**Gold answer:** INSUFFICIENT_EVIDENCE

**Required points:** Explicitly decline to give the unsupported answer.

### fixed_size

I couldn't find enough evidence in the pandas documentation to answer this.

Correct: **True**; faithful: **None**; refused: **True**; first relevant rank: **0**.

The question is unanswerable because pd.teleport_to_mars is not documented. System X explicitly declines to answer, satisfying the required point. Retrieval passages are all irrelevant as expected.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | False | [reference/api/pandas.Series.apply](https://pandas.pydata.org/docs/reference/api/pandas.Series.apply.html) | Passage describes pandas.Series.apply, not pd.teleport_to_mars; no evidence for the unsupported API. |
| 2 | False | [reference/api/pandas.Series.apply](https://pandas.pydata.org/docs/reference/api/pandas.Series.apply.html) | Continuation of Series.apply examples; no evidence for pd.teleport_to_mars. |
| 3 | False | [user_guide/basics](https://pandas.pydata.org/docs/user_guide/basics.html#function-application) | Passage discusses DataFrame.pipe and method chaining; no evidence for pd.teleport_to_mars. |
| 4 | False | [user_guide/basics](https://pandas.pydata.org/docs/user_guide/basics.html#function-application) | Passage discusses elementwise functions and map; no evidence for pd.teleport_to_mars. |
| 5 | False | [user_guide/options](https://pandas.pydata.org/docs/user_guide/options.html#overview) | Passage discusses pandas options API; no evidence for pd.teleport_to_mars. |

### structure_aware

I couldn't find enough evidence in the pandas documentation to answer this.

Correct: **True**; faithful: **None**; refused: **True**; first relevant rank: **0**.

The question is unanswerable because pd.teleport_to_mars is not documented. System Y explicitly declines to answer, satisfying the required point. Retrieval passages are all irrelevant as expected.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | False | [getting_started/comparison/comparison_with_spreadsheets](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_spreadsheets.html#comparison-with-spreadsheets) | Passage is an introduction to spreadsheet comparisons; no evidence for pd.teleport_to_mars. |
| 2 | False | [getting_started/index](https://pandas.pydata.org/docs/getting_started/index.html#getting-started) | Passage mentions trying pandas online; no evidence for pd.teleport_to_mars. |
| 3 | False | [reference/api/pandas.Series.apply](https://pandas.pydata.org/docs/reference/api/pandas.Series.apply.html) | Passage describes pandas.Series.apply; no evidence for pd.teleport_to_mars. |
| 4 | False | [getting_started/tutorials](https://pandas.pydata.org/docs/getting_started/tutorials.html#video-tutorials) | Passage lists video tutorials; no evidence for pd.teleport_to_mars. |
| 5 | False | [reference/api/pandas.Series.apply](https://pandas.pydata.org/docs/reference/api/pandas.Series.apply.html) | Continuation of Series.apply examples; no evidence for pd.teleport_to_mars. |

## Q28 — unmeasured_performance

Exactly how many milliseconds will pd.read_csv take to read my 10 GB CSV on my own laptop? No hardware details, data, or benchmark are provided.

**Gold answer:** INSUFFICIENT_EVIDENCE

**Required points:** Explicitly decline to give the unsupported answer.

### fixed_size

I couldn't find enough evidence in the pandas documentation to answer this.

Correct: **True**; faithful: **None**; refused: **True**; first relevant rank: **0**.

The question is unanswerable because no hardware, data, or benchmark details are provided. The system explicitly declines to give an unsupported answer, satisfying the required point. Retrieval passages are all irrelevant as none contain evidence for the requested exact runtime.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | False | [user_guide/io](https://pandas.pydata.org/docs/user_guide/io.html#csv-text-files) | Passage shows source code traceback from read_csv but does not provide exact runtime for the user's unspecified 10 GB CSV. |
| 2 | False | [reference/api/pandas.read_csv](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html) | Passage is the read_csv API reference; it documents parameters but does not give exact runtime for an unmeasured workload. |
| 3 | False | [getting_started/comparison/comparison_with_sas](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_sas.html#other-considerations) | Passage discusses SAS interop and a specific benchmark for a 10M row CSV, not the user's unspecified 10 GB CSV. |
| 4 | False | [user_guide/io](https://pandas.pydata.org/docs/user_guide/io.html#performance-considerations) | Passage lists file sizes for various formats but does not provide runtime for reading a 10 GB CSV. |
| 5 | False | [user_guide/io](https://pandas.pydata.org/docs/user_guide/io.html#performance-considerations) | Passage shows timing benchmarks for various formats on a specific dataset, not the user's unspecified 10 GB CSV. |

### structure_aware

I couldn't find enough evidence in the pandas documentation to answer this.

Correct: **True**; faithful: **None**; refused: **True**; first relevant rank: **0**.

The question is unanswerable because no hardware, data, or benchmark details are provided. The system explicitly declines to give an unsupported answer, satisfying the required point. Retrieval passages are all irrelevant as none contain evidence for the requested exact runtime.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | False | [user_guide/cookbook](https://pandas.pydata.org/docs/user_guide/cookbook.html#data-in-out) | Passage discusses CSV usage examples and chunking but provides no evidence about exact runtime for a 10 GB CSV on unspecified hardware. |
| 2 | False | [getting_started/comparison/comparison_with_sas](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_sas.html#other-considerations) | Passage compares disk vs memory and shows a benchmark for a specific 10M row CSV, but does not answer the exact runtime for the user's unspecified 10 GB CSV. |
| 3 | False | [getting_started/comparison/comparison_with_spss](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_spss.html#data-input-output) | Passage shows how to read CSV with read_csv but contains no timing information relevant to the user's specific hardware and data. |
| 4 | False | [user_guide/io](https://pandas.pydata.org/docs/user_guide/io.html#performance-considerations) | Passage lists file sizes for various formats but does not provide runtime for reading a 10 GB CSV. |
| 5 | False | [reference/api/pandas.read_csv](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html) | Passage is the read_csv API reference; it documents parameters but does not give exact runtime for an unmeasured workload. |

## Q29 — live_information

What is the current live USD to CNY exchange rate right now?

**Gold answer:** INSUFFICIENT_EVIDENCE

**Required points:** Explicitly decline to give the unsupported answer.

### fixed_size

I couldn't find enough evidence in the pandas documentation to answer this.

Correct: **True**; faithful: **None**; refused: **True**; first relevant rank: **0**.

The question is unanswerable from the provided documentation. The system explicitly declines to give an unsupported answer, satisfying the required point. Retrieval passages are irrelevant as they contain no substantive evidence.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | False | [user_guide/style](https://pandas.pydata.org/docs/user_guide/style.html#Other-Fun-and-Useful-Stuff) | Passage contains only numeric data and no substantive evidence about live exchange rates or refusal. |
| 2 | False | [user_guide/style](https://pandas.pydata.org/docs/user_guide/style.html#Other-Fun-and-Useful-Stuff) | Passage contains only numeric data and no substantive evidence about live exchange rates or refusal. |
| 3 | False | [user_guide/style](https://pandas.pydata.org/docs/user_guide/style.html#Other-Fun-and-Useful-Stuff) | Passage contains only numeric data and no substantive evidence about live exchange rates or refusal. |
| 4 | False | [user_guide/style](https://pandas.pydata.org/docs/user_guide/style.html#Other-Fun-and-Useful-Stuff) | Passage contains only numeric data and no substantive evidence about live exchange rates or refusal. |
| 5 | False | [user_guide/style](https://pandas.pydata.org/docs/user_guide/style.html#Other-Fun-and-Useful-Stuff) | Passage contains only numeric data and no substantive evidence about live exchange rates or refusal. |

### structure_aware

I couldn't find enough evidence in the pandas documentation to answer this.

Correct: **True**; faithful: **None**; refused: **True**; first relevant rank: **0**.

The question is unanswerable from the provided documentation. The system explicitly declines to give an unsupported answer, satisfying the required point. Retrieval passages are irrelevant as they contain no substantive evidence.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | False | [user_guide/style](https://pandas.pydata.org/docs/user_guide/style.html#Other-Fun-and-Useful-Stuff) | Passage contains only numeric data and no substantive evidence about live exchange rates or refusal. |
| 2 | False | [user_guide/style](https://pandas.pydata.org/docs/user_guide/style.html#Other-Fun-and-Useful-Stuff) | Passage contains only numeric data and no substantive evidence about live exchange rates or refusal. |
| 3 | False | [user_guide/style](https://pandas.pydata.org/docs/user_guide/style.html#Other-Fun-and-Useful-Stuff) | Passage contains only numeric data and no substantive evidence about live exchange rates or refusal. |
| 4 | False | [user_guide/style](https://pandas.pydata.org/docs/user_guide/style.html#Other-Fun-and-Useful-Stuff) | Passage contains only numeric data and no substantive evidence about live exchange rates or refusal. |
| 5 | False | [user_guide/style](https://pandas.pydata.org/docs/user_guide/style.html#Other-Fun-and-Useful-Stuff) | Passage contains only numeric data and no substantive evidence about live exchange rates or refusal. |

## Q30 — private_policy

What is the official CS5481 team's private policy for deleting customer data after 2026-12-01? The policy has not been supplied.

**Gold answer:** INSUFFICIENT_EVIDENCE

**Required points:** Explicitly decline to give the unsupported answer.

### fixed_size

I couldn't find enough evidence in the pandas documentation to answer this.

Correct: **True**; faithful: **None**; refused: **True**; first relevant rank: **0**.

The question is unanswerable because the private team policy is not in the pandas corpus. System Y explicitly declines to give an unsupported answer, satisfying the required point. Retrieval passages are all irrelevant as expected.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | False | [user_guide/style](https://pandas.pydata.org/docs/user_guide/style.html#Other-Fun-and-Useful-Stuff) | Passage contains numerical data and no evidence about a private policy for deleting customer data. |
| 2 | False | [user_guide/style](https://pandas.pydata.org/docs/user_guide/style.html#Other-Fun-and-Useful-Stuff) | Passage contains numerical data and no evidence about a private policy for deleting customer data. |
| 3 | False | [user_guide/style](https://pandas.pydata.org/docs/user_guide/style.html#Other-Fun-and-Useful-Stuff) | Passage contains numerical data and no evidence about a private policy for deleting customer data. |
| 4 | False | [user_guide/style](https://pandas.pydata.org/docs/user_guide/style.html#Other-Fun-and-Useful-Stuff) | Passage contains numerical data and no evidence about a private policy for deleting customer data. |
| 5 | False | [user_guide/style](https://pandas.pydata.org/docs/user_guide/style.html#Other-Fun-and-Useful-Stuff) | Passage contains numerical data and no evidence about a private policy for deleting customer data. |

### structure_aware

I couldn't find enough evidence in the pandas documentation to answer this.

Correct: **True**; faithful: **None**; refused: **True**; first relevant rank: **0**.

The question is unanswerable because the private team policy is not in the pandas corpus. System X explicitly declines to give an unsupported answer, satisfying the required point. Retrieval passages are all irrelevant as expected.

| Rank | Relevant | Source | Evidence / reason |
|---|---|---|---|
| 1 | False | [getting_started/overview](https://pandas.pydata.org/docs/getting_started/overview.html#development-team) | Passage mentions Core Team members but provides no evidence about a private policy for deleting customer data. |
| 2 | False | [getting_started/overview](https://pandas.pydata.org/docs/getting_started/overview.html#institutional-partners) | Passage mentions institutional partners but no private policy for deleting customer data. |
| 3 | False | [getting_started/tutorials](https://pandas.pydata.org/docs/getting_started/tutorials.html#exercises-for-new-users) | Passage about practice exercises and resources, unrelated to the question. |
| 4 | False | [getting_started/tutorials](https://pandas.pydata.org/docs/getting_started/tutorials.html#video-tutorials) | Passage lists video tutorials and repos, no private policy information. |
| 5 | False | [getting_started/tutorials](https://pandas.pydata.org/docs/getting_started/tutorials.html#bamboo-weekly-by-reuven-lerner) | Passage about Bamboo Weekly mailing list, unrelated to the question. |
