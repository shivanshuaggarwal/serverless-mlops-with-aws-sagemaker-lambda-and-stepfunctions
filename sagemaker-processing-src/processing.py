import argparse
import os
import warnings

import numpy as np
import pandas as pd
#from sklearn.model_selection import train_test_split
#from sklearn.preprocessing import PowerTransformer, StandardScaler
from sklearn.exceptions import DataConversionWarning

from time import gmtime, strftime

warnings.filterwarnings(action='ignore', category=DataConversionWarning)

LOCAL_DATA_PATH = "/opt/ml/processing" 
#LOCAL_DATA_PATH = "./data" 

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--train-test-split-ratio', type=float, default=0.3)
    args, _ = parser.parse_known_args()
    
    split_ratio = args.train_test_split_ratio

    input_data_path = os.path.join(LOCAL_DATA_PATH, 'input/boston.csv')
    print('Reading input data from {}'.format(input_data_path))
    df = pd.read_csv(input_data_path)
    print(df.shape)
    
    test_index = np.random.rand(len(df)) < 0.2
    test_df = df[test_index].reset_index(drop=True)
    df = df[~test_index].reset_index(drop=True)
    valid_index = np.random.rand(len(df)) < 0.2
    valid_df = df[valid_index].reset_index(drop=True)
    train_df = df[~valid_index].reset_index(drop=True)


    train_df.to_csv(os.path.join(LOCAL_DATA_PATH, "train/train.csv"), index = False)

    valid_df.to_csv(os.path.join(LOCAL_DATA_PATH, "validation/validation.csv"), index = False)

    test_df.to_csv(os.path.join(LOCAL_DATA_PATH, "test/test.csv"), index = False)
    
    print(train_df.shape)
    print(valid_df.shape)
    print(test_df.shape)