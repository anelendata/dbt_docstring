#!/usr/bin/env python3
import argparse, datetime, logging, os, sys
from textwrap import indent
import yaml

logger = logging.getLogger(__name__)

COMMAND = "dbt_docstring"
DBT_BLOCK_START_KEY = "```dbt"


def _get_models_dirs(dbt_dir):
    dbt_project_file = os.path.join(dbt_dir, "dbt_project.yml")
    if not os.path.isfile(dbt_project_file):
        print("dbt_project.yml not found in {}".format(dbt_dir))
        exit(1)
    with open(dbt_project_file, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config["source-paths"]


def _read_dbt_block(sql_file):
    with open(sql_file, "r") as f:
        sql = f.read()
    doc_start = sql.find("/*")
    doc_end = sql.find("*/")
    doc = sql[doc_start + 2:doc_end] if doc_start > -1 else ""

    if not doc:
        return None

    dbt_start = doc.find(DBT_BLOCK_START_KEY)
    dbt_end = doc.find("```", dbt_start + len(DBT_BLOCK_START_KEY))

    dbt_block = ""
    if dbt_start > -1:
        dbt_block = doc[dbt_start + len(DBT_BLOCK_START_KEY):dbt_end]

    return dbt_block


def _scan_models(models_dir):
    if not os.path.isdir(models_dir):
        logger.warning("%s directory not found" % models_dir)
        return

    dbt_blocks = dict()
    models_dirs = os.walk(models_dir)
    for cdir, dirs, files in models_dirs:
        for fname in files:
            # Parse the table name from the SQL file name
            if fname[-3:] != "sql":
                logger.info("Skipping non-sql file: " + fname)
                continue
            tname = fname[0:-4]
            dbt_block= _read_dbt_block(os.path.join(cdir, fname))
            if dbt_block:
                dbt_blocks[tname] = dbt_block

    return dbt_blocks


def _run(dbt_dir, backup=False):
    models_dirs = _get_models_dirs(dbt_dir)
    for models_dir in models_dirs:
        schema_file = os.path.join(dbt_dir, models_dir, "schema.yml")

        if backup and os.path.isfile(schema_file):
            os.rename(schema_file, schema_file[:len(schema_file) - 4] + "_" +
                      datetime.datetime.now().isoformat().replace(":", "-") +
                      ".yml")

        dbt_blocks = _scan_models(os.path.join(dbt_dir, models_dir))
        with open(schema_file, "w") as f:
            f.write("version: 2\nmodels:\n")
            for key in dbt_blocks:
                f.write(indent(dbt_blocks[key], " " * 2) + "\n")


def main():
    """
    Entry point
    """
    parser = argparse.ArgumentParser(COMMAND)

    parser.add_argument(
        "dbt_dir",
        type=str,
        help="dbt root directory")

    args = parser.parse_args()

    _run(args.dbt_dir)


if __name__ == "__main__":
    main()
