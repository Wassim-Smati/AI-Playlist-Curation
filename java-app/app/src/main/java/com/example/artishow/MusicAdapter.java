package com.example.artishow;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
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

    public MusicAdapter(List<musicItem> musicList, boolean showPredictButton, OnItemClickListener listener) {
        this.musicList = musicList;
        this.listener = listener;
        this.showPredictButton = showPredictButton;
    }

    public void updateSeekBar(int position, int progressMs) {
        if (position >= 0 && position < musicList.size()) {
            musicList.get(position).setCurrentProgress(progressMs);
            notifyItemChanged(position);
        }
    }

    @NonNull
    @Override
    public MusicViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        // Utilise bien le nom de ton fichier XML sublimé
        View itemView = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_music_card, parent, false);
        return new MusicViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(@NonNull MusicViewHolder holder, int position) {
        musicItem item = musicList.get(position);

        holder.musicTitle.setText(item.title);
        holder.musicArtist.setText(item.artist);
        holder.seekBar4.setMax(30000); // 30 secondes
        holder.seekBar4.setProgress(item.getCurrentProgress());

        // Gestion de la visibilité du bouton Predict
        holder.predictButton.setVisibility(showPredictButton ? View.VISIBLE : View.GONE);

        // Chargement de l'image avec Glide
        Glide.with(holder.itemView.getContext())
                .load(item.getCoverUrl())
                .placeholder(android.R.drawable.ic_menu_report_image) // Image par défaut
                .into(holder.imageView4);

        // Click listeners
        holder.playButton.setOnClickListener(v -> listener.onPlayClick(item, position));
        holder.predictButton.setOnClickListener(v -> listener.onPredictClick(item, position));
    }

    @Override
    public int getItemCount() {
        return musicList.size();
    }

    // LA CLASSE VIEWHOLDER NETTOYÉE
    static class MusicViewHolder extends RecyclerView.ViewHolder {
        TextView musicTitle, musicArtist;
        SeekBar seekBar4;
        Button playButton, predictButton;
        ImageView imageView4;

        public MusicViewHolder(@NonNull View itemView) {
            super(itemView);
            musicTitle = itemView.findViewById(R.id.musicTitle);
            musicArtist = itemView.findViewById(R.id.musicArtist);
            imageView4 = itemView.findViewById(R.id.imageView4);
            seekBar4 = itemView.findViewById(R.id.seekBar4);
            playButton = itemView.findViewById(R.id.playButton);
            predictButton = itemView.findViewById(R.id.predictButton);
        }
    }
}