#!/usr/bin/env python3
#
# lobster_cpp - Extract C/C++ tracing tags for LOBSTER
# Copyright (C) 2023 Bayerische Motoren Werke Aktiengesellschaft (BMW AG)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program. If not, see
# <https://www.gnu.org/licenses/>.
import json
import sys
import argparse
import os.path

from lobster.items import Tracing_Tag, Implementation
from lobster.location import File_Reference
from lobster.io import lobster_write
from lobster.tools.cpp_parser.parser.requirements_parser import ParserForRequirements, SUPPORTED_REQUIREMENTS


def parse_cpp_config_file(file_name):
    assert isinstance(file_name, str)
    assert os.path.isfile(file_name)

    with open(file_name, "r") as file:
        data = json.loads(file.read())

        provided_config_keys = set(data.keys())
        supported_references = set(SUPPORTED_REQUIREMENTS)

        if not provided_config_keys.issubset(supported_references):
            raise Exception("The provided requirement types are not supported! "
                  "supported requirement types: '%s'" % ', '.join(SUPPORTED_REQUIREMENTS))
        return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files",
                    nargs="+",
                    metavar="FILE|DIR")
    ap.add_argument("--config-file",
                    help="path of the config file, it consists of "
                         "a requirement types as keys and "
                         "output filenames as value",
                    default=None)

    options = ap.parse_args()

    if options.config_file:
        if os.path.isfile(options.config_file):
            cpp_output_config = parse_cpp_config_file(options.config_file)
        else:
            ap.error("cannot open config file '%s'" % options.config_file)

    file_list = []
    for item in options.files:
        if os.path.isfile(item):
            file_list.append(item)
        elif os.path.isdir(item):
            for path, _, files in os.walk(item):
                for filename in files:
                    _, ext = os.path.splitext(filename)
                    # if ext in (".cpp", ".cc", ".c", ".h"):
                    if ext in [".cpp"]:
                        file_list.append(os.path.join(path, filename))
        else:
            ap.error("%s is not a file or directory" % item)

    prefix = os.getcwd()

    for requirement_type in cpp_output_config.keys():

        parser = ParserForRequirements()
        requirement_details = parser.fetch_requirement_details_for_test_files(test_files=file_list,
                                                                              requirement_type=requirement_type)

        db = {}

        for requirement_detail in requirement_details:
            # get requirement detail properties delivered from parser
            tracking_id: str = requirement_detail.get('tracking_id')
            function_name: str = requirement_detail.get('component')
            test_desc: str = requirement_detail.get('test_desc')
            file_name_with_line_number: str = requirement_detail.get('file_name')

            # convert into fitting parameters for Implementation
            file_name, line_nr = file_name_with_line_number.split("#L")
            filename = os.path.relpath(file_name, prefix)
            line_nr = int(line_nr)
            function_uid = "%s:%s:%u" % (os.path.basename(filename),
                                         function_name,
                                         line_nr)
            tag = Tracing_Tag("cpp", function_uid)
            loc = File_Reference(filename, line_nr)
            kind = 'Function'
            ref = tracking_id.replace("CB-#", "")

            if ref == '2957143':
                pass

            if tag.key() not in db:
                db[tag.key()] = Implementation(
                    tag      = tag,
                    location = loc,
                    language = "C/C++",
                    kind     = kind,
                    name     = function_name)
            if 'Missing' not in ref:
                db[tag.key()].add_tracing_target(Tracing_Tag("req", ref))

        if cpp_output_config.get(requirement_type):
            with open(cpp_output_config.get(requirement_type), "w", encoding="UTF-8") as fd:
                lobster_write(fd, Implementation, "lobster_cpp_parser", db.values())
            print("Written output for %u items to %s" % (len(db), cpp_output_config.get(requirement_type)))

        else:
            lobster_write(sys.stdout, Implementation, "lobster_cpp_parser", db.values())
            print()


if __name__ == "__main__":
    sys.exit(main())
