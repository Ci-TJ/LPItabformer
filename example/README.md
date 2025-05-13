# Introduction

## 1. Tool Example
`tool_example` demonstrates how to use the trained model to predict new LPIs. You can follow the instructions in `predict.ipynb` to achieve your goal.

## 2. Example.zip
- `example.zip` contains the code for training LPItabformer on LPI346223 and LPI250342 (also named LPI500684) using GroupKFold or KFold. The code is in `dsuTab_cz.ipynb`.
- LPItabformer requires **three essential input files**:
  1. **LPI pairs with labels**, named `LPI346223_seed1_randp1.txt` and `LPI500684_seed1_randp1.txt`.
  2. **K-mer matrix**, generated using [MathFeature](https://bonidia.github.io/MathFeature/). You can create it with `data_mf.sh` or `mf.sh`.
  3. **Cluster information for RNAs and proteins**, which you can generate using [MMseqs2](https://github.com/soedinglab/MMseqs2) with the script `cluster.sh`.




