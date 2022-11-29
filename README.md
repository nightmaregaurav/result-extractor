# Result Extractor

---
## Description
This tool is used to extract the results of individual campus from a given file that lists the results of multiple campus as a global merit list. This tool was primarily made for the purpose of extracting the results of individual campus from the global merit list of the `BCA TU Entrance Examination` taken by [TUFOHSS](https://www.tufohss.edu.np).

## Scenario

[TUFOHSS](https://www.tufohss.edu.np) publishes the results of the `BCA TU Entrance Examination` in the form of a global merit list. This list contains the results of all the campuses. This tool is used to extract the results of individual campus from the global merit list. THis tool may be useful for similar scenario.
* The global merit list is in the form of a `.txt` file.
* The global merit list contains the results of all the campuses.
* The merit list contains the following information:
    * Symbol Number
* The Symbol Number is unique for each candidate.
* The Symbol Numbers are line separated.
* The Symbol Numbers are sorted in the descending order of the total marks.
* The Symbol Number contains a unique campus code that can be extracted using a regular expression.

## Prerequisites
* Regular Expression to extract the campus code from the Symbol Number.
* client_secrets.json file for Google Drive API. (Help for this is provided in the client_secrets.json.readme file)
* Input file containing the Symbol Numbers of the global merit list.
* Update/Change Campus.db to match campus code, name, and address to match your scenario. Default sample contains TU-BCA campuses as of 2022-Nov.

## Setup
* Clone the repository.
* Create a python virtual environment and switch to it.
* Install the requirements using `pip install -r requirements.txt`.
* Create a client_secrets.json file for Google Drive API if you want to upload results in Google Drive. (Help for this is provided in the client_secrets.json.readme file)

## Usage
* Run the `main.py` file.
* Enter the Result Name `[e.g. BCA TU Entrance Examination]` `(Default: Result)`.
* Enter the input file name `[e.g. result.txt]` `(Default: IN.txt)`.
* Enter the Regular Expression to extract the campus code from the Symbol Number `[e.g. ^[0-9]{2}]` `(Default: ^(\d+)-.+$)`.
* Choose whether to upload the results in Google Drive or not with `[Y/N]` `(Default: N)`.
* Wait till the program finishes it's magic.

## Output
* The output will be stored in a folder with name `Publish-<result_name>-<timestamp>`
* Inside the folder, there will be a files and folders:
  * htmls ~ Folder: html files for result each campus.
  * pdfs ~ Folder: pdf files for result each campus.
  * images ~ Folder: Folders of images of the result for each campus.
  * summary ~ Folder: Images of Summary of the result.
  * result.db ~ File: SQLite database file containing the result and summary.
  * summary.html ~ File: html file containing the summary of the result.
  * summary.pdf ~ File: pdf file containing the summary of the result.

## How to Contribute
* Fork the repository
* Clone the forked repository
* Make changes
* Commit and push the changes
* Create a pull request
* Wait for the pull request to be merged
* Celebrate
* Repeat

*If you are new to open source, you can read [this](https://opensource.guide/how-to-contribute/) to learn how to contribute to open source projects.*<br>
*If you are new to GitHub, you can read [this](https://guides.github.com/activities/hello-world/) to learn how to use GitHub.*<br>
*If you are new to Git, you can read [this](https://www.atlassian.com/git/tutorials/learn-git-with-bitbucket-cloud) to learn how to use Git.*<br>
*If you are new to Python, you can read [this](https://www.python.org/about/gettingstarted/) to learn how to use Python.*<br>

---
## Note: This Project is Licensed under GNU GPLv3.

### Which means Anyone are permitted for:
- Commercial use: **The licensed material and derivatives may be used for commercial purposes.**
- Distribution: **The licensed material may be distributed.**
- Modification: **The licensed material may be modified.**
- Patent use: **This license provides an express grant of patent rights from contributors.**
- Private use **The licensed material may be used and modified in private.**

### Under Condition that:
- Disclose source: **Source code must be made available when the licensed material is distributed.**
- License and copyright notice: **A copy of the license and copyright notice must be included with the licensed material.**
- Same license: **Modifications must be released under the same license when distributing the licensed material. In some cases a similar or related license may be used.**
- State changes: **Changes made to the licensed material must be documented. Along with link to original source**

---
Open For Contribution
---
