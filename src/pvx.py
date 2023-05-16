#! /usr/bin/env python3
#
# pvx.py

# penvm-pvx
#
# Copyright 2023 J4M Solutions
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import traceback

try:
    from penvm.client.world import World
    from penvm.ext.workers import MirrorExecWorker
except:
    print("error: cannot find penvm", file=sys.stderr)
    sys.exit(1)

__VERSION__ = (0, 1, 0)
__VERSION_STR__ = ".".join(map(str, __VERSION__))

HEREFILE = os.path.abspath(sys.argv[0])


class ArgOpts:
    pass


def print_usage():
    progname = os.path.basename(sys.argv[0])
    print(
        f"""\
usage: {progname} [<args>] <cmd> [<cmdarg> ...]
       {progname} -h|--help

Run a command on a PENVM network of machines.

There are multiple output modes:
* lines - line oriented
* json - json object
* yaml - yaml text

JSON and YAML output is organized under machine id key, and includes:
* response status ("status")
* return/exit code ("returncode")
* stderr ("stderr")
* stdout ("stdout").

For "lines" mode output (grouped and non-grouped), only stdout is
output to stdout, all else is sent to stderr.

Arguments:
<cmd>                   Command.
<cmdarg> ...            Argument(s) for the command.
-c <config>             Configuration filename.
--empty                 Show even when empty (e.g., stdout and
                        stderr). Use with --group.
--group                 Group output (for lines) with a heading.
                        Default is non grouped output.
--heading <format>      Heading output before each group. String
                        format substitution is done for "machid" and
                        "stdtype".
-I|--ignore-on-error    Ignore results on error (returncode != 0).
--json                  JSON output mode: output results as JSON.
--lines                 Lines output mode: output results as lines.
                        Default output mode.
--prefix <format>       Prefix all output lines with machine id. See
                        --heading for format.
--no-heading            Do not use heading for groups.
--no-prefix             Do not prefix output lines.
--no-stdout             Do not show stdout.
--on-error              Show only on error (returncode != 0). Should
                        use with --stderr and/or --returncode.
--returncode            Show returncode. For "lines".
--shell <path>          Run command in a shell.
--split                 Split into lines. Use with --json and --yaml.
--split-sep <separator> Split separator. Use with --json and --yaml.
                        A separator of "" (empty string) means
                        whitespace (blank(s), tab(s), newline). Defaults to "\\n".
--status                Show status. For "lines".
--stderr                Show stderr. For "lines".
--unify                 Unify all split results.
--unify-up              Unify with "--unify", "--split", and "--split-trim".
--yaml                  YAML output mode: output results as YAML.
--version               Print version.
""",
        end="",
    )


# TODO: requires further development
# --window                Show results in windows. Window locations are
#                        provided in PENVM_WINDOWS.


def main():
    try:
        argopts = ArgOpts()
        argopts.cmd = None
        argopts.cmdargs = None
        argopts.configfilename = None
        argopts.format = "lines"
        argopts.group = False
        argopts.heading = os.environ.get(
            "PVX_HEADING_FORMAT",
            "----- [%(machid)s][%(stdtype)s] -----",
        )
        argopts.ignoreonerror = False
        argopts.parser = None
        argopts.prefix = os.environ.get(
            "PVX_PREFIX_FORMAT",
            "[%(machid)s][%(stdtype)s]:",
        )
        argopts.network = "default"
        argopts.shell = False
        argopts.showempty = False
        argopts.showonerror = False
        argopts.showreturncode = False
        argopts.showstatus = False
        argopts.showstderr = False
        argopts.showstdout = True
        argopts.split = False
        argopts.splitsep = "\n"
        argopts.splittrim = False
        argopts.unify = False
        # argopts.view = None

        args = sys.argv[1:]
        while args:
            arg = args.pop(0)
            if arg in ["-h", "--help"]:
                print_usage()
                sys.exit(0)
            elif arg == "-c" and args:
                argopts.configfilename = args.pop(0)
            elif arg == "--empty":
                argopts.showempty = True
            elif arg == "--format" and args:
                argopts.format = args.pop(0)
            elif arg == "--group":
                argopts.group = True
            elif arg == "--heading" and args:
                argopts.heading = args.pop(0)
            elif arg in ["-I", "--ignore-on-error"]:
                argopts.ignoreonerror = True
            elif arg == "--json":
                argopts.format = "json"
            elif arg == "--lines":
                argopts.format = "lines"
            elif arg == "-N" and args:
                argopts.network = args.pop(0)
            elif arg == "--no-heading":
                argopts.heading = ""
            elif arg == "--no-prefix":
                argopts.prefix = ""
            elif arg == "--no-stdout":
                argopts.showstdout = False
            elif arg == "--on-error":
                argopts.showonerror = True
            elif arg == "--split":
                argopts.split = True
            elif arg == "--split-sep" and args:
                argopts.splitsep = args.pop(0)
                if argopts.splitsep == "":
                    # special: whitespace
                    argopts.splitsep = None
            elif arg == "--split-trim":
                argopts.splittrim = True
            elif arg == "--stderr":
                argopts.showstderr = True
            elif arg == "--parser" and args:
                argopts.parser = args.pop(0)
            elif arg == "--prefix" and args:
                argopts.prefix = args.pop(0)
            elif arg == "--shell":
                argopts.shell = True
            elif arg == "--status":
                argopts.showstatus = True
            elif arg == "--returncode":
                argopts.showreturncode = True
            elif arg == "--unify":
                argopts.unify = True
            elif arg == "--unify-up":
                argopts.unify = True
                argopts.split = True
                argopts.splittrim = True
            elif arg == "--version":
                print(__VERSION_STR__)
                sys.exit(0)
            elif arg == "--yaml":
                argopts.format = "yaml"
            # elif arg == "--window":
            # argopts.view = "window"
            elif arg.startswith("--"):
                raise Exception(f"unknown option ({arg})")
            else:
                if argopts.shell:
                    argopts.cmd = "/bin/bash"
                    argopts.cmdargs = ["-c", arg] + args
                else:
                    argopts.cmd = arg
                    argopts.cmdargs = args[:]
                del args[:]

        if argopts.cmd == None:
            raise Exception("missing command")
        if argopts.format not in ["json", "lines", "yaml"]:
            raise Exception(f"unsupported format ({argopts.format})")
    except SystemExit:
        raise
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        if argopts.configfilename:
            world = World(filename=argopts.configfilename)
        else:
            world = World()
        network = world.get_network(argopts.network)
        try:
            network.boot()
        except:
            raise Exception(f"failed to boot network ({argopts.network})")

        w = MirrorExecWorker(
            os.getcwd(),
            network,
        )
        # print(f"{argopts.cmd=} {argopts.cmdargs=}")
        result = w.run(argopts.cmd, *argopts.cmdargs)

        # set filters
        stdxs = []
        if argopts.showstdout:
            stdxs.append("stdout")
        if argopts.showstderr:
            stdxs.append("stderr")
        if argopts.showreturncode:
            stdxs.append("returncode")
        if argopts.showstatus:
            stdxs.append("status")

        # apply filters
        for k in list(result.keys()):
            v = result[k]
            returncode = v.get("returncode")
            if argopts.ignoreonerror and returncode != 0:
                result.pop(k)
                continue

            if argopts.showonerror and returncode == 0:
                result.pop(k)
                continue

            for stdx in ["stdout", "stderr", "returncode", "status"]:
                if stdx not in stdxs:
                    v.pop(stdx)

        # output results
        if argopts.format in ["json", "yaml"]:
            if argopts.split:
                # split string into lines
                for stdx in ["stdout", "stderr"]:
                    for k, v in result.items():
                        vv = v.get(stdx)
                        if vv != None:
                            l = vv.split(argopts.splitsep)
                            if argopts.splittrim and l[-1] == "":
                                l = l[:-1]
                            v[stdx] = l

                if argopts.unify:
                    result["all"] = {}
                    for stdx in stdxs:
                        l = []
                        for k, v in list(result.items()):
                            if stdx in v:
                                vv = v.pop(stdx)
                                if type(vv) == list:
                                    l.extend(vv)
                                else:
                                    l.append(vv)

                        result["all"][stdx] = l

                    for k in list(result.keys()):
                        if k != "all":
                            result.pop(k)

            if argopts.format == "json":
                import json

                s = json.dumps(result, indent=2)
                print(s)
            elif argopts.format == "yaml":
                import yaml

                s = yaml.dump(result)
                print(s, end="")
        elif argopts.format == "lines":

            returncodes = []
            for k, v in sorted(result.items()):
                for stdx in stdxs:
                    vv = v.get(stdx)
                    if stdx in ["returncode", "status"]:
                        if stdx == "returncode":
                            returncodes.append(vv)
                        out = str(vv)
                    else:
                        out = vv

                    if out == "":
                        if not argopts.group:
                            continue
                        if not argopts.showempty:
                            continue

                    # stderr and returncode output to stderr
                    f = sys.stdout if stdx == "stdout" else sys.stderr
                    d = {
                        "machid": k,
                        "stdtype": stdx,
                    }

                    if argopts.group:
                        if argopts.heading:
                            heading = argopts.heading % d
                            print(heading, file=f, flush=True)
                        print(out, end="", file=f, flush=True)
                    else:
                        prefix = argopts.prefix % d
                        if out.endswith("\n"):
                            # trim trailing newline
                            out = out[:-1]
                        out = "\n".join([f"{prefix}{line}" for line in out.split("\n")])
                        if out:
                            print(out, file=f, flush=True)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        # traceback.print_exc()
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        pass


if __name__ == "__main__":
    main()
