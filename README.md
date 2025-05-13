# LPItabformer

## Installation
```bash
pip install lpitabformer
```

## Usage
```bash
from lpitabformer.ft_transformer import *
import torch

model = FTTransformer(
    categories = (10, 5, 6, 5, 8),      # tuple containing the number of unique values within each category
    num_continuous = 10,                # number of continuous values
    dim = 32,                           # dimension
    dim_out = 1,                        # binary prediction, but could be anything
    depth = 1,                          # depth
    heads = 8,                          # heads
    attn_dropout = 0.2,                 # post-attention dropout
    ff_dropout = 0.2,                   # feed forward dropout
    p = 0.8,                            # the strength of DSU
    )

# This input just for example, not for LPIs.
x_categ = torch.randint(0, 5, (10, 5))  # category values, from 0 - max number of categories, in the order as passed into the constructor above
x_numer = torch.randn(10, 10)           # numerical value

pred = model(x_categ, x_numer) 
print(pred.shape)
```

## Example
The example code for training LPItabformer is in `example/example.zip`, you can download and unzip it and use it according to `README.txt`. `dsuTab_cz.ipynb` is the main example.
The example for using the trained LPItabformer model to predict new LPIs are in `example/tool_example/`, you could follow `predict.ipynb` to predict your LPI data.

## Model weights
The saving model weights are in `example/tool_example/data/model/`, `hsa` and `mus` represent human and mouse, respectively. You also could get from the `example/example.zip`. Note you need `ft_transformer.py` when you load the model weights, and you also leverage `example/tool_example/predict.ipynb`.

## Input format
For the input data format, please refer to the instructions in the provided example or case input.
