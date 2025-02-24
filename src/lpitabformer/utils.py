import torch
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

#20231030
def fix_random_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)  
    np.random.seed(seed) 

def calculate_metrics(y_true, y_pred, thres=0.5):
    TP = 0
    TN = 0
    FP = 0
    FN = 0
    for i in range(len(y_true)):
        if y_true[i] == 1 and y_pred[i] >= thres:
            TP += 1
        if y_true[i] == 0 and y_pred[i] < thres:
            TN += 1
        if y_true[i] == 0 and y_pred[i] >= thres:
            FP += 1
        if y_true[i] == 1 and y_pred[i] < thres:
            FN += 1
    sensitivity = TP / (TP + FN + 1e-10) #recall
    precision = TP / (TP + FP + 1e-10) #ppv
    specificity = TN / (TN + FP + 1e-10)
    npv = TN / (TN + FN + 1e-10)
    acc = (TN + TP) / (TN + FN + TP + FP + 1e-10)
    F1_score = 2*(precision*sensitivity)/(precision + sensitivity + 1e-10)
    mcc = (TP * TN - FP * FN) / np.sqrt((TP + FP) * (TP + FN) * (TN + FP) * (TN + FN) + 1e-10) #Add 20230903
    return sensitivity, precision, specificity, npv, acc, F1_score, mcc

from torchmetrics.classification import MulticlassConfusionMatrix, MulticlassAccuracy, MulticlassAUROC, MulticlassF1Score, MulticlassMatthewsCorrCoef, \
MulticlassPrecision,  MulticlassRecall, MulticlassROC, MulticlassSpecificity 


def calculate_performace(preds,  labels, device=torch.device('cuda' if torch.cuda.is_available() else 'cpu'), ma_avg="weighted"):
    global TN, TP, FN, FP
    eps = 1e-10
    
    preds = preds.to(device)
    labels = labels.to(device)
    
    CF = MulticlassConfusionMatrix(num_classes=2).to(device)
    MA = MulticlassAUROC(num_classes=2, average=ma_avg).to(device)
    
    confusionMatrix = CF(preds, labels)
    TN = confusionMatrix[0][0].item()
    FP = confusionMatrix[0][1].item()
    FN = confusionMatrix[1][0].item()
    TP = confusionMatrix[1][1].item()
    
    sensitivity = TP / (TP + FN + eps) #recall
    precision = TP / (TP + FP + eps) #ppv
    specificity = TN / (TN + FP + eps)
    npv = TN / (TN + FN + eps)
    acc = (TN + TP) / (TN + FN + TP + FP + eps)
    f1 = 2*(precision*sensitivity)/(precision + sensitivity + eps)
    mcc = (TP * TN - FP * FN) / np.sqrt((TP + FP) * (TP + FN) * (TN + FP) * (TN + FN) + eps) #Add 20230903
    auc = MA(preds, labels).item()
    
    return acc, auc, f1, mcc, npv, precision, sensitivity, specificity
                                                                 
#for FTTransformer
def get_result3(loader, model, device=torch.device('cuda' if torch.cuda.is_available() else 'cpu'), mode=0):
    pred, target = [], []
    model.eval()
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device).float(), y.to(device).float()
            if mode == 0:
                x_categ = x[:,:64].cuda().to(torch.long)
                x_numer = x[:,64:].cuda().to(torch.float32) 
            elif mode == 1:
                x_categ = x[:,:20].cuda().to(torch.long)
                x_numer = x[:,20:].cuda().to(torch.float32)
            elif mode == 2:
                x_categ = x[:,:84].cuda().to(torch.long)
                x_numer = x[:,84:].cuda().to(torch.float32) 
            elif mode == 3:
                x_categ = x[:,:1].cuda().to(torch.long) #add in 20231121
                x_numer = x[:,1:].cuda().to(torch.float32) 
                        
            y_hat = model(x_categ, x_numer)
            y_hat = torch.sigmoid(y_hat) #Add 20230925
            
            pred += list(y_hat.cpu().numpy())
            target += list(y.cpu().numpy())
    auc = roc_auc_score(target, pred)
    sen, pre, spe, npv, acc, F1, mcc = calculate_metrics(target, pred)

    return acc, auc, F1, mcc, npv, pre, sen, spe

def get_result4(loader, model, device=torch.device('cuda' if torch.cuda.is_available() else 'cpu'), mode=0):
    pred, target = [], []
    model.eval()
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device).float(), y.to(device).float()
            if mode == 0:
                x_categ = x[:,:64].to(torch.long)
                x_numer = x[:,64:].to(torch.float32)
            elif mode == 1:
                x_categ = x[:,:20].to(torch.long)
                x_numer = x[:,20:].to(torch.float32)

            elif mode == 2:
                x_categ = x[:,:84].to(torch.long)
                x_numer = x[:,84:].to(torch.float32)
            elif mode == 3:
                x_categ = x[:,:1].to(torch.long) #add in 20231121
                x_numer = x[:,1:].to(torch.float32)
                        
            y_hat = model(x_categ, x_numer)
            y = y.squeeze(dim=-1).long() #20240204
            
            pred += list(y_hat.cpu().numpy())
            target += list(y.cpu().numpy())
    pred = torch.tensor(np.array(pred)).softmax(dim=-1)
    target = torch.tensor(target).to(torch.long)
    acc, auc, f1, mcc, npv, pre, sen, spe = calculate_performace(pred, target, device)
    return acc, auc, f1, mcc, npv, pre, sen, spe