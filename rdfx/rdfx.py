import sys
from os import path
import glob
from rdflib import Graph, util
import argparse
from pathlib import Path
import json
from persistence_systems import *

RDF_FILE_ENDINGS = {
    "ttl": "turtle",
    "turtle": "turtle",
    "json": "json-ld",
    "json-ld": "json-ld",
    "jsonld": "json-ld",
    "owl": "xml",
    "xml": "xml",
    "rdf": "xml",
    "nt": "nt",
    "n3": "n3",
}

OUTPUT_FILE_ENDINGS = {
    "turtle": "ttl",
    "xml": "xml",
    "json-ld": "json-ld",
    "nt": "nt",
    "n3": "n3",
}


def get_input_format(file_path):
    input_format = util.guess_format(str(file_path))
    if input_format is None:
        str_path = str(file_path)
        if (
            str_path.endswith("json-ld")
            or str_path.endswith("jsonld")
        ):
            input_format = "json-ld"
        else:
            raise Exception(
                "ERROR: Cannot guess the RDF format of input file {}".format(file_path)
            )

    return input_format


def make_output_file_path(input_file_path, input_format, output_format, in_place):
    output_file_name = input_file_path.name.split(".")[:-1][0]

    if input_format == output_format and not in_place:
        output_file_name += ".new"

    output_file_name = output_file_name + "." + OUTPUT_FILE_ENDINGS.get(output_format)

    output_path = input_file_path.parent / output_file_name
    print("output file: {}".format(output_path))
    return output_path

def convert(input_file_path, persistence_system):
    input_format = get_input_format(input_file_path)
    g = Graph().parse(str(input_file_path), format=input_format)
    persistence_system.persist(g)


def merge(rdf_files: List[Path], persistence_system) -> Graph:
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
    persistence_system.persist(g)


def persist_to(persistence_system: PersistenceSystem, g: Graph):
    if not issubclass(type(persistence_system), PersistenceSystem):
        return ValueError(
            f"You must select of the the subclasses of PersistenceSystem to use for the persistence_system argument"
        )
    else:
        persistence_system.persist(g)


if __name__ == "__main__":
    if "-h" not in sys.argv and len(sys.argv) < 3:
        print(
            "ERROR: You must supply at a minimum the method (convert or merge), a file or files, and a target format"
        )
        exit()

    parser = argparse.ArgumentParser()

    parser.add_argument("method", choices=("convert", "merge"))
    # group = parser.add_mutually_exclusive_group(required=True)
#
# group.add_argument(
#     "-c",
#     "--convert",
#     type=str,
#     help="Converts a file, or directory of files, to another RDF format",
#     )
#
# group.add_argument(
#     "-m",
#     "--merge",
#     type=str,
#     help="Mergres a file, or directory of files, to a single RDF format.",
#     )

# parser.add_argument(
# 	'-i',
# 	'--inplace',
# 	help='if set, the file is converted in place, i.e. output file = input file',
# 	action='store_false'
# )

    parser.add_argument(
        "data",
        nargs='+',
        type=str,
        help="Path to the RDF file or directory of files"
    )

    parser.add_argument(
        "ext",
        type=str,
        help="The RDFlib token for the RDF format you want to convert the RDF file to.",
        choices=RDF_FILE_ENDINGS.keys(),
    )

    parser.add_argument(
        "--comments", type=str, help="Comments to prepend to the RDF, turtle only."
    )

    args = parser.parse_args()

    if args.method == "merge":
        print("merge")
        if Path(args.data).is_dir():
            ps = File(
                file_path=Path(args.data) / "merged",
                rdf_format=args.ext,
                leading_comments=args.comments,
            )
            # TODO glob only the allowed extensions
            files = [file for file in Path(args.data).glob("*")]  # if file extension in xxx
            merge(files, ps)
        elif Path.is_file(args.data):
            pass

    if args.method == "convert":
        files_list = prepare_files_list(args.data)
        for file in files_list:
            ps = File(
                file_path=Path(file).with_suffix("." + args.ext),
                rdf_format=args.ext,
                leading_comments=args.comments,
            )
            convert(file, ps)

# if Path.is_dir(args.data):
# 	print("converting directory {}".format(args.data))
# 	for f in Path(args.data).glob("*"):
# 		print("converting {}".format(f))
#
# 		input_format = get_input_format(f)
# 		output_file_path = make_output_file_path(f, input_format, RDF_FILE_ENDINGS.get(args.ext), args.inplace)
# 		ps = File(file_path=output_file_path,
# 				  output_format=args.ext,
# 				  leading_comments=args.comments)
# 		convert(f, input_format, ps)
#
# elif Path.is_file(args.data):
# 	print("converting {}".format(sys.argv[1]))
#
# 	output_file_path = make_output_file_path(
# 		args.data,
# 		get_input_format(args.data),
# 		RDF_FILE_ENDINGS.get(args.ext),
# 		args.inplace
# 	)
#
# 	convert(
# 		args.data,
# 		get_input_format(args.data),
# 		output_file_path,
# 		RDF_FILE_ENDINGS.get(args.ext),
# 	)
    else:
        raise ValueError(
            f"The value you supplied for 'data' was {args.data} but that is not a directory or file as required"
        )