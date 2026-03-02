# 🎵 AI Playlist Curation
*Personalized music recommendation engine & Android application.*

<div align="center">

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)]()
[![Java](https://img.shields.io/badge/Java-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)]()
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)]()
[![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)]()

<br/>

## 🌟 [👉 CLICK HERE TO TEST THE LIVE ANDROID APP IN YOUR BROWSER 👈](https://appetize.io/app/b_e7noakfqlzpqggc54ns5p4tidy) 🌟
*(No installation required)*

<br/>

<a href="https://appetize.io/app/b_e7noakfqlzpqggc54ns5p4tidy" target="_blank">
  <img src="_playlist-curation-2 (1).png" alt="Playlist Curation Poster" width="600" style="border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);"/>
</a>
<p><i>👆 Click the image above to launch the live demo!</i></p>

</div>

---

🏆 **Achievement:** Top 5 Jury Favorites at the Telecom Paris Project Showcase.

## 🚀 Overview
This project is an end-to-end music recommendation platform. It features deep-learning-based **genre and mood classifiers** leveraging audio features and spectrograms to curate highly personalized playlists. 

Moving beyond a simple Jupyter Notebook, this project encapsulates a full software engineering lifecycle using Python, Docker, and Java: from model training to a fully deployed REST API and a functional Android interface.

## 🏗️ Architecture & MLOps

To ensure scalability and maintainability, the system is designed with a modern MLOps approach:
* **Backend API:** Dockerized REST API to handle inference requests seamlessly.
* **CI/CD Pipeline:** Continuous deployment pipeline built with GitHub Actions, pushing the Dockerized API directly to Hugging Face Spaces.
* **Frontend Client:** Native Android application built in Java. It handles the user interface, REST API integrations, and complex backend/frontend interactions.

## 🧠 Machine Learning Methodology

### Datasets & Processing
* **GTZAN:** 1,000 music clips spanning 10 genres for baseline classification.
* **MTG-Jamendo:** 55,000 multilabel tracks (instruments, moods, genres).
* **Audio Features:** Tempo, Mean Energy, and Mel-Spectrograms processed via **Librosa**, resulting in a 64-dimensional feature vector.

### Classification & Deep Learning
* **Deep Learning Models:** Convolutional Neural Networks (VGG16 architecture) applied to visual spectrograms. The model was trained on a dataset of over 10,000 Deezer tracks for robust audio analysis.
* **Classical ML & Ensemble:** Evaluated Random Forest, KNN, Gradient Boosting, Logistic Regression, and SVMs. We leveraged **Ensemble Learning** techniques combining multiple models to maximize prediction accuracy.

## 📱 User Workflow
1.  **Input:** The user provides an audio recording or a song title via the mobile app.
2.  **Inference:** The API processes the audio and predicts the song's primary genre and mood.
3.  **Curation:** Similar tracks are fetched and matched using the **Deezer API**.
4.  **Output:** A personalized, playable playlist is rendered on the Android app.

## 👥 Credits
* **Institution:** Project carried out at **Télécom Paris**.
* **Supervisors:** Aurian Quelennec & Antonin Gagnere.
