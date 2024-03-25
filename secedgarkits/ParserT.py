import pandas as pd
import re
import warnings


def parser_10k_10q_df(html_str):
    """
    Parse the 10-K file into dataframe,
    Some issues-> if duplicates occur, then
        1) some of are index, just use them
        2) some of them belong to second part
    :param html_str: the html file
    :return: the dataframe, the dataframe contains the item_number, start_index, end_index, segment_html
    """
    warnings.warn("This function face several challenges, include not applicable in complicated HTM files",
                  DeprecationWarning)

    # Use regex to parse the 10-K/Q file
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

    if test_df.shape[0] == 0:
        return pd.DataFrame(columns=['item_num', 'start_index', 'end_index', 'segment_html'])

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

    nolink_test_df = nolink_test_df.reset_index(drop=True)[['item_num', 'start_index', 'end_index', 'segment_html']]

    return nolink_test_df
