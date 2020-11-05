# Contributor Network Graph

Create a graph visualization from a code repository.

![Graph for contributor-network repository](data/contributor-network-graph.png)


## Installing

```
pip install contributor-network
```

## Running

Given a file called `dependencies.csv`, like:

```csv
name,repository_type,repository_url,depended_by
contributor-network,git,https://github.com/PythonicCafe/contributor-network,
lxml,git,https://github.com/lxml/lxml,contributor-network
tqdm,git,https://github.com/tqdm/tqdm,contributor-network
```

Execute:

```shell
python -m contributor_network.cli \
	--temp-dir=/tmp/repositories/ \
	dependencies.csv \
	network/
```
