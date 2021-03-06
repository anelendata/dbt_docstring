[![Build Status](https://travis-ci.com/daigotanaka/dbt_docstring.svg?branch=master)](https://travis-ci.com/daigotanaka/dbt_docstring)

# dbt_docstring

Docstring dbt test & documentation in SQL file

## What is it?

dbt has a test and documentation feature where models/schema.yml is the
definition file. While this is already a big help for testing and
documentation in ELT, not being able to keep documentation in the source code
may cause more documentats out of sync with the source.

dbtdocstr lets you write docment in a docstring style directly in .sql files.

## Install

```
pip install dbt_docstring
```

## How does it work?

dbtdocstr command scans .sql files under dbt's models directories and look for
a block that begins with ```` ```dbt```` and end with ```` ``` ````.
Inside the block you can write the content of the models section of schema.yml
corresponding to the current table as specified in
[dbt document](https://docs.getdbt.com/docs/building-a-dbt-project/documentation/):

Example (<dbt_root>/models/api_key_status.sql)
````
/*
# API key status

This table lists the API keys with the status.

```dbt
columns:
  - name: api_key
    description: API key
    tests:
      - unique
  - name: enabled
    description: True if API key is enabled status
  - name: update_datetime
    description: Last update date and time
```
*/
SELECT
   api_key,
   enabled,
   update_datetime
FROM {{ ref('my_api_key_list') }}
````

Then run:

```
dbtdocstr <dbt_project_root_directory>
```

These two files will be auto-generated from each .sql file in the dbt project:

`models/docs.md`:
```
# This file was auto-generated by dbtdocstr.
# Don't manually update.
# https://github.com/anelendata/dbt_docstring

{% docs api_key_status %}
# API key status

This table lists the API keys with the status.
{% enddocs %}
```

`models/schema.yml`:
```
# This file was auto-generated by dbtdocstr.
# Don't manually update.
# https://github.com/anelendata/dbt_docstring

version: 2
models:
  - name: api_key_status
    description: '{{ docs("api_key_status") }}'
    columns:
      - name: api_key
        description: API key
        tests:
          - unique
      - name: enabled
        description: True if API key is enabled status
      - name: update_datetime
        description: Last update date and time
  - name: ...
 ```

To see the document generation, use dbt command:

```
dbt docs generate
dbt docs serve
```

### Notes

- The doc must be a SQL comment block comment that begins with '/\*' and ends with '\*/'
- The first comment block will be extracted.
- The dbt block is searched within the first comment block.
- Any text after the dbt block will be ignored.
- dbt's Docs Blocks feature can be used only for table & view description. Not column descriptions.
- `dbtdocstr --backup <dbt_root_directory>` to create backup files of schema.yml and docs.yml if they exsit.

## Original repository

- https://github.com/anelendata/dbt_docstring

# About this project

This project is developed by
ANELEN and friends. Please check out the ANELEN's
[open innovation philosophy and other projects](https://anelen.co/open-source.html)

![ANELEN](https://avatars.githubusercontent.com/u/13533307?s=400&u=a0d24a7330d55ce6db695c5572faf8f490c63898&v=4)
---

Copyright &copy; 2020~ Anelen Co., LLC
