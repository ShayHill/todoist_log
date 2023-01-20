#!python
"""Print a log of completed Todoist tasks for one day.

:author: Shay Hill
:created: 2023-01-20
"""


import argparse
import datetime
import itertools
import json
import time

import requests
from paragraphs import par
from requests.structures import CaseInsensitiveDict


def _new_headers(api_token: str) -> CaseInsensitiveDict[str]:
    """Create a new headers dictionary for requests to the Todoist sync API.

    :param api_token: The API token for the Todoist account.
    :return: A dictionary of headers for requests to the Todoist sync API.
    """
    headers: CaseInsensitiveDict[str] = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    headers["Authorization"] = "Bearer " + api_token
    return headers


def _print_completed_tasks(
    headers: CaseInsensitiveDict[str], date: datetime.date
) -> bool:
    """Print [completed_at project section task] for each completed task for one day.

    :param headers: The headers for requests to the Todoist sync API.
    :param date: The date for which to print completed tasks.
    :return: True if succeeded, False if failed.
    :raise ValueError: if the API token is invalid. Prints and returns False for any
        other Exception.
    """
    since = date.strftime("%Y-%m-%dT00:00:00")
    until = date.strftime("%Y-%m-%dT23:59:59")
    task_lines: list[list[str]] = []

    for offset in (x * 200 for x in itertools.count()):
        try:
            resp = requests.post(
                "https://api.todoist.com/sync/v9/completed/get_all",
                headers=headers,
                data=json.dumps({"since": since, "until": until, "offset": offset}),
            )
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            if "403 Client Error: Forbidden" in str(e):
                raise ValueError("Invalid API token") from e
            print(f"Failed to reach Todoist: {e}")
            return False

        resp_json = resp.json()
        if not resp_json["items"]:
            break
        for task in resp_json["items"]:
            project_id = task.get("project_id")
            section_id = task.get("section_id")
            completed_at = str(task.get("completed_at"))
            project = str(resp_json["projects"].get(project_id, {}).get("name"))
            section = str(resp_json["sections"].get(section_id, {}).get("name"))
            content = str(task.get("content"))
            task_lines.append([completed_at, project, section, content])

    for task_line in sorted(task_lines):
        print("\t".join(task_line))
    if not task_lines:

        print(f"No\ttasks\tcompleted\t{_get_yymmdd_from_date(date)}")
    return True


def _get_date_from_yymmdd(yymmdd: str) -> datetime.date:
    """Return a date from a string in YYMMDD format.

    :param yymmdd: a string in YYMMDD format
    :return: a date
    """
    return datetime.datetime.strptime(yymmdd, "%y%m%d").date()


def _get_yymmdd_from_date(date: datetime.date | datetime.datetime) -> str:
    """Return a YYMMDD string from a date.

    :param date: a datetime.date or datetime.datetime instance
    :return: a string in YYMMDD format
    """
    return date.strftime("%y%m%d")


def _get_parser() -> argparse.ArgumentParser:
    """Return an argument parser for this script.

    :return: an argument parser for `python log_completed_tasks.py ...`
    """
    parser = argparse.ArgumentParser(
        description="Task completion log for Todoist",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _ = parser.add_argument(
        "-a", "--api-token", help="REQUIRED: your Todoist API token.", type=str
    )
    _ = parser.add_argument(
        "-d",
        "--date",
        help="Format YYMMDD. The day to log. Default is yesterday.",
        type=str,
        default="None",
    )
    _ = parser.add_argument(
        "-r",
        "--retries",
        help=par(
            """Limit the number of retries if the script fails for any reason EXCEPT
            an invalid API token. Default behaviour is to try until the script
            succeeds or you force quit the script (ctrl-c)."""
        ),
        type=int,
        default=-1,
    )
    return parser


def main():
    """Main function."""
    parser = _get_parser()
    args = parser.parse_args()

    if not args.api_token:
        parser.print_help()
        return

    if args.date == "None":
        date = datetime.date.today() - datetime.timedelta(days=1)
    else:
        date = _get_date_from_yymmdd(args.date)

    if args.retries < 0:
        attempts = itertools.count()
    else:
        attempts = range(args.retries + 1)

    headers = _new_headers(args.api_token)

    for _ in attempts:
        success = _print_completed_tasks(headers, date)
        if success:
            break
        print("failed to get completed tasks. trying again in 5 seconds...")
        time.sleep(5)


if __name__ == "__main__":
    main()
