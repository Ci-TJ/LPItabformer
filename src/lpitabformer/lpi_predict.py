import warnings

warnings.filterwarnings("ignore")
import sys

import pandas as pd
import numpy as np
import os

sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime
from torch.utils.data import DataLoader, TensorDataset

import torch

from joblib import Parallel, delayed
import multiprocessing

from utils import *
from ft_transformer import FTTransformer


def retrVal(indx, df, rna_mer, pro_mer, sep="_"):
    global rkmer, pkmer
    # rna = df.loc[indx][0]
    rna = df.loc[indx].iloc[0]
    pro = df.loc[indx].iloc[1]
    rkmer = rna_mer.loc[rna].values
    pkmer = pro_mer.loc[pro].values
    rp = np.concatenate((rkmer, pkmer), axis=0)
    rp_tuple = (rna + str(sep) + pro, rp)
    return rp_tuple


def lpi2data(df, rna_mer, pro_mer, sep="_", num_cores=multiprocessing.cpu_count(), backend="threading"):
    global kmer_list, kdf
    # kdf = pd.DataFrame(columns=np.concatenate((rna_mer.columns, pro_mer.columns), axis=0))
    '''
    backend:
    threading: multi threads for I/O task.
    multiprocessing and loky: for CPU enriched task.
    '''
    kmer_list = Parallel(n_jobs=num_cores, backend=backend) \
        (delayed(retrVal) \
             (indx=indx, df=df, rna_mer=rna_mer, pro_mer=pro_mer, sep=sep) \
         for indx in range(len(df)))

    kdf = pd.DataFrame(dict(kmer_list)).T
    kdf.columns = np.concatenate((rna_mer.columns, pro_mer.columns), axis=0)

    print(kdf.head())

    return kdf


def preprocess(args):
    global lpi, data, group_df, groups, gdf, rna_mer, pro_mer

    if "gencode" in args.clusterPath or "NONCODE" in args.clusterPath:
        select_part = 'front'
        merge_name = "RNA"
    else:
        select_part = 'back'
        merge_name = "protein"

    def transform(x, sep="_", select_part=select_part):
        if select_part == "back":
            x = x.split(sep)[1]  # Note: RNA.protein is formated in LION feature matrix
        else:
            x = x.split(sep)[0]
        return x

    rna_mer = pd.read_csv(args.rKmer, header=0, index_col=0,
                          usecols=lambda column: column != 'label')  # col 'label' is in MathFeature
    pro_mer = pd.read_csv(args.pKmer, header=0, index_col=0, usecols=lambda column: column != 'label')

    print(rna_mer.shape)

    lpi = pd.read_csv(args.lpi_file, header=0, index_col=0)
    if args.use_kmerM:
        data = lpi
    else:
        data = lpi2data(lpi, rna_mer, pro_mer, num_cores=12)  # -1 to 24


def dataPre(args):
    global tuple_cat, num_conti, col_names, data
    # NPInter2 and other datasets is RNA-protein-label, but RPI488 and RPI1807 is protein-RNA-label.
    if args.mode == 0:
        col_cat = ['C' + str(i) for i in range(1, 65)]
        col_num = ['N' + str(i) for i in range(1, 21)]
        col_names = col_cat + col_num
        tuple_cat = tuple([64] * 64)
        num_conti = 20
    elif args.mode == 1:
        col_cat = ['C' + str(i) for i in range(1, 21)]
        col_num = ['N' + str(i) for i in range(1, 65)]
        col_names = col_num + col_cat
        tuple_cat = tuple([20] * 20)
        num_conti = 64
    elif args.mode == 2:
        col_cat = ['C' + str(i) for i in range(1, 85)]
        col_num = ['N' + str(i) for i in range(1, 2)]
        col_names = col_cat + col_num
        tuple_cat = tuple([64] * 64 + [20] * 20)
        num_conti = 1
    elif args.mode == 3:
        col_cat = ['C' + str(i) for i in range(1, 2)]
        col_num = ['N' + str(i) for i in range(1, 85)]
        col_names = col_cat + col_num
        tuple_cat = tuple([1] * 1)
        num_conti = 84

    if args.mode == 2:
        data.loc[:, "N1"] = 0
        data.columns = col_names
    elif args.mode == 3:
        data.columns = col_num
        data.loc[:, "C1"] = 0
        data = data[col_names]
    else:
        data.columns = col_names

    print(data.head())

    data = data[col_cat + col_num]

    print(data.head())

    data[col_cat] = data[col_cat].fillna('0', )
    data[col_num] = data[col_num].fillna('0', )

    if args.mode == 2:
        cat_rna = ['C' + str(i) for i in range(1, 65)]
        cat_prot = ['C' + str(i) for i in range(65, 85)]
        ###RNA
        df_rna = data[cat_rna]
        for ind in range(df_rna.shape[0]):
            # df_cat.iloc[ind] = df_cat.iloc[ind].rank().astype(np.int32) - 1 #Note minus 1
            df_rna.iloc[ind] = np.argsort(df_rna.iloc[ind]).astype(np.int32)

        data[cat_rna] = df_rna.astype(np.int32)
        ###protein
        df_prot = data[cat_prot]
        for ind in range(df_prot.shape[0]):
            # df_cat.iloc[ind] = df_cat.iloc[ind].rank().astype(np.int32) - 1 #Note minus 1
            df_prot.iloc[ind] = np.argsort(df_prot.iloc[ind]).astype(np.int32)

        data[cat_prot] = df_prot.astype(np.int32)
    else:
        df_cat = data[col_cat]
        for ind in range(df_cat.shape[0]):
            # df_cat.iloc[ind] = df_cat.iloc[ind].rank().astype(np.int32) - 1 #Note minus 1
            df_cat.iloc[ind] = np.argsort(df_cat.iloc[ind]).astype(np.int32)

        data[col_cat] = df_cat.astype(np.int32)


def get_model():
    global ftt, loss_func
    ftt = FTTransformer(
        categories=(10, 5, 6, 5, 8),  # tuple containing the number of unique values within each category
        num_continuous=10,  # number of continuous values
        dim=32,  # dimension, paper set at 32
        dim_out=1,  # binary prediction, but could be anything
        depth=6,  # depth, paper recommended 6
        heads=8,  # heads, paper recommends 8
        attn_dropout=0.1,  # post-attention dropout
        ff_dropout=0.1,  # feed forward dropout
        p=0,

    )

    x_categ = torch.randint(0, 5, (
        1, 5))  # category values, from 0 - max number of categories, in the order as passed into the constructor above
    x_numer = torch.randn(1, 10)  # numerical value
    print(x_categ.shape)
    print(x_numer.shape)
    ftt(x_categ, x_numer)  # (1, 1)


def get_predict(loader, model, device=torch.device('cuda' if torch.cuda.is_available() else 'cpu'), mode=0):
    pred, target = [], []
    model.eval()
    with torch.no_grad():
        for x in loader:
            x = x[0].to(device).float()
            if mode == 0:
                x_categ = x[:, :64].cuda().to(torch.long)
                x_numer = x[:, 64:].cuda().to(torch.float32)
            elif mode == 1:
                x_categ = x[:, :20].cuda().to(torch.long)
                x_numer = x[:, 20:].cuda().to(torch.float32)
                # elif mode == 2:
            # 20240127
            elif mode == 2:
                x_categ = x[:, :84].cuda().to(torch.long)
                x_numer = x[:, 84:].cuda().to(torch.float32)
            elif mode == 3:
                x_categ = x[:, :1].cuda().to(torch.long)  # add in 20231121
                x_numer = x[:, 1:].cuda().to(torch.float32)

            y_hat = model(x_categ, x_numer)

            pred += list(y_hat.cpu().numpy())

    pred = pd.DataFrame(
        torch.tensor(np.array(pred)).softmax(dim=-1).numpy())  # torchmetrics will auto-determine logits or probs.
    lpi_index = pd.DataFrame(data.index, columns=['LPI'])
    probs_lpi = pd.concat([lpi_index, pred], axis=1)

    return probs_lpi


def modelPredict(args, data, mode, device, time=1234,
                 modelPath=None):
    global test_loader, evalCol, outDir, resDir, outDir
    resDir = os.path.join(args.workdir, "data", args.dataset, "result")
    if os.path.exists(resDir):
        print(f"{resDir} exits!")
    else:
        os.makedirs(resDir)

    outDir = os.path.join(resDir, "test")
    if os.path.exists(outDir):
        print(f"{outDir} exits!")
    else:
        os.makedirs(outDir)

    test_tensor_data = TensorDataset(torch.from_numpy(np.array(data)))
    test_loader = DataLoader(test_tensor_data, batch_size=args.bs)

    print("======================", "Start!", "======================", "\n")
    trTS = modelPath[0][-10:-4]  # time seed during the training -8:-4 to -10:-4 in 20240115
    model = torch.load(modelPath)

    probs_lpi = get_predict(test_loader, model, device, mode)  # get_result3 is for FTTransformer

    print("Model:", modelPath, "Test dataset:", data_name, "\n")
    probs_lpi.to_csv(
        os.path.join(outDir, "te_res_" + data_name + "_" + args.dataset + "_" + str(trTS) + "_" + str(time) + ".csv"),
        index=True, header=True)


class Args:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def lpi_predict(dataset: str = 'test_mEV',
                workdir: str = None,
                bs: int = 5,
                clusterPath: str = None,
                seed: int = 1,
                mode: int = 0,
                rKmer: str = None,
                pKmer: str = None,
                modelPath: str = None,
                save_metric: str = 'pre',
                lpi_file: str = None,
                use_kmerM: bool = True
                ) -> None:
    """
    Parameters:
    - dataset (str): The dataset you want to process
    - workdir (str): The initial directory
    - bs (int): Batch size
    - seed (int): Random seed
    - clusterPath (str): protein cluster file
    - mode (int): Mode for category and numeric for RNA and protein kmer. 0 is rna-cat and prot-num; 1 is rna-num and prot-cat; 2 is rna-cat and prot-cat; 3 is rna-num and pro-num
    - rKmer (str): All lncRNA kmer path
    - pKmer (str): All protein kmer path
    - modelPath (str): Model weight file path
    - save_metric (str): The metrics for saving models
    - lpi_file (str): Lpi file path
    - use_kmerM (bool): Whether you use the kmer matrix for input. If False, you need input the LPI pairs and waiting for kmer matrix generation
    """
    args = Args(
        dataset=dataset,
        workdir=workdir,
        bs=bs,
        seed=seed,
        clusterPath=clusterPath,
        mode=mode,
        rKmer=rKmer,
        pKmer=pKmer,
        modelPath=modelPath,
        save_metric=save_metric,
        lpi_file=lpi_file,
        use_kmerM=use_kmerM
    )

    assert workdir is not None and clusterPath is not None and rKmer is not None and pKmer is not None and modelPath is not None and lpi_file is not None, \
        'workdir, clusterPath, rKmer, pKmer, modelPath and lpi_file cannot be empty!'

    fix_random_seed(args.seed)

    global data_name, device
    seedList = [args.seed]  # [1, 2, 3, 4, 5]
    for i in seedList:
        # args.seed = i

        print("+++++++++++++++++++++++++++++++++++++++++++++++++++", "\n")
        print("++++++++++++++++++", "seed", i, "start!", "++++++++++++++++++", "\n")
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++", "\n")

        data_name = args.dataset
        ##0 prepare
        os.environ['CUDA_VISIBLE_DEVICES'] = '0'
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        # device ="cpu"
        print("Device available: ", device, " ", torch.cuda.get_device_name(0))

        ##1
        preprocess(args)
        dataPre(args)
        get_model()

        global now_time
        now_time = datetime.now().strftime('%Y_%m_%d_%H%M%S_%f')

        modelPredict(args=args, data=data, mode=args.mode, device=device, time=now_time, modelPath=args.modelPath)

        print(args.dataset, i, "\n", "Seed", args.seed, args.mode, "OK!", "\n")
        print("---------------------------------------------------------------------", "\n")
        print("---------------------------------------------------------------------", "\n")
