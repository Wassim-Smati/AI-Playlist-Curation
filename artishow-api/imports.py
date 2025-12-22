import pandas as pd
import numpy as np
import os
import warnings
import json 
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier

# --- Tensorflow ---
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras import layers, models

# --- Librosa ---
import librosa
import joblib

import requests

import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import librosa
import librosa.display