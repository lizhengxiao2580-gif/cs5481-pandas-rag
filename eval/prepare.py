"""Freeze a source-grounded benchmark before any formal system outputs are read."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "eval"


def api(name):
    return "reference/api/pandas." + name + "#page"


# Each criterion has a literal/regex source locator, checked against the committed corpus.
# These locators construct gold evidence; they are NOT answer or retrieval scorers.
SPECS = [
    ("basic", "How can I read only the name and age columns from a CSV file with pandas?",
     "Use pd.read_csv(path, usecols=['name', 'age']). usecols selects a subset of columns.",
     [api("read_csv")], [("Select columns at read time with usecols=['name', 'age'].", r"usecolsSequence[\s\S]{0,600}")]),
    ("basic", "How do I write a DataFrame to CSV without writing the row index?",
     "Use df.to_csv(path, index=False); index controls writing the row names, and defaults to True.",
     [api("DataFrame.to_csv")], [("Set index=False when calling to_csv.", r"indexbool, default True\s+Write row names \(index\)\.")]),
    ("basic", "How can I keep rows whose country column is either UK or JP?",
     "Use df[df['country'].isin(['UK', 'JP'])]. isin returns a Boolean membership mask.",
     [api("DataFrame.isin"), "user_guide/indexing#indexing-with-isin"], [("Use isin with the list of allowed values and use its Boolean mask to filter rows.", r"[\s\S]{0,160}Whether each element[\s\S]{0,160}|[\s\S]{0,100}isin\([\s\S]{0,250}")]),
    ("basic", "How do I drop a row if either its name or age is missing, while ignoring missing values in other columns?",
     "Use df.dropna(subset=['name', 'age'], how='any'). subset restricts considered columns; any drops rows with at least one missing value.",
     [api("DataFrame.dropna")], [("Use subset=['name','age'] to restrict missing-value checks.", r"subsetcolumn[\s\S]{0,250}"), ("Use how='any' to remove a row if either selected value is missing.", r"‘any’ : If any NA values[\s\S]{0,100}")]),
    ("basic", "How can I fill missing values in column A with 0 and column B with 'unknown', leaving other columns alone?",
     "Use df.fillna({'A': 0, 'B': 'unknown'}). A mapping supplies per-column replacement values; unspecified columns are not filled.",
     [api("DataFrame.fillna")], [("Pass a per-column dictionary to fillna.", r"valuescalar, dict[\s\S]{0,460}"), ("Columns absent from the mapping remain unfilled.", r"Values not in the dict/Series/DataFrame will not be filled\.")]),
    ("basic", "How do I calculate mean sales separately for each combination of region and product?",
     "Use df.groupby(['region', 'product'])['sales'].mean(). A list of grouping column names forms combination groups.",
     [api("DataFrame.groupby"), "user_guide/groupby#splitting-an-object-into-groups"], [("Group by both columns using a list, select sales, and compute mean.", r"A label or list of labels[\s\S]{0,350}|groupby\(\[.{0,120}\][\s\S]{0,160}")]),
    ("basic", "How do I reshape a wide table into long format while keeping id as an identifier and unpivoting only Jan and Feb?",
     "Use pd.melt(df, id_vars=['id'], value_vars=['Jan', 'Feb']). id_vars stay as identifiers; value_vars select measured columns to unpivot.",
     [api("melt")], [("Set id_vars=['id'] to preserve the identifier.", r"id_varsscalar[\s\S]{0,150}"), ("Set value_vars=['Jan','Feb'] to select the unpivoted columns.", r"value_varsscalar[\s\S]{0,240}")]),
    ("basic", "How can I convert only column age to int64 and column score to float64 in a DataFrame?",
     "Use df.astype({'age': 'int64', 'score': 'float64'}). A dtype mapping specifies column-specific types; other columns remain unchanged.",
     [api("DataFrame.astype")], [("Pass a mapping of column names to dtypes to astype.", r"Alternatively, use a mapping[\s\S]{0,450}")]),
    ("parameter", "With DataFrame.drop_duplicates, how can I remove every occurrence of duplicate ids rather than keeping one? Does this method compare index labels?",
     "Use df.drop_duplicates(subset=['id'], keep=False). It removes all duplicate-id rows; index labels are ignored.",
     [api("DataFrame.drop_duplicates")], [("subset=['id'] with keep=False removes all occurrences of duplicated ids.", r"False : Drop all duplicates\."), ("Index labels are ignored by drop_duplicates.", r"Indexes, including time indexes are ignored\.")]),
    ("parameter", "How can Series.value_counts report proportions and include missing values as a counted category?",
     "Use s.value_counts(normalize=True, dropna=False). normalize returns relative frequencies and dropna=False includes missing values.",
     [api("Series.value_counts")], [("normalize=True returns relative frequencies.", r"If True then the object returned will contain the relative frequencies[\s\S]{0,90}"), ("dropna=False includes NA values in the counts.", r"With dropna set to False[\s\S]{0,150}")]),
    ("parameter", "When both merge key columns contain null values, can pandas match those rows together, and is this the same as typical SQL joins?",
     "Yes, pandas matches rows whose merge keys are null on both sides. This differs from usual SQL join behavior.",
     [api("DataFrame.merge")], [("Null keys on both sides can match each other.", r"If both key columns contain rows where the key is a null value[\s\S]{0,150}"), ("This differs from usual SQL join behavior.", r"This is different from usual SQL join behaviour[\s\S]{0,90}")]),
    ("parameter", "If a nullable Boolean indexing mask contains pd.NA, are those rows selected? How can I retain those rows?",
     "Mask NA entries are treated as False. Use mask.fillna(True) before indexing to retain those positions.",
     ["user_guide/boolean#indexing-with-na-values"], [("NA entries in a Boolean mask are treated as False.", r"pandas allows indexing[\s\S]{0,150}"), ("Fill mask NA entries with True to keep those rows.", r"If you would prefer to keep the NA values[\s\S]{0,160}")]),
    ("parameter", "How do I construct a Series of integers with missing values without converting it to floating point? Is 'Int64' the same spelling as NumPy 'int64'?",
     "Specify dtype='Int64', for example pd.Series([1, None], dtype='Int64'). The capital I distinguishes the nullable integer dtype from NumPy int64; missing values become pandas.NA.",
     ["user_guide/integer_na#construction", "user_guide/integer_na#nullable-integer-data-type"], [("Explicitly use nullable Int64 with a capital I.", r'Or the string alias "Int64"[\s\S]{0,180}'), ("Missing values are represented by pandas.NA.", r"All NA-like values are replaced with pandas.NA\.")]),
    ("parameter", "In Series.map with an ordinary dictionary, what happens to values that have no matching key? How do I avoid applying a function to existing missing values?",
     "Unmatched values become NaN for an ordinary dict. Set na_action='ignore' to propagate existing missing values without calling the mapping function on them.",
     [api("Series.map")], [("Values absent from an ordinary dictionary become NaN.", r"When func is a dictionary[\s\S]{0,210}"), ("na_action='ignore' skips existing missing values.", r"na_action\{[\s\S]{0,200}")]),
    ("parameter", "Does DataFrame.groupby include groups whose grouping keys are NA by default? How do I include them?",
     "The default dropna=True excludes rows with NA group keys. Set dropna=False to include NA as a group key.",
     [api("DataFrame.groupby")], [("dropna=True excludes NA group keys by default; dropna=False includes them.", r"dropnabool, default True[\s\S]{0,420}")]),
    ("parameter", "Does read_csv(low_memory=True) return an iterator of chunks? Which option should I use to process 1000 rows at a time?",
     "No. low_memory controls internal parsing; the entire file is still returned in one DataFrame. Use chunksize=1000 to return a TextFileReader for iteration.",
     [api("read_csv"), "user_guide/io#iterating-through-files-chunk-by-chunk"], [("low_memory does not itself produce an iterable of output chunks.", r"low_memorybool[\s\S]{0,650}"), ("chunksize=1000 yields an iterable TextFileReader of row chunks.", r"chunksizeint[\s\S]{0,460}")]),
    ("comparison", "Why can DataFrame.pivot fail on repeated index/column combinations, and when should I use pivot_table instead?",
     "pivot does not aggregate and raises ValueError for duplicate index/column pairs. pivot_table aggregates repeated pairs using aggfunc (mean by default; select a suitable explicit function such as sum).",
     [api("DataFrame.pivot"), api("DataFrame.pivot_table"), "user_guide/reshaping#pivot-and-pivot-table"], [("pivot requires unique index/column pairs and raises ValueError for duplicates.", r"When there are any index, columns combinations[\s\S]{0,180}"), ("pivot_table aggregates repeated combinations using aggfunc.", r"aggfuncfunction[\s\S]{0,400}")]),
    ("comparison", "How do .loc and .iloc differ, and do their slice stop endpoints get included? Assume unique sorted labels and valid slice bounds.",
     ".loc selects by label and includes both label endpoints. .iloc selects by integer position with Python-style slicing that excludes the stop position.",
     [api("DataFrame.loc"), api("DataFrame.iloc"), "user_guide/indexing#different-choices-for-indexing", "user_guide/indexing#selection-by-label", "user_guide/indexing#selection-by-position"], [("loc is label-based and includes both label slice endpoints.", r"both the start and the stop[\s\S]{0,100}|both the start and the stop[\s\S]{0,100}"), ("iloc is integer-position based and excludes the slice stop.", r"Purely integer-location[\s\S]{0,130}|Python/NumPy[\s\S]{0,150}|start of the slice[\s\S]{0,190}")]),
    ("comparison", "With no explicit join keys, what does DataFrame.join match on and what is its default join type? How does this differ from DataFrame.merge?",
     "join defaults to index-on-index and how='left'. merge defaults to how='inner' and, without index flags or on, uses the intersection of column names as merge keys.",
     [api("DataFrame.join"), api("DataFrame.merge")], [("join defaults to index-on-index with a left join.", r"otherwise joins index-on-index[\s\S]{0,420}"), ("merge defaults to inner and common column names when no keys/index flags are supplied.", r"how='inner'[\s\S]{0,100}|this defaults to the intersection of the columns[\s\S]{0,100}")]),
    ("comparison", "For grouped data, how does aggregation differ from transform, and which should I use to add each group's mean back to every original row?",
     "Aggregation reduces groups to summaries. transform preserves the original row index and broadcasts group summaries; use df.groupby('group')['value'].transform('mean') to align group means with original rows.",
     ["user_guide/groupby#aggregation", "user_guide/groupby#transformation"], [("Aggregation reduces groups to summary results.", r"An aggregation[\s\S]{0,300}|aggregate[\s\S]{0,180}"), ("transform preserves the original index and broadcasts a group aggregation to its rows.", r"A transformation is a GroupBy operation[\s\S]{0,190}|When an aggregation method is provided[\s\S]{0,170}")]),
    ("comparison", "In pd.concat, how do ignore_index=True and keys=['left','right'] differ when combining two DataFrames along rows?",
     "ignore_index=True discards the concatenation-axis index labels and creates 0..n-1. keys adds outer levels to a hierarchical index that identify the inputs; it is not simple index renumbering.",
     [api("concat"), "user_guide/merging#concat"], [("ignore_index=True renumbers the concatenation axis from 0 to n-1.", r"ignore_indexbool[\s\S]{0,310}"), ("keys constructs an outer level of a hierarchical index.", r"keyssequence[\s\S]{0,240}")]),
    ("comparison", "When working with a DatetimeIndex, when should I use tz_localize and when should I use tz_convert?",
     "Use tz_localize to attach a time zone to timezone-naive timestamps. Use tz_convert to convert already timezone-aware timestamps into another time zone, preserving their underlying instants.",
     ["user_guide/timeseries#time-zone-handling"], [("tz_localize assigns a timezone to naive timestamps.", r"To localize these dates[\s\S]{0,300}"), ("tz_convert converts timezone-aware timestamps between zones.", r"[\s\S]{0,140}tz_convert[\s\S]{0,280}")]),
    ("comparison", "How does a rolling window differ from an expanding window when computing statistics over a Series?",
     "A rolling window moves over a fixed-size or variable-size subset. An expanding window accumulates observations from the start up to the current position.",
     ["user_guide/window#overview", "user_guide/window#rolling-window", "user_guide/window#expanding-window"], [("Rolling uses a sliding window.", r"Rolling window: Generic fixed or variable sliding window over the values\."), ("Expanding uses an accumulating window.", r"Expanding window: Accumulating window over the values\.")]),
    ("comparison", "For Series.apply with a callable, what changes between by_row='compat' and by_row=False?",
     "With by_row='compat', a callable receives individual elements, like Series.map. With by_row=False it receives the whole Series at once.",
     [api("Series.apply")], [("With compat a callable is applied to individual elements.", r'If "compat" and func is a callable[\s\S]{0,170}'), ("With by_row=False the callable receives the entire Series.", r"If False, the func will be passed the whole Series at once\.")]),
]

NEGATIVES = [
    ("private_data", "How many rows in my company's private customers.csv have a missing age? I have not uploaded or provided that file.", "The private data are not present; the actual missing-value count cannot be determined."),
    ("private_data", "What was the exact total revenue in our team's unpublished 2026 sales DataFrame? No data or values have been supplied.", "The actual private revenue values are absent from the knowledge base."),
    ("unsupported_api", "What are the documented parameters of the pandas function pd.teleport_to_mars, and how do I call it?", "No such API is documented in the knowledge base; do not invent its parameters."),
    ("unmeasured_performance", "Exactly how many milliseconds will pd.read_csv take to read my 10 GB CSV on my own laptop? No hardware details, data, or benchmark are provided.", "Documentation cannot determine the exact runtime of an unmeasured private workload."),
    ("live_information", "What is the current live USD to CNY exchange rate right now?", "The static pandas documentation contains no live exchange-rate feed."),
    ("private_policy", "What is the official CS5481 team's private policy for deleting customer data after 2026-12-01? The policy has not been supplied.", "The private team policy is not part of the pandas corpus."),
]


def main():
    sections = {s["section_id"]: s for s in map(json.loads, (ROOT / "data/sections.jsonl").read_text().splitlines())}
    questions = []
    for number, (category, question, answer, sources, criteria) in enumerate(SPECS, 1):
        evidence, points = [], []
        for point, pattern in criteria:
            found = []
            for sid in sources:
                if sid not in sections:
                    continue
                s = sections[sid]
                m = re.search(pattern, s["text"], re.I)
                if m:
                    quote = s["text"][max(0, m.start()-140):min(len(s["text"]), m.end()+140)]
                    found.append({"section_id": sid, "url": s["url"], "quote": quote})
            if not found:
                raise ValueError(f"Q{number:02d}: no gold evidence for {point} ({sources})")
            points.append(point)
            evidence.extend(found)
        questions.append({"id": f"Q{number:02d}", "category": category, "answerable": True,
                          "question": question, "gold_answer": answer, "required_points": points,
                          "gold_evidence": evidence})
    for category, question, reason in NEGATIVES:
        questions.append({"id": f"Q{len(questions)+1:02d}", "category": category, "answerable": False,
                          "question": question, "gold_answer": "INSUFFICIENT_EVIDENCE",
                          "required_points": ["Explicitly decline to give the unsupported answer."],
                          "gold_evidence": [], "unanswerable_reason": reason})
    OUT.mkdir(exist_ok=True)
    path = OUT / "questions.jsonl"
    path.write_text("".join(json.dumps(q, ensure_ascii=False)+"\n" for q in questions), encoding="utf-8")
    print("Frozen benchmark:", len(questions), "questions; SHA256", hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
