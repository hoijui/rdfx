import argparse
import os
import sys
from pathlib import Path
from typing import List

import rdflib
from rdflib import Graph, util

from rdfx.constants import RDF_FILE_ENDINGS, OUTPUT_FILE_ENDINGS
from rdfx.persistence_systems import File, PersistenceSystem, prepare_files_list

def get_input_format(file_path):
    input_format = util.guess_format(str(file_path))
    if input_format is None:
        str_path = str(file_path)
        if str_path.endswith("json-ld") or str_path.endswith("jsonld"):
            input_format = "json-ld"
        else:
            raise Exception(
                f"ERROR: Cannot guess the RDF format of input file {file_path}"
            )

    return input_format


def make_output_file_path(input_file_path, input_format, output_format, in_place):
    output_file_name = input_file_path.name.split(".")[:-1][0]

    if input_format == output_format and not in_place:
        output_file_name += ".new"

    output_file_name = output_file_name + "." + OUTPUT_FILE_ENDINGS.get(output_format)

    output_path = input_file_path.parent / output_file_name
    print(f"output file: {output_path}")
    return output_path


def convert(
    input_file_path: Path,
    persistence_system,
    output_filename: str,
    output_format: str,
    comments: str = None,
):
    input_format = get_input_format(input_file_path)
    output_file_path = input_file_path.parent
    g = Graph().parse(str(input_file_path), format=input_format)
    persistence_system.write(g, output_filename, output_format, comments,output_file_path)


def merge(
    rdf_files: List[Path],
    persistence_system,
    output_format,
    output_filename,
    leading_comments=None,
):
    """
    Merges a given set of RDF files into one graph

    """
    for f in rdf_files:
        if not f.name.endswith(tuple(RDF_FILE_ENDINGS.keys())):
            raise ValueError(
                f"Files to be merged must have a known RDF suffix (one of {', '.join(RDF_FILE_ENDINGS)})"
            )

    g = Graph()
    for f in rdf_files:
        g.parse(f, format=RDF_FILE_ENDINGS[f.suffix.lstrip(".")])
    persistence_system.write(g, output_filename, output_format, leading_comments)


def persist_to(persistence_system: PersistenceSystem, g: Graph):
    if not issubclass(type(persistence_system), PersistenceSystem):
        raise ValueError(
            "You must select one of the subclasses of PersistenceSystem to use for the persistence_system argument"
        )
    persistence_system.write(g)

def get_leading_comments(input_file_path:Path):
    """
    Returns a list of all leading comments in the file.
    """

    comments_list = []
    comment_flag = False
    with open(input_file_path, "r", encoding='utf-8', errors='ignore') as f:
        for index, line in enumerate(f):
            if len(line.strip()) > 0 and line.strip()[0] == '#' and index == 0:
                comments_list.append(line.strip()[2:])
                comment_flag = True

            elif len(line.strip()) > 0 and line.strip()[0] == '#' and comment_flag:
                comments_list.append(line.strip()[2:])

            elif len(line.strip()) > 0 and line.strip()[0] != '#':
                comment_flag = False

            elif not comment_flag:
                break

    return comments_list

def get_sorted_namespaces(g:Graph):
    """
    Extracts the list of used name-spaces from the grah,
    in sorted order.
    """

    all_ns = list(g.namespaces())
    subjects = list(g.subjects())
    predicates = list(g.predicates())
    objects = list(g.objects())
    all_prefixes = set(subjects + predicates + objects)
    used_namespace = []
    for full_prefix in all_prefixes:
        for prefix in all_ns:
            if prefix[1] in full_prefix:
                used_namespace.append(prefix)

    used_namespace = list(set(used_namespace))
    used_namespace.sort(key=lambda tup: tup[0])

    return used_namespace

def clean_ttl(input_file_path:Path):
    """
    Removes unused namespace entries
    and re-serializes a graph
    with the prefixes in sorted order.
    """

    comments_list = get_leading_comments(input_file_path)

    g = Graph()
    g.parse(input_file_path)
    used_namespace = get_sorted_namespaces(g)
    f = rdflib.Graph()
    for name in used_namespace:
        f.bind(name[0], name[1])

    for s, p, o in g:
        f.add((s, p, o))
    os.remove(input_file_path)
    input_file_path = Path(input_file_path)
    ps = File(directory=input_file_path.parent)
    if len(comments_list) > 0:
        ps.write(g=g, filename=input_file_path.stem, leading_comments=comments_list)
    else:
        ps.write(g=g, filename=input_file_path.stem)

def main():
    if "-h" not in sys.argv and "--help" not in sys.argv and len(sys.argv) < 3:
        print(
            "ERROR: You must supply at a minimum the method (convert, merge or clean), a file or files, and a target format"
        )
        return 1

    parser = argparse.ArgumentParser()

    parser.add_argument("method", choices=("convert", "merge", "clean"))

    parser.add_argument(
        "data",
        nargs="+",
        type=str,
        help="Path to the RDF file or directory of files for merging or conversion.",
    )

    parser.add_argument(
        "--format",
        "-f",
        type=str,
        help="The RDFlib token for the RDF format you want to convert the RDF file to.",
        choices=RDF_FILE_ENDINGS.keys(),
    )

    parser.add_argument(
        "-o",
        "--output",
        help="if set, the output location for merged or converted files, defaults to the current working directory",
        type=str,
    )

    parser.add_argument(
        "--comments", type=str, help="Comments to prepend to the RDF, turtle only."
    )

    args = parser.parse_args()

    if args.output:
        output_loc = Path(args.output)
    else:
        output_loc = Path(os.getcwd())

    if args.method == "merge":
        files_list = prepare_files_list(args.data)
        ps = File(directory=output_loc)
        merge(files_list, ps, args.format, "merged", args.comments)

    if args.method == "convert":
        ps = File(directory=output_loc)
        rdf_format = args.format
        leading_comments = args.comments
        files_list = prepare_files_list(args.data)
        for file in files_list:
            output_filename = Path(file).stem
            convert(file, ps, output_filename, rdf_format, leading_comments)

    if args.method == "clean":
        files_list = prepare_files_list(args.data)
        for file in files_list:
            clean_ttl(file)

    return 0

if __name__ == "__main__":
    sys.exit(main())
