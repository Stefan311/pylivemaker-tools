# BSD 2-Clause License
#
# Copyright (c) 2020, Stefan Berndt (stefan.berndt@imoriath.com)
#
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""pylivemaker string extraction tool"""

import sys
import csv
from pathlib import Path

import click
from livemaker.lsb import LMScript
from livemaker.lsb.command import CommandType
from livemaker.exceptions import LiveMakerException


@click.command()
@click.argument("lsb_file", required=True, type=click.Path(exists=True, dir_okay="False"))
@click.argument("csv_file", required=True, type=click.Path(exists=False, dir_okay="False"))
@click.option(
    "-e",
    "--encoding",
    type=click.Choice(["cp932", "utf-8", "utf-8-sig"]),
    default="utf-8",
    help="Output text encoding (defaults to utf-8).",
)
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing csv file.")
@click.option("--append", is_flag=True, default=False, help="Append text data to existing csv file.")
def extract_strings(lsb_file, csv_file, encoding, overwrite, append):
    """Extract strings from the given LSB file to a CSV file.

    You can open this CSV file for translation in most spreadsheet programs (Excel, Open/Libre Office Calc, etc).
    Just remember to choose comma as delimiter and " as quotechar.

    NOTE: If you are using Excel and UTF-8 text, you must also specify --encoding=utf-8-sig, since Excel requires
    UTF-8 with BOM to handle UTF-8 properly.

    You can use the --append option to add the text data from this lsb file to a existing csv.
    With the --overwrite option an existing csv will be overwritten without warning.

    NOTE: this program also extracts strings used in menu functions. DO NOT USE this function for translating menu items.
    The menu will not work!

    NOTE: be very careful with translating strings. Changing the wrong text can break game functionality!
    Lines you would not translate have to be left blank.
    """
    with open(lsb_file, "rb") as f:
        try:
            lsb:LMScript = LMScript.from_file(f)
        except LiveMakerException as e:
            sys.exit("Could not open LSB file: {}".format(e))

    csv_data = []

    for c in lsb.commands:
        calc = c.get("Calc")
        if calc:
            for s in calc["entries"]:
                op = s["operands"][0]
                if op["type"] == "Str":
                    csv_data.append(["pylm:string:{}:{}:{}".format(lsb_file, c.LineNo, s["name"]), None, c, op["value"]])

    if len(csv_data) == 0:
        sys.exit("No strings found.")

    if Path(csv_file).exists():
        if not overwrite and not append:
            sys.exit("File {} already exists. Please use --overwrite or --append option.".format(csv_file))
    elif append:
        print("File {} does not exist, but --append specified. A new file will be created.".format(csv_file))
        append = False

    with open(csv_file, ("a" if append else "w"), newline="\n", encoding=encoding) as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        if not append:
            csv_writer.writerow(["ID", "Label", "Context", "Original text", "Translated text"])
        for row in csv_data:
            csv_writer.writerow(row)

    print(f"Extracted {len(csv_data)} strings.")


if __name__ == "__main__":
    extract_strings()
