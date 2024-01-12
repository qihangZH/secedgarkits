# This package is to support the https://github.com/sec-edgar/sec-edgar project
import secedgar
import os
import re
import json
import pathlib
import copy


def metadata_parsed_dir_augment(stored_dir) -> dict:
    """
    After use secedgar.MetaParser().process() This function will return a dict contains the real path of the files
    The new dict is actually the augment of the original dict, it add on the real path of the files to the dict.
    NEW document key: full_filename, full_filename_absolute
    NEW outsider key: METADATA_JSON_FILENAME, METADATA_JSON_ABS_PATH
    Use new metadata dict by calling the function secedgar_utils.metadata_parsed_dir_augment()[grp]
    :param stored_dir: the directory of the stored secedgar.MetaParser().process() files
    :return: dict contains the real path of the files
    """
    assert os.path.isdir(stored_dir), "the input path is not a directory"

    filename_l = os.listdir(stored_dir)

    metadata_regex = re.compile(r'^(\d+)\.metadata.json$', flags=re.IGNORECASE)
    matadata_dict = {}
    for f in filename_l:
        match = re.search(metadata_regex, f)
        if match:
            matadata_dict[int(match.groups()[0])] = f
        else:
            continue
    if len(matadata_dict) == 0:
        raise ValueError("No metadata.json file found in the directory")

    augment_metadatas_dict = {}
    for grp, grp_f in matadata_dict.items():
        with open(os.path.join(stored_dir, grp_f), 'r') as f:
            grp_metadata_json = json.load(f)

        augment_metadatas_dict[grp] = {
            'METADATA_JSON_FILENAME': grp_f,
            'METADATA_JSON_ABS_PATH': pathlib.Path(stored_dir, grp_f).absolute().as_posix(),
            **{
                k: (
                    [
                        {
                            **d,
                            'full_filename': '{}.{}'.format(grp, d['filename']),
                            'full_filename_absolute': pathlib.Path(stored_dir,
                                                                   '{}.{}'.format(grp,
                                                                                  d['filename'])).absolute().as_posix()
                        }
                        for d in v
                    ] if k == 'documents' else v
                )
                for k, v in grp_metadata_json.items()
            }
        }

    return augment_metadatas_dict
