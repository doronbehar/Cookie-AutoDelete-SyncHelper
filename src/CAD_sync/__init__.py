#!/usr/bin/env python

import argparse
import json
import sys
import copy


# Based upon: https://stackoverflow.com/a/67208041/4935114
class ExplicitDefaultsHelpFormatter(argparse.ArgumentDefaultsHelpFormatter):
    # HACK: Use this function, as it prints multiline description and help
    # strings much better.
    _fill_text = argparse.RawDescriptionHelpFormatter._fill_text
    def _get_help_string(self, action):
        required = (
            " (REQUIRED)"
            if action.required else
            ""
        )
        if action.default in [None, [None], [], False]:
            return action.help + required
        return super()._get_help_string(action) + required
class ExplicitDefaultsArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **({
            'formatter_class': ExplicitDefaultsHelpFormatter,
        } | kwargs))

parser = ExplicitDefaultsArgumentParser(
    description=\
"""

Configuring [Cookie-AutoDelete][1] along with other containers handlin privacy
browser extensions is a bit tricky. That's because the JSON file it exports,
doesn't use container names, but rather unique identifiers of the containers.
This is [problematic][2] for syncing because whenever a new Firefox profile is
created, Firefox creates for you all the containers created in profiles in
other machines, but using new containers identifiers.

[1]: https://github.com/Cookie-AutoDelete/Cookie-AutoDelete
[2]: https://github.com/Cookie-AutoDelete/Cookie-AutoDelete/issues/1718

Given you have a working setup on machine A, you can use the script to transfer
that setup to machine B with the following instructions.
"""
)
parser.add_argument("-i", "--input-expressions",
    metavar="CAD_expressions-in.json",
    help="The input CAD_Expressions.json",
    required=True,
    type=argparse.FileType('r'),
)
parser.add_argument("-O", "--original-containers",
    metavar="original-containers.json",
    help=\
        "The original containers.json file fitting the --expressions argument. "
        "If not supplied, the script will ask you interactively to fit each "
        "list of URL expressions to a container names, using the "
        "--current-containers. This interactive usage requires the "
        "`questionary` Python library to be available.",
    required=False,
    type=argparse.FileType('r'),
)
parser.add_argument("-c", "--current-containers",
    metavar="containers.json",
    help=\
        "The current containers.json file, holding the names and the IDs of "
        "the containers on the machine you wish to import the CAD expressions "
        "to.",
    required=True,
    type=argparse.FileType('r'),
)
parser.add_argument("-o", "--output-expressions",
    metavar="CAD_expressions-out.json",
    help="The input CAD_Expressions.json",
    required=True,
    type=argparse.FileType('w'),
)

def get_containers_dict(file, id2name=True):
    return dict((
        (
            (ctr['userContextId'], ctr['name'])
            if id2name else
            (ctr['name'], ctr['userContextId'])
        )
        for ctr in json.load(file)['identities']
        if ctr['public']
    ))

def main():
    args = parser.parse_args()
    expressions = json.load(args.input_expressions)
    original_containers = (
        get_containers_dict(args.original_containers)
        if args.original_containers else
        {}
    )
    current_containers = get_containers_dict(args.current_containers, id2name=False)
    output_containers = {}
    for container_id_str in expressions:
        if container_id_str == "default":
            output_containers['default'] = expressions['default']
            continue
        container_id = int(container_id_str.removeprefix("firefox-container-"))
        if container_id not in original_containers:
            try:
                import questionary
            except ImportError:
                print(
                    "--original-containers argument doesn't include the "
                    "name-ID mapping required for matching container id "
                    f"{container_id} to a container by name. Hence we need "
                    "the `questionary` Python module to be available to make "
                    "such matches.",
                    file=sys.stderr,
                )
                sys.exit(3)
            choices = sorted(
                # Remove the containers we have already chosen..
                set(current_containers.keys()) - set(output_containers.keys())
            )
            # If we can take an easy guess based on the container name and the
            # 1st expression, do it.
            default=None
            for choice in choices:
                if choice.lower() in expressions[container_id_str][0]['expression']:
                    default=choice
            container_name = questionary.select(
                "Select the container of the following CAD URLs: " + ", ".join((
                    e['expression']
                    for e in expressions[container_id_str]
                )),
                choices=choices,
                default=default,
            ).ask()
            if container_name is None:
                sys.exit(2)
        else:
            container_name = original_containers[container_id]
        output_containers[container_name] = expressions[container_id_str]
    for container_name,container_id in current_containers.items():
        if container_name not in output_containers:
            continue
        new_key = "firefox-container-{}".format(container_id)
        # Copy (using list comprehension) the list in the `container_name` key,
        # while also fixing the 'storeId' key per each expression.
        output_containers[new_key] = [
            e | {'storeId': new_key}
            for e in output_containers[container_name]
        ]
        del output_containers[container_name]
    json.dump(
        output_containers,
        args.output_expressions,
        indent=4,
    )

if __name__ == '__main__':
    main()
