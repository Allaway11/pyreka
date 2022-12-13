import subprocess
from subprocess import CompletedProcess
import re
from typing import List, Literal
import typer
from rich.prompt import Prompt
from rich import print
from rich.console import Console

PATTERN = (
    """(def)\\s((.*?)\\((.*?)\\)):\n(\t|\\s{4}|\\s{2})+("|'){3}((.|\n|\t)*?)("|'){3}"""
)
SEPARATOR = "<SEP>"


def search_score(text: str, keywords: List[str]) -> float:
    """Score text using keywords - case is ignored."""
    count: int = 0
    text: str = text.lower()
    for keyword in keywords:
        count += 1 if text.find(keyword.lower()) > -1 else 0
    score: float = count / len(keywords)
    return score


def get_package_path(package_name: str) -> str:
    # TODO: Add error handling if the path is not found.
    result: CompletedProcess[bytes] = subprocess.run(
        [
            "python",
            "-c",
            f"import {package_name}; print({package_name}.__path__)",
        ],
        capture_output=True,
    )
    # TODO: write test if more than one location is found.
    package_path: str = "/" + result.stdout.decode("utf-8")[3:-3]
    return package_path


def get_functions_from_package_path(path: str) -> List[str]:
    grep_result: CompletedProcess[bytes] = subprocess.run(
        [
            "pcregrep",
            "-M",
            "-o1",
            "-o2",
            "-o3",
            "-o7",
            "--om-separator",
            SEPARATOR,
            "-r",
            "--include",
            ".py$",
            "-n",
            "-e",
            PATTERN,
            path,
        ],
        capture_output=True,
    )

    functions: List[str] = grep_result.stdout.decode("utf-8").splitlines()
    return format_functions(functions=functions, path=path)


def format_functions(functions: List[str], path: str) -> List[str]:
    start: Literal[0] = 0
    functions_processed: List = []
    for line_no, line in enumerate(functions):
        if line.startswith(path):
            if line_no != 0:
                functions_processed.append("\n".join(functions[start:line_no]))
                start = line_no
    return functions_processed


def create_function_dicts(function_strings: List[str]):
    function_pattern = re.compile("(^.*\.py):(\d*?):(\w*)")
    functions_store = []
    for function in function_strings:
        function_prefix, function_signature, function_name, docstring = function.split(
            SEPARATOR
        )
        match = function_pattern.match(function_prefix)
        file_name, line_number = match[1], match[2]
        functions_store.append(
            dict(
                file_name=file_name,
                function_name=function_name,
                function_signature=function_signature,
                docstring=docstring,
                line_number=line_number,
            )
        )
    return functions_store


def get_functions(path: str) -> List[dict]:
    functions: List[str] = get_functions_from_package_path(path)
    functions: List[dict] = create_function_dicts(functions)
    return functions


def score_function_search(functions: List[dict], search_terms: str):
    keywords: List[str] = search_terms.split()
    for function in functions:
        docstring_score: float = search_score(
            text=function["docstring"], keywords=keywords
        )
        function_name_score: float = search_score(
            text=function["function_name"], keywords=keywords
        )
        score = (docstring_score + function_name_score) / 2
        function["score"] = score
    functions = sorted(functions, key=lambda d: d["score"], reverse=True)
    return functions


def print_top_k_functions(functions: List[dict], k: int = 5):
    console = Console()
    for rank, function in enumerate(functions[:k], start=1):
        print(
            f"\n:inbox_tray: [bold italic green]Rank {rank} - {function['function_name']} - {function['score']*100:.1f}% match[/]"
        )
        print(f":link: {function['file_name']}")
        print(f":pushpin: LineNo: {function['line_number']}")
        print(f"\n:memo: {function['function_signature']}")
        # TODO: print 1st line of docstring
        print("\t" + function["docstring"].strip().split("\n")[0])

        res = typer.prompt(
            "Hit Enter to view docstring", default="^[[C", show_default=False
        )
        if res:
            with console.pager():
                console.print(f'{function["function_signature"]}:')
                console.print(f'{function["docstring"]}\n\n')
        Prompt.ask(
            ":fast_forward: Hit Enter to view next result :fast_forward:",
            default="\n",
            show_default=False,
        )


def main(
    package_name_or_path: str,
    search_terms: str,
    is_directory: bool = typer.Option(
        default=False, prompt="Are you searching in a directory?"
    ),
):
    if is_directory:
        search_path = package_name_or_path
    else:
        search_path: str = get_package_path(package_name=package_name_or_path)
    functions: List[dict] = get_functions(path=search_path)
    functions: List[dict] = score_function_search(
        functions=functions, search_terms=search_terms
    )
    print_top_k_functions(functions=functions)


if __name__ == "__main__":
    typer.run(main)
