# Grading tools

Some tools I use when grading [Canvas](https://www.instructure.com/canvas)
assignments.

There are command line tools, and some utilities for working with Canvas outputs.

The main use is when doing by-hand grading of assignments with multiple components, and you want to keep track of the scores per component, with notes from grading.

To do this, I make a Markdown marking log file, with specifications at the top,
then one second-level heading per student, like this:

```
# 2018 Marking log for assessment Foo

Ordinary maxima:

* quality: 20
* does_task: 15
* skill_range: 10
* elegance: 10
* functions_variables: 10
* display: 10
* usable: 15
* comments_safety: 10

Total: 100

## mbr110

* quality: 14.0
* does_task: 11.0
* skill_range: 7.0
* elegance: 6.0
* functions_variables: 7.0
* display: 8.0
* usable: 10.0
* comments_safety: 8.0

Total: 71

Martin Brett

You did a good job generally.  Etc.  More comments on specifics.

## vrr101

* quality: 5.0
* does_task: 6.0
* skill_range: 3.0
* elegance: 2.0
* functions_variables: 3.0
* display: 4.0
* usable: 5.0
* comments_safety: 3.0

Total: 55.0

Valia Rodriguez Rodriguez

You did not do a very good job, generally.  Etc.
```

## Command line tools

Commands need a file `gdconfig.toml` in the current directory.

Example:

```
log = "markingb_log.md"
year = "2018"
assignment = "Data Analysis Due (000000)"

[fudges]
2018 = 10
```

* gdo-check : analyzes a marking log in Markdown, with headings per student,
  and sub-totals for component.  Checks sub-totals match specification at top
  of file, checks and prints totals per student.
* gdo-year : prints "year" field value from config file (above).
* gdo-mkstable : makes template CSV file to upload to Canvas, using exported
  CSV file from Canvas as input.
* gdo-stinit : makes section in marking log for student with specified login.
  If field `nb_template` exists in config file, make matching notebook for
  student.
* gdo-mkfb : splits marking log into one file per student, builds PDFs for each
  student.
* gdo-report : write marks CSV from report.

## Utilities

* `canvastools` - various utilities for interpreting Canvas output filenames,
  reading Canvas output CSV files.

## Installation, development

Install from pip, usually:

```
pip install gradools
```

To install locally from the repository, you will need [flit](https://pypi.org/project/flit).


```
flit install --user
```

For development I use:

```
flit install --user -s
```

Test with:

```
pip install -r test-requirements.txt
pytest gradools
```
