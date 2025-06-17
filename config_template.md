For a config file, a toml/yaml/json is all acceptable.
However, we recommend using toml or yaml for better readability.

nvchecker_doc: "https://nvchecker.readthedocs.io/en/latest/usage.html#configuration-files"

You shall read the documentation for more details. However here is a brief introduction.

```toml
[name]
# The name is the name of the software you want to check.
source = "github" # The source of the software, also specified which plugin to use.
# Here, we use the github plugin as an example.
repo = "owner/repo" # The repository of the software, for github, it is in the form of owner/repo.
# For other sources, please refer to the documentation.
use_latest_release = true # Use the latest release version as the version.
```

Also, here is an simple version of the config file, using url as the source.

```yaml
name:
    source: regex
    url: "https://example.com/downloads/latest"
    regex: "v([0-9]+\\.[0-9]+\\.[0-9]+)"
```

The above example uses the regex plugin to check the version from a URL, It will get the entire HTML page and search for the version number using the regex pattern provided.

# How the name is formatted

For general case, the name is formatted as:
```
{vendor}-generic-{system}-{variant}
```

All above fields are in support-matrix's metadata. If any field is `None`, use `null` instead.

For example, for duo buildroot v1:
```
milkv-duo-generic-buildroot-v1
```

To split each part for a better understanding:
```
milkv-duo
-generic-
buildroot
-
v1
```

For any specific case, modify the function in src/utils.py:gen_old to suit your needs. However, better not have so many special cases?

# How to skip one image?

There are two ways to skip an image:
- Manually skip: Indicate the image is checked manually.
- EOL skip: Indicate the image is EOL, we would not check it anymore.

For manual skip, a note will be added to the report, add it like this:
```yaml
skip: true
reason: "Any reason you want to skip this image, Optional, but recommended to add."
```

For EOL skip, no note will provided, add it like this:
```yaml
eol: true
```
