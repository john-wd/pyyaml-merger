# PyYAML Merger

Built on top of the [deepmerge](https://github.com/toumorokoshi/deepmerge) package, I extend its `Merger` class to implement the [Strategic Merge Patch](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-api-machinery/strategic-merge-patch.md) strategy that is used in Kubernetes's Kustomize to build overlays on top of base images.

## How does it work?

Conventionally, when one attempts to deepmerge some composite data structure such as arrays (`list`s), either the whole array gets replaced by the incoming changes or things get added to it, so data is prone to be lost during merges. Worse still is that if you want to keep most of the structures in place, you would have to keep an exact copy of most of the contents between base and overlay files which directly impacts maintainability and overall cleanniness.

Kubernetes addesses this by having a *smarter* way of querying the conflicted entry if i. it exists, then update and ii. if it does not exist, then append to the array. This can only be done thanks to how Kubernetes work with selectors, which is to say "match things by `name`", for example.

I wanted to do something similar to generic YAML files so that we can enable composition (separate into smaller bits), customization (replace one field for a given overlay) and organization (keep files structure using some folder logic) to many regular configs monolithic files. Unsurprisingly, this can be done if said configuration has a *keyed* structure just like our `name` matcher from before. I then wanted to have two files

```yaml
# base.yaml
configs:
    - name: aservice
      http:
        url: http://example.com
        method: POST
        payload:
            some_field: potato
            # and so on
```

and 

```yaml
# overlay.yaml
configs:
    - name: aservice
      http:
        url: http://another.host.com

    - name: brand-new-service
      config:
        socket: unix:///tmp/some.socket

```

results into

```yaml
configs:
    - name: aservice
      http:
        url: http://another.host.com
        method: POST
        payload:
            some_field: potato
            # and so on
    - name: brand-new-service
      config:
        socket: unix:///tmp/some.socket
```

This can be done with the present solution.

### Special field `$mergeStrategy`

Sometimes I want to remove bits in an overlay from a base config or replace it in full with another thing (think of some feature that I do not want in production yet or to completely redo a plugin configuration for test environments). For this, I introduce this `$mergeStrategy` field that should be declared within an array element with either `remove` or `replace` values. This field will not be rendered in the final coalesced file, so no need to worry.

To illustrate this, take the example above

```yaml
configs:
    - name: aservice
      http:
        url: http://another.host.com
        method: POST
        payload:
            some_field: potato
            # and so on
    - name: brand-new-service
      config:
        socket: unix:///tmp/some.socket
```

To remove `brand-new-service`, all you have to do is to merge it with

```yaml
configs:
    - name: brand-new-service
      $mergeStrategy: remove
```

Thus the result will be

```yaml
configs:
    - name: aservice
      http:
        url: http://another.host.com
        method: POST
        payload:
            some_field: potato
            # and so on
```

Alternatively, I can update the entire `aservice`. Taking the same example, but applying

```yaml
configs:
    - name: aservice
      $mergeStrategy: replace
      log: /var/log/some-entry.log
    - name: brand-new-service
      config:
        socket: unix:///tmp/some.socket

```

will result in

```yaml
configs:
    - name: aservice
      log: /var/log/some-entry.log
    
```


## Installation

Clone this repository, then run

```bash
$ python -m pip install --user .
```

to install into your own user $PYTHONPATH or, to work it in a virtual environment

```bash
$ python -m venv venv
$ source venv/bin/activate
(venv) $ pip install .
```

This installs the `yaml-merge` binary to your `$PATH`, so you can run

```bash
$ yaml-merge --help

Usage: yaml-merge [OPTIONS] [FILES]...

Options:
  -r, --recursive    Traverse given directory
  -o, --output PATH  Output file. Defaults to the stdout.
  -k, --key TEXT     Which key to use for strategy patch.  [default: name]
  -h, --help         Show this message and exit.
```

## Use it with docker

Pull the image `johnwds/pyyaml-merger` and mount your YAML config folder to `/workdir`.

```bash
$ docker pull johnwds/pyyaml-merger
$ docker run --rm -v /path/to/your/yaml/folder:/workdir pyyaml-merger
```

It will recursively merge all YAML files and print the full rendered file to your stdout.

### Use more than one directory

To apply more overlays on top of this one, do

```bash
$ docker run --rm -v /path/to/base:/workdir -v /path/to/overlay:/patches pyyaml-merger yaml-merge -r /workdir /patches
```

and so on.

## Read more

- [Kubernetes Strategic Merge Patch rationale](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-api-machinery/strategic-merge-patch.md)
- [deepmerge](https://github.com/toumorokoshi/deepmerge) library