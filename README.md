# 🎵 Playlist Curation  
*Personalized AI playlist recommendations*

Try it here : https://appetize.io/app/b_e7noakfqlzpqggc54ns5p4tidy

<img src="_playlist-curation-2 (1).png" alt="Playlist Curation Poster" width="600"/>

[![YouTube](https://upload.wikimedia.org/wikipedia/commons/b/b8/YouTube_Logo_2017.svg)](https://www.youtube.com/shorts/TyXu-nWRp_8)

## 🚀 Project Description
This project develops **genre and mood classifiers** for music tracks using audio features and spectrograms.  
The goal is to provide a **personalized playlist recommendation tool**.


## 📊 Methodology
- **Datasets used:**
  - **GTZAN**: 1000 music clips (10 genres)
  - **MTG-Jamendo**: 55,000 tracks, multilabel (instruments, moods, etc.)
- **Extracted features:**
  - Tempo, Mean Energy, Spectrograms...
  - Feature vector (64 dimensions)
- **Classification methods:**
  - Random Forest, K-Nearest Neighbors, Gradient Boosting, Logistic Regression, SVM
- **Deep Learning:**
  - CNN (VGG16) applied on spectrograms
- **Ensemble Learning:**
  - Combining multiple models to improve performance

---

## 🛠️ Tech Stack
- **Python**
  - Scikit-Learn (Machine Learning)
  - Librosa (Feature extraction)
  - Pandas (Data processing)
  - TensorFlow (Deep Learning)
- **Mobile App**
  - Java (Android Studio)
  - Deezer API (music search + preview)

---

## 📱 Workflow
1. **Input**: audio file or song title  
2. **Analysis**: predict song’s genre and mood  
3. **Playlist Generator**: pick similar songs using Deezer API  
4. **Output**: personalized playlist on the mobile app  

## 👥 Supervisors
- **Aurian Quelennec**  
- **Antonin Gagnere**

## 📍 Institution
Project carried out at **Télécom Paris**
