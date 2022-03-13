#!/usr/bin/env python3
"""CLI to fetch basic tech info from builtwith.com"""
import argparse
import json
import sys
import re
from bs4 import BeautifulSoup as bs4
from colorama import Fore, Style
import requests

user_agent: str = "User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0"
domain_reg: re.Pattern = re.compile(r'^(?!:\/\/)([a-zA-Z0-9-_]+\.)*[a-zA-Z0-9][a-zA-Z0-9-_]+\.[a-zA-Z]{2,11}?$')


def fmt_url(url: str) -> str:
    """Extract domain from URL

    Args:
        url (str): URL

    Returns:
        str: Extracted domain
    """
    if "://" in url:
        url = url.split("://")[1]
    if "/" in url:
        url = url.split("/")[0]
    if domain_reg.match(url):
        return url
    print("[i] URL has unknown format.")
    sys.exit(1)


def fetch_tech(url: str) -> dict:
    """Fetch basic information from builtwith.com

    Args:
        url (str): URL to fetch information for

    Returns:
        dict: result as json
    """
    data = {"Technology Profile": {}}
    url = "https://builtwith.com/" + fmt_url(url)
    res = requests.get(url, headers={"User-Agent": user_agent})
    soup = bs4(res.text, "lxml")
    cards = soup.findAll(class_="card mt-4 mb-2")
    for card in cards:
        card_title = card.find(class_="card-title").text
        text_dark = card.findAll(class_="text-dark")
        descriptions = card.findAll(class_="pb-0 mb-0 small")
        data["Technology Profile"][card_title] = {}
        for text, descr in zip(text_dark, descriptions):
            data["Technology Profile"][card_title][text.text] = descr.text
    return data


def colorize_data(data: dict | list, url: str) -> None:
    """Print formatted results with colors

    Args:
        data (dict | list): results
        url (str): url
    """
    if isinstance(data, dict):
        data = [data]
    for entry in data:
        profile = list(entry.keys())[0]
        print(f"Fetched information from {profile} for {fmt_url(url)}")
        for card in entry[profile]:
            print("\n" + Style.BRIGHT + ">>> " + Style.RESET_ALL +
                  Fore.LIGHTCYAN_EX + card + Fore.RESET)
            for technique in entry[profile][card]:
                print(Fore.LIGHTGREEN_EX + technique + Fore.RESET)
                print(entry[profile][card][technique])


def main():
    """Entry point, parse args and init according actions
    """
    # Init argument parser
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("-o", "--output", required=False, default="stdout",
                    type=str, help="Output format of your data. Either 'stdout' or 'json'")
    argument_parser.add_argument("-u", "--url", required=False, type=str,
                    help="URL to fetch information for")
    argument_parser.add_argument("--colorize", required=False, type=str,
                    help="Colorize already stored results.")
    # Parse args
    args = argument_parser.parse_args()
    # Colorize file if option was selected
    if args.colorize:
        try:
            with open(args.colorize, 'r', encoding="utf-8") as json_file:
                data = json.load(json_file)
                url = '.'.join(args.colorize.split("_")[-1].split(".")[:-1])
            colorize_data(data, url)
        except FileNotFoundError:
            print(f"[!] Could not find file {args.colorize}")
            sys.exit(1)
        sys.exit(0)
    # Quit if no URL was supplied
    if not args.url:
        print("[!] No URL supplied!")
        argument_parser.print_help()
        sys.exit(1)
    # Fetch data for URL
    data = fetch_tech(args.url)
    # Print formatted and colored results
    if args.output == "stdout":
        colorize_data(data, args.url)
    # or export data as JSON
    elif args.output == "json":
        fname = "bw_" + fmt_url(args.url) + ".json"
        print(f"[i] Results stored in '{fname}'.")
        with open(fname, 'w', encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4)
    else:
        print("[!] Output can only be 'stdout' or 'json'.")
        sys.exit(1)


if __name__ == "__main__":
    print(
        f"     __              ___        ___        {Fore.RED}__{Fore.RESET}   __        ")
    print(
        f"    |__) |  | {Fore.RED}|{Fore.RESET} {Fore.RED}|{Fore.RESET}     |  |  | |  |  |__|  "
        f"{Fore.RED}/  `{Fore.RESET} /  \  |\/| ")
    print(
        f"    |__) \__/ {Fore.RED}|{Fore.RESET} {Fore.RED}|___{Fore.RESET}  |  |/\| |  |  |  | "
        f".{Fore.RED}\__,{Fore.RESET} \__/  |  | ")
    print("    (c) 2022 - Jakob Schaffarczyk\n")
    main()
