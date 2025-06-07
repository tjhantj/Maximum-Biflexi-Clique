# The Maximum Biflexi Clique
This repository propose the maximum biflexi clique algorithm in the following paper submitted in CIKM 2025
## Source code info
Programming Language: Python 3.12

## Dataset
All datasets are obtained from [KONECT](http://konect.cc/networks/) website except for [housebill](https://www.cs.cornell.edu/~arb/data/)

## Usage
Each line of the input .txt file consists of two node IDs separated by a single whitespace, representing an edge in the bipartite graph. The left node belongs to the U-side, and the right node belongs to the V-side.

If the U-side and V-side node sets both start from 1 (i.e., there is potential overlap between node IDs), use the read_bipartite_edgelist function by specifying --filltype 1.

In contrast, if the U-side and V-side node sets are disjoint (i.e., their IDs do not overlap), use the read_bipartite_simple_edgelist function with --filltype 0.

## Command Line Options

| Option            | Type     | Default                             | Description |
|-------------------|----------|-------------------------------------|-------------|
| `--t`             | `float`  | `0.7`                               | Tau threshold parameter |
| `--algorithm`     | `str`    | `'biflexi'`                         | Algorithm name to be executed |
| `--network`       | `str`    | `'../dataset/real/CL.dat'`          | Path to the input dataset file |
| `--filetype`      | `int`    | `1`                                 | File type: `0` = U/V side disjoint, `1` = IDs may overlap |
| `--output`        | `str`    | `'none'`                            | Path to save CSV result file |
| `--noderesult`    | `str`    | `'none'`                            | Path to save selected node list |

You can run the script as follows:

```bash
python main.py --t 0.7 --algorithm biflexi --network ../dataset/real/CL.dat --filetype 1 --output result.csv --noderesult nodes.txt


