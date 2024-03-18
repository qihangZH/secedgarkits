import pandas as pd
import re
import numpy as np


def parser_10k_10q_df(html_str):
    """
    Parse the 10-K file into dataframe
    :param html_str: the html file
    :return: the dataframe, the dataframe contains the item_number, start_index, end_index, segment_html
    """

    # Write the regex
    # regex = re.compile(r'((\<[^\<\>]+>)(Item|ITEM)(\s|&#160;|&nbsp;)(\d+[A-Z]{0,})\.{0,1})',
    #                    flags=re.IGNORECASE)
    """new version: match the outsiders but not the first tags"""
    regex = re.compile(
        r'(\<\/[^\<\>]+\>(\<[^\/][^\<\>]*\>)+(?!item)[^\<\>]*(\<\/[^\<\>]+\>)+)?'
        r'(\<[^\/][^\<\>]*\>)+(item)(\s|&#160;|&nbsp;)(\d+[A-Z]{0,})\.{0,1}[^\<\>]*(\<\/[^\<\>]+\>)+'
        r'((\<[^\/][^\<\>]*\>)+(?!item)[^\<\>]*(\<\/[^\<\>]+\>)+)?',
        flags=re.IGNORECASE)

    # Use finditer to math the regex
    matches = regex.finditer(html_str)

    test_df = pd.DataFrame(
        [
            (
                bool(re.search(r'(href|onclick)\=',
                               x.group(0), flags=re.IGNORECASE)),
                x.groups()[6],
                x.start(),
                x.end()
            )
            for x in matches
        ]
    )

    # if test_df.shape[0] == 0:
    #     return pd.DataFrame(columns=['item_num', 'start_index', 'end_index', 'segment_html'])

    test_df.columns = ['contain_links', 'item_num', 'start', 'end']

    # remove all the items that contain links
    nolink_test_df = test_df[~test_df['contain_links']].sort_values(
        'start', ascending=True)

    # remove the duplicated item numbers if consecutive
    picked_lines = [True]  # the first line is always picked
    for ind in range(1, nolink_test_df.shape[0]):
        last_item_num = nolink_test_df.iloc[ind - 1]['item_num']
        this_item_num = nolink_test_df.iloc[ind]['item_num']
        if last_item_num == this_item_num:
            picked_lines.append(False)
        else:
            picked_lines.append(True)

    # nolink_test_df = nolink_test_df[picked_lines].sort_values(
    #     'start', ascending=True)

    # if nolink_test_df.duplicated(subset=['item_num']).any():
    #     duplicated_item_num = nolink_test_df[
    #         nolink_test_df.duplicated(subset=['item_num'])
    #     ]['item_num'].unique()

    #     # remove the duplicated item numbers
    #     # if they are not bigger then the num before and smaller then number after
    #     picked_lines = [True]  # the first line is always picked
    #     for ind in range(1, nolink_test_df.shape[0] - 1):
    #         # read the number
    #         last_item_num, last_item_char = re.search(
    #             r'(\d+)([A-Z]{0,})',
    #             nolink_test_df.iloc[ind - 1]['item_num'],
    #             flags=re.IGNORECASE
    #         ).groups()
    #         this_item_num, this_item_char = re.search(
    #             r'(\d+)([A-Z]{0,})',
    #             nolink_test_df.iloc[ind]['item_num'],
    #             flags=re.IGNORECASE
    #         ).groups()

    #         next_item_num, next_item_char = re.search(
    #             r'(\d+)([A-Z]{0,})',
    #             nolink_test_df.iloc[ind + 1]['item_num'],
    #             flags=re.IGNORECASE
    #         ).groups()

    #         # first situation: not in the duplicated_item_num
    #         if not (nolink_test_df.iloc[ind]['item_num'] in duplicated_item_num):
    #             picked_lines.append(True)
    #         else:

    #             bigger_equal_then_last = (
    #                 (int(last_item_num) < int(this_item_num))
    #                                       or
    #                 (
    #                     (int(last_item_num) == int(this_item_num)) and
    #                     (last_item_char.lower() <= this_item_char.lower())
    #                 )
    #                                       )
    #             smaller_equal_then_next = (
    #                 (int(this_item_num) < int(next_item_num))
    #                                       or
    #                 (
    #                     (int(this_item_num) == int(next_item_num)) and
    #                     (this_item_char.lower() <= next_item_char.lower())
    #                 )
    #                                       )

    #             if bigger_equal_then_last and smaller_equal_then_next:
    #                 # keep
    #                 picked_lines.append(True)
    #             else:
    #                 picked_lines.append(False)

    #     # the last line only check if it is bigger than the last line
    #     """special-> last line"""
    #     last_item_num, last_item_char = re.search(
    #         r'(\d+)([A-Z]{0,})',
    #         nolink_test_df.iloc[-2]['item_num'],
    #         flags=re.IGNORECASE
    #     ).groups()

    #     this_item_num, this_item_char = re.search(
    #         r'(\d+)([A-Z]{0,})',
    #         nolink_test_df.iloc[-1]['item_num'],
    #         flags=re.IGNORECASE
    #     ).groups()

    #     if not (nolink_test_df.iloc[-1]['item_num'] in duplicated_item_num):
    #             picked_lines.append(True)
    #     else:
    #         bigger_equal_then_last = (
    #             (int(last_item_num) < int(this_item_num))
    #                                     or
    #             (
    #                 (int(last_item_num) == int(this_item_num)) and
    #                 (last_item_char.lower() <= this_item_char.lower())
    #             )
    #                                     )

    #         if bigger_equal_then_last:
    #             # keep
    #             picked_lines.append(True)
    #         else:
    #             picked_lines.append(False)

    #     nolink_test_df = nolink_test_df[picked_lines].sort_values(
    #         'start', ascending=True)

    # # some times the first time the ind is error:
    # if nolink_test_df.duplicated(subset=['item_num']).any():
    #     # remove the duplicates of "first occurence", keep other duplicates
    #     nolink_test_df = nolink_test_df[
    #         # xor count, only the first occurence are these two set difference.
    #         # and then use ~ to reverse the boolean
    #         ~np.logical_xor(
    #             nolink_test_df.duplicated('item_num', False),
    #             nolink_test_df.duplicated('item_num', 'first')
    #         )
    #         ].sort_values('start', ascending=True)

    """Do not use assertion"""
    # assert not nolink_test_df.duplicated(subset=['item_num']).any(), \
    #     "PARSE ERROR, There are duplicated item numbers with out link(href/onclick) in the 10-K Form."

    nolink_test_df['end_index'] = nolink_test_df['start'].shift(
        -1).astype(pd.Int64Dtype())

    nolink_test_df['end_index'].iloc[-1] = len(html_str)

    nolink_test_df = nolink_test_df.rename(columns={'start': 'start_index'}
                                           )[['item_num', 'start_index', 'end_index']]

    nolink_test_df['segment_html'] = nolink_test_df.apply(
        lambda x: html_str[x['start_index']:x['end_index']], axis=1)

    nolink_test_df = nolink_test_df.reset_index(drop=True)

    return nolink_test_df
