# Todoist-log

Task completion log for Todoist

    -h, --help            show this help message and exit

    -a API_TOKEN, --api-token API_TOKEN
                          REQUIRED: your Todoist API token.

    -d DATE, --date DATE  Format YYMMDD. The day to log. Default is yesterday.

    -r RETRIES, --retries RETRIES
                          Limit the number of retries if the script fails for
                          any reason EXCEPT an invalid API token.  Default
                          behaviour is to try until the script succeeds or you
                          force quit the script (ctrl-c).

# Example

    python todoist-log -a <YOUR-API-TOKEN>

Will print a tab-delimited line (time, project, section, task) for each task completed yesterday.

    python todoist-log -a <YOUR-API-TOKEN> -d 230101

Will print a tab-delimited line (time, project, section, task) for each task completed New Year's Day 2023.

To capture this data in a text file

    python todoist-log -a <YOUR-API-TOKEN> > my_file.txt

If no tasks were completed on the requested day, the script will print "no`\t`tasks`\t`completed`\t`*datestring*". This will keep your columns lined up if you plan to open the exported text as a spreadsheet.

# Installation

You will not install this script, but you will need to install [Python](https://www.python.org/) >=3.10. Life will be easier if you also install [git](https://git-scm.com/downloads).

    git clone https://github.com/ShayHill/todoist_log
    cd todoist_log
    python -m venv venv
    venv/Scripts/activate
    pip install -r requirements.txt
    python todoist-log -a <YOUR-API-TOKEN> -d 230120 -r 5

# What is my API token?

From the Todoist website, click Profile > Integrations > Developer to find your API token.
