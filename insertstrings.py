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
import shutil
import sys
import csv
from pathlib import Path

import click
from livemaker.lsb import LMScript
from livemaker.lsb.command import CommandType
from livemaker.exceptions import LiveMakerException


@click.command()
@click.argument("lsb_file", required=True, type=click.Path(exists=True, dir_okay="False"))
@click.argument("csv_file", required=True, type=click.Path(exists=True, dir_okay="False"))
@click.option(
    "-e",
    "--encoding",
    type=click.Choice(["cp932", "utf-8", "utf-8-sig"]),
    default="utf-8",
    help="Input text encoding (defaults to utf-8).",
)
@click.option("--no-backup", is_flag=True, default=False, help="Do not generate backup of original lsb file.")
def insert_strings(lsb_file, csv_file, encoding, no_backup):
    """Insert strings from the given CSV file to a given LSB file.

    CSV_FILE should be a file previously created by the extractstrings command, with added translations.
    --encoding option must match the values were used for extractstrings.

    The original LSB file will be backed up to <lsb_file>.bak unless the --no-backup option is specified.

    NOTE: be very careful with translating strings. Changing the wrong text can break game functionality!
    Lines you would not translate have to be left blank.
    """
    lsb_file = Path(lsb_file)
    print("Patching {} ...".format(lsb_file))

    with open(lsb_file, "rb") as f:
        try:
            lsb: LMScript = LMScript.from_file(f)
        except LiveMakerException as e:
            sys.exit("Could not open LSB file: {}".format(e))

    csv_data = []

    with open(csv_file, newline="\n", encoding=encoding) as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=",", quotechar='"')
        for row in csv_reader:
            csv_data.append(row)

    translated = 0

    for c in lsb.commands:
        calc = c.get("Calc")
        if calc:
            for s in calc["entries"]:
                op = s["operands"][0]
                if op["type"] == "Str":
                    for line in csv_data:
                        if len(line) < 4: continue
                        if line[3] == "": continue
                        if line[4] == "": continue
                        if line[0] == "pylm:string:{}:{}:{}".format(lsb_file, c.LineNo, s["name"]):
                            op.value = line[4]
                            translated += 1

    if not translated:
        return

    if not no_backup:
        print("Backing up original LSB.")
        shutil.copyfile(str(lsb_file), "{}.bak".format(str(lsb_file)))
    try:
        new_lsb_data = lsb.to_lsb()
        with open(lsb_file, "wb") as f:
            f.write(new_lsb_data)
        print("Wrote new LSB.")
    except LiveMakerException as e:
        sys.exit("Could not generate new LSB file: {}".format(e))


if __name__ == "__main__":
    insert_strings()
