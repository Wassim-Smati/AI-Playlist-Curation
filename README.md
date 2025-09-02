# 🎵 Playlist Curation  
*Personalized AI playlist recommendations*

<img src="_playlist-curation-2 (1).png" alt="Playlist Curation Poster" width="600"/>
[![Watch the video](https://img.youtube.com/vi/VIDEO_ID/0.jpg)](https://www.youtube.com/watch?v=VIDEO_ID)
---

## 🚀 Project Description
This project develops **genre and mood classifiers** for music tracks using audio features and spectrograms.  
The goal is to provide a **personalized playlist recommendation tool**.

---

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
