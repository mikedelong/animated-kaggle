import logging
from json import load
from os.path import isdir
from time import time

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeRegressor


def get_setting(arg_setting_name, arg_settings):
    if arg_setting_name in arg_settings.keys():
        result = arg_settings[arg_setting_name]
        return result
    else:
        logger.warning('required key %s is not in the settings. Quitting.' % arg_setting_name)
        quit()


def check_exists(arg_folder_name, arg_descriptor):
    folder_exists = isdir(arg_folder_name)
    if folder_exists:
        logger.debug('using %s as the %s folder' % (arg_folder_name, arg_descriptor))
    else:
        logger.warning('%s %s does not exist. Quitting.' % (arg_descriptor, arg_folder_name))
        quit()


if __name__ == '__main__':
    start_time = time()

    formatter = logging.Formatter('%(asctime)s : %(name)s :: %(levelname)s : %(message)s')
    logger = logging.getLogger('main')
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    console_handler.setLevel(logging.DEBUG)
    logger.debug('started')

    with open('./settings-predict.json') as settings_fp:
        settings = load(settings_fp)
        logger.debug(settings)

    input_folder = get_setting('input_folder', settings)
    check_exists(input_folder, 'input')
    output_folder = get_setting('output_folder', settings)
    check_exists(output_folder, 'output')
    training_data_file = get_setting('training_data_file', settings)
    full_training_data_file = input_folder + training_data_file
    logger.debug('loading data from %s' % full_training_data_file)
    train_df = pd.read_csv(full_training_data_file)
    logger.debug('training data has shape %d x %d' % train_df.shape)
    test_data_file = get_setting('test_data_file', settings)
    full_test_data_file = input_folder + test_data_file
    logger.debug('loading data from %s' % full_test_data_file)
    test_df = pd.read_csv(full_test_data_file)
    logger.debug('training data has shape %d x %d' % test_df.shape)

    # get the target before we do any feature engineering
    target = train_df['TARGET'].values

    # get the fields where we want to do label encoding
    fields_to_label_encode = get_setting('fields_to_label_encode', settings)
    logger.debug('we will use the label encoder for the following fields: %s' % fields_to_label_encode)
    for field in fields_to_label_encode:
        if train_df.dtypes[field] == 'object':
            train_df[field].replace(np.nan, '', regex=True, inplace=True)
            test_df[field].replace(np.nan, '', regex=True, inplace=True)
        encoder = LabelEncoder()
        logger.debug('field %s has unique values %s' % (field, train_df[field].unique()))
        encoder.fit(train_df[field])
        train_df[field] = encoder.transform(train_df[field])
        logger.debug('done transforming the training data, field %s' % field)
        test_df[field] = encoder.transform(test_df[field])
        logger.debug('done transforming the test data, field %s' % field)

    # after feature engineering align the two data frames
    train_df, test_df = train_df.align(test_df, join='inner', axis=1)
    logger.debug('after alignment the training data has shape %d x %d' % train_df.shape)
    logger.debug('after alignment the test data has shape %d x %d' % test_df.shape)

    random_state = get_setting('random_state', settings)
    # build the model
    model = DecisionTreeRegressor(criterion='mse', splitter='best', max_depth=None, min_impurity_split=2,
                                  min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_features=None,
                                  random_state=random_state, max_leaf_nodes=None, presort=False,
                                  min_impurity_decrease=0.0)

    model.fit(X=train_df, y=target, sample_weight=None, check_input=True, X_idx_sorted=None)
    y_pred = model.predict(X=test_df, check_input=True)

    logger.debug('done')
    finish_time = time()
    elapsed_hours, elapsed_remainder = divmod(finish_time - start_time, 3600)
    elapsed_minutes, elapsed_seconds = divmod(elapsed_remainder, 60)
    logger.info("Time: {:0>2}:{:0>2}:{:05.2f}".format(int(elapsed_hours), int(elapsed_minutes), elapsed_seconds))
    console_handler.close()
    logger.removeHandler(console_handler)
