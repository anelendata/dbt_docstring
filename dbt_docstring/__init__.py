#!/usr/bin/env python3
import argparse, datetime, logging, os, sys
from collections import defaultdict
from collections import OrderedDict

from textwrap import indent
import yaml,re

logger = logging.getLogger(__name__)

COMMAND = "dbt_docstring"
DBT_BLOCK_START_KEY = "```dbt"

def represent_odict(dumper, instance):
    return dumper.represent_mapping('tag:yaml.org,2002:map', instance.items())

yaml.add_representer(OrderedDict, represent_odict)

def construct_odict(loader, node):
    return OrderedDict(loader.construct_pairs(node))

yaml.add_constructor('tag:yaml.org,2002:map', construct_odict)




def _get_dirs(dbt_dir):
    dbt_project_file = os.path.join(dbt_dir, "dbt_project.yml")
    if not os.path.isfile(dbt_project_file):
        print("dbt_project.yml not found in {}".format(dbt_dir))
        exit(1)
    with open(dbt_project_file, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config["source-paths"], config["macro-paths"]


def _read_dbt_block(sql_file):
    """ Extract doc, dbt block from comments
    """
    with open(sql_file, "r") as f:
        sql = f.read()
    doc_start = sql.find("/*")
    doc_end = sql.find("*/")
    doc = sql[doc_start + 2:doc_end] if doc_start > -1 else ""

    dbt = {}
    if doc:
        dbt_start = doc.find(DBT_BLOCK_START_KEY)
        dbt_end = doc.find("```", dbt_start + len(DBT_BLOCK_START_KEY))

        if dbt_start > -1:
            dbt_block = doc[dbt_start + len(DBT_BLOCK_START_KEY):dbt_end]
            dbt = yaml.load(dbt_block, Loader=yaml.FullLoader)
        doc = doc[0:dbt_start].strip()

    return doc, dbt



def _scan_models(models_dir):
    """ local method to extract informatinon from each model dir
    """
    if not os.path.isdir(models_dir):
        logger.warning("%s directory not found" % models_dir)
        return

    doc_blocks = OrderedDict()
    dbt_blocks = OrderedDict()

    models_dirs = os.walk(models_dir)
    for cdir, dirs, files in models_dirs:
        for fname in files:
            # Parse the table name from the SQL file name
            if fname[-3:] != "sql":
                logger.info("Skipping non-sql file: " + fname)
                continue
            tname = fname[0:-4]
            doc_block, dbt_block= _read_dbt_block(os.path.join(cdir, fname))

            if dbt_block:
                dbt_blocks[tname] = dbt_block

            if doc_block:
                doc_blocks[tname] = doc_block

                if not dbt_block:
                    dbt_blocks[tname] = OrderedDict()
                dbt_blocks[tname]["name"] = tname
                dbt_blocks[tname]["description"] = "{{ doc(\"%s\") }}" % tname

                dbt_blocks[tname].move_to_end("description", False)
                dbt_blocks[tname].move_to_end("name", False)

    # write to file
    _write_property_yml(models_dir, dbt_blocks, "models")
    _write_doc_md(models_dir, doc_blocks)


def _scan_macros(macros_dir):
    """ Scan macro folder and collect resource information
    """
    if not os.path.isdir(macros_dir):
        logger.warning("%s directory not found" % macros_dir)
        return
    doc_blocks = OrderedDict()
    dbt_blocks = OrderedDict()

    macro_dirs = os.walk(macros_dir)
    for cdir, dirs, files in macro_dirs:
        for fname in files:
            # Parse the table name from the SQL file name
            if fname[-3:] != "sql":
                logger.info("Skipping non-sql file: " + fname)
                continue

            with open(os.path.join(cdir, fname), 'r') as f:
                sql = f.read()

            r = re.findall('(/\*.*?\*/.*?macro .*? )', sql, re.DOTALL)
            for block in r:
                rr =  re.match('.*macro (.*)\(',block,re.DOTALL)
                tname = rr.group(1)

                doc_start = block.find("/*")
                doc_end = block.find("*/")
                doc = block[doc_start + 2:doc_end] if doc_start > -1 else ""

                dbt = {}
                if doc:
                    dbt_start = doc.find(DBT_BLOCK_START_KEY)
                    dbt_end = doc.find("```", dbt_start + len(DBT_BLOCK_START_KEY))

                    if dbt_start > -1:
                        dbt_block = doc[dbt_start + len(DBT_BLOCK_START_KEY):dbt_end]
                        dbt = yaml.load(dbt_block, Loader=yaml.FullLoader)
                    doc = doc[0:dbt_start].strip()

                # doc -> model name, desc
                # dbt -> model columns
                if dbt:
                    dbt_blocks[tname] = dbt

                if doc:
                    doc_blocks[tname] = doc

                    if not dbt:
                       dbt_blocks[tname] = OrderedDict()
                    dbt_blocks[tname]["name"] = tname
                    dbt_blocks[tname]["description"] = "{{ doc(\"%s\") }}" % tname

                    dbt_blocks[tname].move_to_end("description", False)
                    dbt_blocks[tname].move_to_end("name", False)

    # write to file
    _write_property_yml(macros_dir, dbt_blocks, "macros")
    _write_doc_md(macros_dir, doc_blocks)



def _write_property_yml(resource_dir, dbt_blocks, keyword="models"):
    """ write to property file, default is schema.yaml
        keyword is `models` or `macros`
    """
    if args.schema:
        property_file = args.schema
    else:
        property_file = os.path.join(args.dbt_dir, resource_dir, "schema.yml")

    if args.backup and os.path.isfile(property_file):
        os.rename(property_file, property_file[:len(property_file) - 4] + "_" +
                  datetime.datetime.now().isoformat().replace(":", "-") +
                  ".yml_")

    with open(property_file, "w") as f:
        f.write("""# This file was auto-generated by dbtdocstr.
# Don't manually update.
# https://github.com/anelendata/dbt_docstring

""")
        if not dbt_blocks:
            return
        f.write(f"version: 2\n{keyword}:\n")
        f.write(indent(yaml.dump(list(dbt_blocks.values())), " " * 2) + "\n")


def _write_doc_md(resource_dir, doc_blocks):
    """ write to doc file, default is docs.md
    """
    if args.doc:
        doc_file = args.doc
    else:
        doc_file = os.path.join(args.dbt_dir, resource_dir, "docs.md")

    if args.backup and os.path.isfile(doc_file):
        os.rename(doc_file, doc_file[:len(doc_file) - 3] + "_" +
                  datetime.datetime.now().isoformat().replace(":", "-") +
                  ".md_")

    with open(doc_file, "w") as f:
        f.write("""# This file was auto-generated by dbtdocstr.
# Don't manually update.
# https://github.com/anelendata/dbt_docstring

""")
        if not doc_blocks:
            return
        for key in doc_blocks:
            f.write("{%% docs %s %%}\n" % key)
            f.write(doc_blocks[key] + "\n")
            f.write("{% enddocs %}\n\n")


def _run():
    dbt_dir = args.dbt_dir
    models_dirs, macro_dirs = _get_dirs(dbt_dir)

    for models_dir in models_dirs:
        _scan_models(os.path.join(dbt_dir, models_dir))

    for macro_dir in macro_dirs:
        _scan_macros(os.path.join(dbt_dir, macro_dir))


args = {}
def main():
    global args
    """
    Entry point
    """
    parser = argparse.ArgumentParser(COMMAND)

    parser.add_argument(
        "dbt_dir",
        type=str,
        help="dbt root directory")
    parser.add_argument(
        "-b",
        "--backup",
        action="store_true",
        help="When set, take a back up of existing schema.yml and docs.md")
    parser.add_argument(
        "-d","--doc",
        type=str,
        help="output doc file"
    )
    parser.add_argument(
        "-s","--schema",
        type=str,
        help="output schema file"
    )

    args = parser.parse_args()
    _run()


if __name__ == "__main__":
    main()
