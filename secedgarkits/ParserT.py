import pandas as pd
import re


def parser_10k_df(html_str):
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
        r'\<\/[^\<\>]+\>((\<[^\/][^\<\>]*\>)+)(item)(\s|&#160;|&nbsp;)(\d+[A-Z]{0,})\.{0,1}',
        flags=re.IGNORECASE)

    # Use finditer to math the regex
    matches = regex.finditer(html_str)

    test_df = pd.DataFrame(
        [
            (
                bool(re.search(r'(href|onclick)\=', x.groups()[0], flags=re.IGNORECASE)),
                x.groups()[-1],
                x.start(1),
                x.end()
            )
            for x in matches
        ]
    )

    test_df.columns = ['contain_links', 'item_num', 'start', 'end']

    # remove indexs, These are first occurance of each item number
    noindex_test_df = test_df[test_df.sort_values('start', ascending=True).duplicated(
        subset=['item_num'], keep='first')
    ]

    # remove all the items that contain links
    noindex_nolink_test_df = noindex_test_df[~noindex_test_df['contain_links']].sort_values('start', ascending=True)

    # remove the duplicated item numbers if consecutive
    picked_lines = [True] # the first line is always picked
    for ind in range(1, noindex_nolink_test_df.shape[0]):
        last_item_num = noindex_nolink_test_df.iloc[ind - 1]['item_num']
        this_item_num = noindex_nolink_test_df.iloc[ind]['item_num']
        if last_item_num == this_item_num:
            picked_lines.append(False)
        else:
            picked_lines.append(True)
    noindex_nolink_test_df = noindex_nolink_test_df[picked_lines].sort_values('start', ascending=True)

    assert not noindex_nolink_test_df.duplicated(subset=['item_num']).any(), \
        "PARSE ERROR, There are duplicated item numbers with out link(href/onclick) in the 10-K Form."

    noindex_nolink_test_df['end_index'] = noindex_nolink_test_df['start'].shift(-1).astype(pd.Int64Dtype())

    noindex_nolink_test_df['end_index'].iloc[-1] = len(html_str)

    noindex_nolink_test_df = noindex_nolink_test_df.rename(columns={'start': 'start_index'}
                                                           )[['item_num', 'start_index', 'end_index']]

    noindex_nolink_test_df['segment_html'] = noindex_nolink_test_df.apply(
        lambda x: html_str[x['start_index']:x['end_index']], axis=1)

    return noindex_nolink_test_df
