package com.example.artishow;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.SeekBar;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.bumptech.glide.Glide;

import java.util.List;

public class MusicAdapter extends RecyclerView.Adapter<MusicAdapter.MusicViewHolder> {

    private final List<musicItem> musicList;
    private final OnItemClickListener listener;
    private boolean showPredictButton;
    public interface OnItemClickListener {
        void onPlayClick(musicItem item, int position);
        void onPredictClick(musicItem item, int position);
    }

    public void updateSeekBar(int position, int progressMs) {
        if (position >= 0 && position < musicList.size()) {
            musicItem item = musicList.get(position);
            item.setCurrentProgress(progressMs);
            notifyItemChanged(position);
        }
    }
    public MusicAdapter(List<musicItem> musicList, boolean showPredictButton, OnItemClickListener listener) {
        this.musicList = musicList;
        this.listener = listener;
        this.showPredictButton = showPredictButton;
    }

    @NonNull
    @Override
    public MusicViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_music_card, parent, false);
        return new MusicViewHolder(itemView);

    }

    @Override
    public void onBindViewHolder(@NonNull MusicViewHolder holder, int position) {
        musicItem item = musicList.get(position);
        holder.bind(item, listener, position);
        holder.seekBar.setMax(30000); // car preview = 30s
        holder.seekBar.setProgress(item.getCurrentProgress());

        Glide.with(holder.itemView.getContext()).
                load(item.getCoverUrl())
                .into(holder.coverImageView);
    }

    @Override
    public int getItemCount() {
        return musicList.size();
    }

    static class MusicViewHolder extends RecyclerView.ViewHolder {

        TextView title, artist;
        SeekBar seekBar;
        ImageButton playButton;

        Button predictButton;

        ImageView coverImageView;

        public MusicViewHolder(@NonNull View itemView) {
            super(itemView);
            title = itemView.findViewById(R.id.musicTitle);
            artist = itemView.findViewById(R.id.musicArtist);
            seekBar = itemView.findViewById(R.id.seekBar4);
            playButton = itemView.findViewById(R.id.playButton); //
            coverImageView = itemView.findViewById(R.id.imageView4);
            predictButton = itemView.findViewById(R.id.predictButton);
        }

        public void bind(musicItem item, OnItemClickListener listener, int position) {
            title.setText(item.title);
            artist.setText(item.artist);
            playButton.setOnClickListener(v -> listener.onPlayClick(item, position));
            predictButton.setOnClickListener(v -> listener.onPredictClick(item, position));
        }
    }
}
