[![Build Status](https://travis-ci.com/daigotanaka/dbt_docstring.svg?branch=master)](https://travis-ci.com/daigotanaka/dbt_docstring)

# dbt_docstring

Docstring dbt test & documentation in SQL file

## What is it

dbt has a test and documentation feature where models/schema.yml is the
definition file. While this is already a big help for SQL test and
documentation, not keeping the documentation in a separate file may cause
a lot of documentation sections not updated with the code.

dbtdocstr command scans .sql files under dbt's models directories and look for
a block that begins with "```dbt" and end with "```".
Inside the block you can write the content of the models section of schema.yml
corresponding to the current table as specified in
[dbt document](https://docs.getdbt.com/docs/building-a-dbt-project/documentation/):

Example:
```
- name: api_keys_status
  description: API key status
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

Then run:

```
dbtdocstr <dbt_project_root_directory>
```

`models/schema.yml` is auto-generated from each .sql file in the dbt project.

To see the document generation, use dbt command:

```
dbt docs generate
dbt docs serve
```

## Original repository

- https://github.com/daigotanaka/dbt_docstring

---

Copyright &copy; 2020 Anelen Co., LLC
