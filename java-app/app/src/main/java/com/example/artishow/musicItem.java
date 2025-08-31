package com.example.artishow;

public class musicItem {
    public String title;
    public String artist;
    private String previewUrl;
    private String coverUrl;

    public musicItem(String title, String artist, String previewUrl, String coverUrl){
        this.title = title;
        this.artist = artist;
        this.previewUrl = previewUrl;
        this.coverUrl = coverUrl;
    }

    private int currentProgress;

    public int getCurrentProgress() {
        return currentProgress;
    }

    public void setCurrentProgress(int currentProgress) {
        this.currentProgress = currentProgress;
    }


    public String getPreviewUrl() {
        return previewUrl;
    }

    public String getCoverUrl() {
        return coverUrl;
    }
}
