import pandas as pd
import json
import os
from globals import *

with open("config.json") as cfg:
    fields = json.load(cfg)


if not fields:
    raise ValueError("No fields specified in config file")

if not "LOOKUP_FIELDS" in locals() and LOOKUP_FIELDS:
    raise ValueError("Not sure which fields to lookup in each row. Please update config.json with LOOKUP_FIELDS")


def join_with_underscore(items):
    type_cast_to_str = False
    for x in items:
        if not isinstance(x, str):
            # raise TypeError("join_with_underscore()  inputs must be string")
            type_cast_to_str = True
    if type_cast_to_str:
        items = [str(x) for x in items]

    return "_".join(items)

def reliablity_weighted_sum(df, weights_col_name, items):
    grouped = df.groupby(SOURCE_COL)

    for x, y in items.items():
        first_index = x
        break

    # group_name = df.iloc[first_index].loc[SOURCE_COL]
    group_name = df.loc[first_index, SOURCE_COL]
    group = grouped.get_group(group_name)

    new_reliability_col = items * (group[weights_col_name] / sum(group[weights_col_name]))
    return sum(new_reliability_col)

def get_first_item(items):
    return items.iloc[0]

def get_by_preference(group):
    preferences = INVENTORY_PREFERENCE_BY_COMPARTMENT[group.name]

    for pref in preferences:
        for index, row in group.iterrows():
            if pref == row[SOURCE_COL]:
                return row




def main():
    if not INCLUDE_ORIGINAL and not KEEP_ALL_DUPLICATES:
        raise ValueError("Cannot have both INCLUDE_ORIGINAL and KEEP_REPEATED_DUPLICATES fields as False")

    datafilepath = DATA_FILEPATH
    if os.path.splitext(datafilepath)[-1].lower() == ".csv":
        df = pd.read_csv(datafilepath)
    elif os.path.splitext(datafilepath)[-1].lower() == ".xlsx":
        df = pd.read_excel(datafilepath)

    output_csvfilepath = OUTPUT_FILEPATH
    print("Starting processing data...")


    if INCLUDE_ORIGINAL:
        keep = False
    else:
        keep = 'first'

    df_chunk_filtered = df[LOOKUP_FIELDS]

    if not KEEP_ALL_DUPLICATES:
        # from a set of duplicates a logic is applied to figure out what is sent to write to output file
        # for example only the first duplicate is kept
        # or duplicates are filtered preferentially and high priority one is kept etc
        df_dups = df[df_chunk_filtered.duplicated(keep=keep)]
        df_dups_filtered = df_dups[LOOKUP_FIELDS]
        df = df_dups[df_dups_filtered.duplicated(keep=keep).apply(lambda x: not x)]
    else:
        # all duplicates found are sent to be written to output file
        df = df[df_chunk_filtered.duplicated(keep=keep)]

    # Duplicates found
    # print(df)

    print("Grouping duplicates by LOOKUP_FIELDS")
    grouped = df.groupby(LOOKUP_FIELDS)

    print("Grouping duplicates by SOURCE_COL")
    if SOURCE_COL not in df.columns: raise ("SOURCE_COL not found in input file's header")


    print("Combining each group to a single row")
    funcname_cols_map = COL_FUNC_PAIRS
    for col in list(set(df.columns) - set(
            COL_FUNC_PAIRS.keys())):  # col names in columns, not in key of COL_FUNC_PAIRS
        funcname_cols_map[col] = COL_FUNC_DEFAULT

    to_be_concat = []
    for name, df in grouped:
        # print(name, df)
        # find functions mapping for this df
        func_cols_map = {}
        for key, val in funcname_cols_map.items():
            if "reliablity_weighted_sum" in val:
                args = val.split(":")
                if len(args) > 1:
                    weights_col_name = args[1]
                func_cols_map[key] = lambda items: reliablity_weighted_sum(df, weights_col_name, items)
            else:
                func_cols_map[key] = eval(val)
        grouped_by_src = df.groupby(SOURCE_COL)
        df_new = grouped_by_src.agg(func_cols_map)

        # If we have 2 or more duplicates with same compartment use `INVENTORY_PREFERENCE_BY_COMPARTMENT`
        grouped = df_new.groupby(COMPARTMENT_COL)
        df_new = grouped.apply(get_by_preference)
        # print(df_new)
        # print(name)
        to_be_concat.append(df_new)

    df = pd.concat(to_be_concat)

    #
    # print(df)
    print("Writing to output")
    if os.path.splitext(output_csvfilepath)[-1].lower() == ".csv":
        df.to_csv(output_csvfilepath, header=df.columns, index=False, mode='w')
    elif os.path.splitext(output_csvfilepath)[-1].lower() == ".xlsx":
        writer = pd.ExcelWriter(output_csvfilepath)
        df.to_excel(writer, columns=df.columns, index=False)
        writer.save()

    print("Process completed. Check the output file for results")

if __name__ == "__main__":
    main()