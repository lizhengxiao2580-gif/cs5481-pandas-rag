# Frozen evaluation questions

## Q01 (basic)

How can I read only the name and age columns from a CSV file with pandas?

**Reference answer:** Use pd.read_csv(path, usecols=['name', 'age']). usecols selects a subset of columns.

- Select columns at read time with usecols=['name', 'age'].

- [reference/api/pandas.read_csv#page](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)

## Q02 (basic)

How do I write a DataFrame to CSV without writing the row index?

**Reference answer:** Use df.to_csv(path, index=False); index controls writing the row names, and defaults to True.

- Set index=False when calling to_csv.

- [reference/api/pandas.DataFrame.to_csv#page](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html)

## Q03 (basic)

How can I keep rows whose country column is either UK or JP?

**Reference answer:** Use df[df['country'].isin(['UK', 'JP'])]. isin returns a Boolean membership mask.

- Use isin with the list of allowed values and use its Boolean mask to filter rows.

- [reference/api/pandas.DataFrame.isin#page](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.isin.html)
- [user_guide/indexing#indexing-with-isin](https://pandas.pydata.org/docs/user_guide/indexing.html#indexing-with-isin)

## Q04 (basic)

How do I drop a row if either its name or age is missing, while ignoring missing values in other columns?

**Reference answer:** Use df.dropna(subset=['name', 'age'], how='any'). subset restricts considered columns; any drops rows with at least one missing value.

- Use subset=['name','age'] to restrict missing-value checks.
- Use how='any' to remove a row if either selected value is missing.

- [reference/api/pandas.DataFrame.dropna#page](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.dropna.html)
- [reference/api/pandas.DataFrame.dropna#page](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.dropna.html)

## Q05 (basic)

How can I fill missing values in column A with 0 and column B with 'unknown', leaving other columns alone?

**Reference answer:** Use df.fillna({'A': 0, 'B': 'unknown'}). A mapping supplies per-column replacement values; unspecified columns are not filled.

- Pass a per-column dictionary to fillna.
- Columns absent from the mapping remain unfilled.

- [reference/api/pandas.DataFrame.fillna#page](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.fillna.html)
- [reference/api/pandas.DataFrame.fillna#page](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.fillna.html)

## Q06 (basic)

How do I calculate mean sales separately for each combination of region and product?

**Reference answer:** Use df.groupby(['region', 'product'])['sales'].mean(). A list of grouping column names forms combination groups.

- Group by both columns using a list, select sales, and compute mean.

- [reference/api/pandas.DataFrame.groupby#page](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html)
- [user_guide/groupby#splitting-an-object-into-groups](https://pandas.pydata.org/docs/user_guide/groupby.html#splitting-an-object-into-groups)

## Q07 (basic)

How do I reshape a wide table into long format while keeping id as an identifier and unpivoting only Jan and Feb?

**Reference answer:** Use pd.melt(df, id_vars=['id'], value_vars=['Jan', 'Feb']). id_vars stay as identifiers; value_vars select measured columns to unpivot.

- Set id_vars=['id'] to preserve the identifier.
- Set value_vars=['Jan','Feb'] to select the unpivoted columns.

- [reference/api/pandas.melt#page](https://pandas.pydata.org/docs/reference/api/pandas.melt.html)
- [reference/api/pandas.melt#page](https://pandas.pydata.org/docs/reference/api/pandas.melt.html)

## Q08 (basic)

How can I convert only column age to int64 and column score to float64 in a DataFrame?

**Reference answer:** Use df.astype({'age': 'int64', 'score': 'float64'}). A dtype mapping specifies column-specific types; other columns remain unchanged.

- Pass a mapping of column names to dtypes to astype.

- [reference/api/pandas.DataFrame.astype#page](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.astype.html)

## Q09 (parameter)

With DataFrame.drop_duplicates, how can I remove every occurrence of duplicate ids rather than keeping one? Does this method compare index labels?

**Reference answer:** Use df.drop_duplicates(subset=['id'], keep=False). It removes all duplicate-id rows; index labels are ignored.

- subset=['id'] with keep=False removes all occurrences of duplicated ids.
- Index labels are ignored by drop_duplicates.

- [reference/api/pandas.DataFrame.drop_duplicates#page](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop_duplicates.html)
- [reference/api/pandas.DataFrame.drop_duplicates#page](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop_duplicates.html)

## Q10 (parameter)

How can Series.value_counts report proportions and include missing values as a counted category?

**Reference answer:** Use s.value_counts(normalize=True, dropna=False). normalize returns relative frequencies and dropna=False includes missing values.

- normalize=True returns relative frequencies.
- dropna=False includes NA values in the counts.

- [reference/api/pandas.Series.value_counts#page](https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html)
- [reference/api/pandas.Series.value_counts#page](https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html)

## Q11 (parameter)

When both merge key columns contain null values, can pandas match those rows together, and is this the same as typical SQL joins?

**Reference answer:** Yes, pandas matches rows whose merge keys are null on both sides. This differs from usual SQL join behavior.

- Null keys on both sides can match each other.
- This differs from usual SQL join behavior.

- [reference/api/pandas.DataFrame.merge#page](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html)
- [reference/api/pandas.DataFrame.merge#page](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html)

## Q12 (parameter)

If a nullable Boolean indexing mask contains pd.NA, are those rows selected? How can I retain those rows?

**Reference answer:** Mask NA entries are treated as False. Use mask.fillna(True) before indexing to retain those positions.

- NA entries in a Boolean mask are treated as False.
- Fill mask NA entries with True to keep those rows.

- [user_guide/boolean#indexing-with-na-values](https://pandas.pydata.org/docs/user_guide/boolean.html#indexing-with-na-values)
- [user_guide/boolean#indexing-with-na-values](https://pandas.pydata.org/docs/user_guide/boolean.html#indexing-with-na-values)

## Q13 (parameter)

How do I construct a Series of integers with missing values without converting it to floating point? Is 'Int64' the same spelling as NumPy 'int64'?

**Reference answer:** Specify dtype='Int64', for example pd.Series([1, None], dtype='Int64'). The capital I distinguishes the nullable integer dtype from NumPy int64; missing values become pandas.NA.

- Explicitly use nullable Int64 with a capital I.
- Missing values are represented by pandas.NA.

- [user_guide/integer_na#construction](https://pandas.pydata.org/docs/user_guide/integer_na.html#construction)
- [user_guide/integer_na#construction](https://pandas.pydata.org/docs/user_guide/integer_na.html#construction)

## Q14 (parameter)

In Series.map with an ordinary dictionary, what happens to values that have no matching key? How do I avoid applying a function to existing missing values?

**Reference answer:** Unmatched values become NaN for an ordinary dict. Set na_action='ignore' to propagate existing missing values without calling the mapping function on them.

- Values absent from an ordinary dictionary become NaN.
- na_action='ignore' skips existing missing values.

- [reference/api/pandas.Series.map#page](https://pandas.pydata.org/docs/reference/api/pandas.Series.map.html)
- [reference/api/pandas.Series.map#page](https://pandas.pydata.org/docs/reference/api/pandas.Series.map.html)

## Q15 (parameter)

Does DataFrame.groupby include groups whose grouping keys are NA by default? How do I include them?

**Reference answer:** The default dropna=True excludes rows with NA group keys. Set dropna=False to include NA as a group key.

- dropna=True excludes NA group keys by default; dropna=False includes them.

- [reference/api/pandas.DataFrame.groupby#page](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html)

## Q16 (parameter)

Does read_csv(low_memory=True) return an iterator of chunks? Which option should I use to process 1000 rows at a time?

**Reference answer:** No. low_memory controls internal parsing; the entire file is still returned in one DataFrame. Use chunksize=1000 to return a TextFileReader for iteration.

- low_memory does not itself produce an iterable of output chunks.
- chunksize=1000 yields an iterable TextFileReader of row chunks.

- [reference/api/pandas.read_csv#page](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
- [reference/api/pandas.read_csv#page](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)

## Q17 (comparison)

Why can DataFrame.pivot fail on repeated index/column combinations, and when should I use pivot_table instead?

**Reference answer:** pivot does not aggregate and raises ValueError for duplicate index/column pairs. pivot_table aggregates repeated pairs using aggfunc (mean by default; select a suitable explicit function such as sum).

- pivot requires unique index/column pairs and raises ValueError for duplicates.
- pivot_table aggregates repeated combinations using aggfunc.

- [reference/api/pandas.DataFrame.pivot#page](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.pivot.html)
- [reference/api/pandas.DataFrame.pivot_table#page](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.pivot_table.html)

## Q18 (comparison)

How do .loc and .iloc differ, and do their slice stop endpoints get included? Assume unique sorted labels and valid slice bounds.

**Reference answer:** .loc selects by label and includes both label endpoints. .iloc selects by integer position with Python-style slicing that excludes the stop position.

- loc is label-based and includes both label slice endpoints.
- iloc is integer-position based and excludes the slice stop.

- [reference/api/pandas.DataFrame.loc#page](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.loc.html)
- [user_guide/indexing#different-choices-for-indexing](https://pandas.pydata.org/docs/user_guide/indexing.html#different-choices-for-indexing)
- [user_guide/indexing#selection-by-label](https://pandas.pydata.org/docs/user_guide/indexing.html#selection-by-label)
- [reference/api/pandas.DataFrame.iloc#page](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.iloc.html)
- [user_guide/indexing#different-choices-for-indexing](https://pandas.pydata.org/docs/user_guide/indexing.html#different-choices-for-indexing)
- [user_guide/indexing#selection-by-position](https://pandas.pydata.org/docs/user_guide/indexing.html#selection-by-position)

## Q19 (comparison)

With no explicit join keys, what does DataFrame.join match on and what is its default join type? How does this differ from DataFrame.merge?

**Reference answer:** join defaults to index-on-index and how='left'. merge defaults to how='inner' and, without index flags or on, uses the intersection of column names as merge keys.

- join defaults to index-on-index with a left join.
- merge defaults to inner and common column names when no keys/index flags are supplied.

- [reference/api/pandas.DataFrame.join#page](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.join.html)
- [reference/api/pandas.DataFrame.merge#page](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html)

## Q20 (comparison)

For grouped data, how does aggregation differ from transform, and which should I use to add each group's mean back to every original row?

**Reference answer:** Aggregation reduces groups to summaries. transform preserves the original row index and broadcasts group summaries; use df.groupby('group')['value'].transform('mean') to align group means with original rows.

- Aggregation reduces groups to summary results.
- transform preserves the original index and broadcasts a group aggregation to its rows.

- [user_guide/groupby#aggregation](https://pandas.pydata.org/docs/user_guide/groupby.html#aggregation)
- [user_guide/groupby#transformation](https://pandas.pydata.org/docs/user_guide/groupby.html#transformation)
- [user_guide/groupby#transformation](https://pandas.pydata.org/docs/user_guide/groupby.html#transformation)

## Q21 (comparison)

In pd.concat, how do ignore_index=True and keys=['left','right'] differ when combining two DataFrames along rows?

**Reference answer:** ignore_index=True discards the concatenation-axis index labels and creates 0..n-1. keys adds outer levels to a hierarchical index that identify the inputs; it is not simple index renumbering.

- ignore_index=True renumbers the concatenation axis from 0 to n-1.
- keys constructs an outer level of a hierarchical index.

- [reference/api/pandas.concat#page](https://pandas.pydata.org/docs/reference/api/pandas.concat.html)
- [reference/api/pandas.concat#page](https://pandas.pydata.org/docs/reference/api/pandas.concat.html)

## Q22 (comparison)

When working with a DatetimeIndex, when should I use tz_localize and when should I use tz_convert?

**Reference answer:** Use tz_localize to attach a time zone to timezone-naive timestamps. Use tz_convert to convert already timezone-aware timestamps into another time zone, preserving their underlying instants.

- tz_localize assigns a timezone to naive timestamps.
- tz_convert converts timezone-aware timestamps between zones.

- [user_guide/timeseries#time-zone-handling](https://pandas.pydata.org/docs/user_guide/timeseries.html#time-zone-handling)
- [user_guide/timeseries#time-zone-handling](https://pandas.pydata.org/docs/user_guide/timeseries.html#time-zone-handling)

## Q23 (comparison)

How does a rolling window differ from an expanding window when computing statistics over a Series?

**Reference answer:** A rolling window moves over a fixed-size or variable-size subset. An expanding window accumulates observations from the start up to the current position.

- Rolling uses a sliding window.
- Expanding uses an accumulating window.

- [user_guide/window#overview](https://pandas.pydata.org/docs/user_guide/window.html#overview)
- [user_guide/window#overview](https://pandas.pydata.org/docs/user_guide/window.html#overview)

## Q24 (comparison)

For Series.apply with a callable, what changes between by_row='compat' and by_row=False?

**Reference answer:** With by_row='compat', a callable receives individual elements, like Series.map. With by_row=False it receives the whole Series at once.

- With compat a callable is applied to individual elements.
- With by_row=False the callable receives the entire Series.

- [reference/api/pandas.Series.apply#page](https://pandas.pydata.org/docs/reference/api/pandas.Series.apply.html)
- [reference/api/pandas.Series.apply#page](https://pandas.pydata.org/docs/reference/api/pandas.Series.apply.html)

## Q25 (private_data)

How many rows in my company's private customers.csv have a missing age? I have not uploaded or provided that file.

**Reference answer:** INSUFFICIENT_EVIDENCE

- Explicitly decline to give the unsupported answer.



## Q26 (private_data)

What was the exact total revenue in our team's unpublished 2026 sales DataFrame? No data or values have been supplied.

**Reference answer:** INSUFFICIENT_EVIDENCE

- Explicitly decline to give the unsupported answer.



## Q27 (unsupported_api)

What are the documented parameters of the pandas function pd.teleport_to_mars, and how do I call it?

**Reference answer:** INSUFFICIENT_EVIDENCE

- Explicitly decline to give the unsupported answer.



## Q28 (unmeasured_performance)

Exactly how many milliseconds will pd.read_csv take to read my 10 GB CSV on my own laptop? No hardware details, data, or benchmark are provided.

**Reference answer:** INSUFFICIENT_EVIDENCE

- Explicitly decline to give the unsupported answer.



## Q29 (live_information)

What is the current live USD to CNY exchange rate right now?

**Reference answer:** INSUFFICIENT_EVIDENCE

- Explicitly decline to give the unsupported answer.



## Q30 (private_policy)

What is the official CS5481 team's private policy for deleting customer data after 2026-12-01? The policy has not been supplied.

**Reference answer:** INSUFFICIENT_EVIDENCE

- Explicitly decline to give the unsupported answer.
