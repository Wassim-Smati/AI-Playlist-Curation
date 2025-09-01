
from IPython.display import Audio, FileLink
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import random
import shutil
import glob
import os
import zipfile
import warnings
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report, mean_absolute_error, silhouette_score
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.neighbors import KNeighborsClassifier
from sklearn import tree
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras import layers, models
import librosa
import librosa.display
import joblib
import graphviz
from transformers import pipeline

