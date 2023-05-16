# pvx

pvx leverages PENVM to perform operations across a network of machines.

## Prerequisites

PENVM is required. See [penvm](https://penvm.dev/).

Download pvx:
```
mkdir ~/tmp
cd ~/tmp
git clone https://github.com/penvm/penvm-pvx.git
```

Add to `PATH`:
```
export PATH=~/tmp/penvm-pvx/bin:$PATH
```

## Setup

A PENVM network needs to be set up either in advance or at run time. Set up in advance means faster runs.

The following requires a world configuration file. See [http://github.com/penvm/penvm](http://github.com/penvm/penvm) for details.

Use `penvm-boot` to set up in advance:
```
penvm-boot --verbose --shell /bin/bash <configfile>
```

Otherwise, provide a configuration file at execution time. E.g.,
```
pvx -c <config> hostname
```

## Examples

Unless indicated otherwise, the following assume that a network is in place.

### Basic Operation

Get host names:
```
pvx hostname
```

Get process status information:
```
pvx ps
```

Get process status of all processes, long format:
```
pvx ps -elf
```

Notes:

* Default output is in "lines" mode with only "stdout".
* Each line is prefixed.
* The default prefix format is `[%(machid)s][%(stdtype)s]` where `machid` is the PENVM machine id and `stdtype` is one of "stdout", "stderr", "status", "returncode".

### Stdtypes

By default `stdout` is always output. But `stderr`, `returncode`, and `status` are not. To obtain more than `stdout`, specify:

* `--stderr` - show stderr
* `--returncode` - show returncode
* `--status` - show message status

`stdout` can be ignored by using `--no-stdout`.

Get directory listing (defaults to the current working directory) with `stderr` and `returncode`:
```
pvx --stderr --returncode ls
```

If there is no output (e.g., for `stderr`), it will *not* show.

Get directory listing of `/tmp`:
```
pvx --stderr --returncode ls /tmp
```

Get directory listing at non-existent path:
```
pvx --stderr --returncode ls /tmp/123456789
```

Get only non-error results (choose a `/tmp/XXX` that does not exist on at least one machine):
```
pvx --ignore-on-error --stderr ls /tmp/XXX
```

Get returncodes only (must suppress `stdout`):
```
pvx --returncode --no-stdout ls /tmp/XXX
```

Get returncodes only for error results:
```
pvx --on-error --returncode ls /tmp/XXX
```

### Grouped Output

Instead of each output line being prefixed, output can be grouped with a suitable heading.

Get directory listing:
```
pvx --group ls /tmp
```

Empty results can be shown when grouped:
```
pvx --group --empty --stderr ls /
```

### JSON and YAML

In addition to "lines" mode, `pvx` can output in json and yaml formats. These are best suited when those formats can be worked with easily.

Get hostnames using "json" mode:
```
pvx --json hostname
```

Get hostnames using "yaml" mode:
```
pvx --yaml hostname
```

Notes:

* Trailing newlines in `stdout` and `stderr` are *not* stripped/trimmed.
* Trailing newlines make for (slightly) unexpected yaml output, but it does load back correctly.

Whereas "lines" mode splits output into individual lines (to allow for prefixing) by default, json and yaml modes output are raw (i.e., not split into lines, and not stripped/trimmed).

Get process status:
```
pvx --json ps
```

Get process status and split into lines (newline separator) to produce a list:
```
pvx --split --yaml ps
```

Again, but strip/trim trailing empty string:
```
pvx --split --split-trim --yaml ps
```

Again, but split by whitespace:
```
pvx --split --split-trim --split-sep "" --yaml ps
```

This result is every non-whitepsace text is its own value in a list.

### Unified Result

There are multiple ways to obtain a unified form of the results. I.e., the data independent of its source.

Remove prefix (for "lines" mode):
```
pvx --no-prefix hostname
```

Remove heading (for group in "lines" mode):
```
pvx --no-heading --group hostname
```

Unify under special "all" machine id and json:
```
pvx --unify --split --split-trim --json hostname
```

Notes:

* The `--split` is required to obtain lists for output of each stdtype.
* The `--split-trim` is necessary to eliminate trailing empty string which is typically unwanted.

### Shell Pipeline

Some operations are better done on the output from each source, at the source, before returning. Shell (`/bin/bash`) pipelines make this possible.

Get filtered directory listing (command and pipeline must be enclosed):
```
pvx --shell 'ls /etc | grep host.'
```

Again, but split and present as json:
```
pvx --split --json --shell 'ls /etc/ | grep host.'
```

The same could be done with:
```
pvx --split --json /bin/bash -c 'ls /etc/ | grep host.'
```

### Troubleshooting

Some tips if something does not seem to be working correctly.

Simplify the command and arguments being called until something works.

Enable all stdtypes and output in json or yaml:
```
pvx --returncode --stderr --status --json <cmd> [<arg> ...]
```

If the `status` is not `ok`, then something is not working right on the machine side.

If the `returncode` is not 0, then something is not correct with the command being executed. See also the `stderr` which should clarify things further.
