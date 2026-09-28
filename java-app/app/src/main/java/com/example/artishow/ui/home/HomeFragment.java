package com.example.artishow.ui.home;

import android.content.Context;
import android.media.MediaPlayer;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.view.inputmethod.InputMethodManager;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;

import com.example.artishow.MusicAdapter;
import com.example.artishow.databinding.FragmentHomeBinding;
import com.example.artishow.musicItem;
import com.google.android.material.snackbar.Snackbar;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;
import com.example.artishow.network.HttpClientProvider;

public class HomeFragment extends Fragment {

    private FragmentHomeBinding binding;

    // Variables Audio
    private MediaPlayer mediaPlayer;
    private String currentPlayingUrl = "";
    private int currentPlayingIndex = -1;

    // Variables Données
    private MusicAdapter musicAdapter;
    private final List<musicItem> musicList = new ArrayList<>();
    private final Handler handler = new Handler(Looper.getMainLooper());

    // Client Réseau instrumenté avec Datadog
    private final OkHttpClient client = HttpClientProvider.getClient();

    public View onCreateView(@NonNull LayoutInflater inflater,
                             ViewGroup container, Bundle savedInstanceState) {
        binding = FragmentHomeBinding.inflate(inflater, container, false);
        return binding.getRoot();
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        // 1. Initialisation Audio
        if (mediaPlayer == null) mediaPlayer = new MediaPlayer();

        // 2. Setup RecyclerView et Adapter
        musicAdapter = new MusicAdapter(musicList, true, new MusicAdapter.OnItemClickListener() {
            @Override
            public void onPlayClick(musicItem item, int position) {
                handlePlayPause(item, position);
            }

            @Override
            public void onPredictClick(musicItem item, int position) {
                handlePredict(item);
            }
        });

        binding.RecyclerView.setLayoutManager(new LinearLayoutManager(getContext()));
        binding.RecyclerView.setAdapter(musicAdapter);

        // 3. Setup Bouton Recherche
        binding.btnSearchAction.setOnClickListener(v -> performSearch());
    }

    private void performSearch() {
        String query = binding.musicInput.getText().toString().trim();
        if (!query.isEmpty()) {
            try {
                String url = "https://api.deezer.com/search?q=" + URLEncoder.encode(query, "UTF-8");
                fetchPreviewUrl(url);

                // Cacher clavier
                InputMethodManager imm = (InputMethodManager) requireActivity().getSystemService(Context.INPUT_METHOD_SERVICE);
                imm.hideSoftInputFromWindow(binding.getRoot().getWindowToken(), 0);

            } catch (UnsupportedEncodingException e) {
                Log.e("ENCODING", "Erreur encodage", e);
            }
        }
    }

    // --- Audio Logic ---
    private void handlePlayPause(musicItem item, int position) {
        try {
            if (currentPlayingIndex == position && item.getPreviewUrl().equals(currentPlayingUrl)) {
                if (mediaPlayer.isPlaying()) {
                    mediaPlayer.pause();
                    handler.removeCallbacks(updateSeekBarRunnable);
                } else {
                    mediaPlayer.start();
                    handler.post(updateSeekBarRunnable);
                }
            } else {
                if (mediaPlayer.isPlaying()) mediaPlayer.stop();
                mediaPlayer.reset();
                mediaPlayer.setDataSource(item.getPreviewUrl());
                mediaPlayer.prepare();
                mediaPlayer.start();
                currentPlayingIndex = position;
                currentPlayingUrl = item.getPreviewUrl();
                handler.post(updateSeekBarRunnable);
            }
        } catch (IOException e) {
            Log.e("PLAYER", "Erreur lecture", e);
            Snackbar.make(binding.getRoot(), "Erreur lecture audio", Snackbar.LENGTH_SHORT).show();
        }
    }

    Runnable updateSeekBarRunnable = new Runnable() {
        @Override
        public void run() {
            if (mediaPlayer != null && mediaPlayer.isPlaying() && currentPlayingIndex != -1) {
                musicAdapter.updateSeekBar(currentPlayingIndex, mediaPlayer.getCurrentPosition());
                handler.postDelayed(this, 500);
            }
        }
    };

    // --- API & Network Logic ---
    private void handlePredict(musicItem item) {
        if (item.getPreviewUrl() != null && !item.getPreviewUrl().isEmpty()) {
            Snackbar.make(binding.getRoot(), "Téléchargement et analyse...", Snackbar.LENGTH_SHORT).show();
            downloadMp3AndSend(item.getPreviewUrl());
        } else {
            Snackbar.make(binding.getRoot(), "Aucun preview disponible", Snackbar.LENGTH_SHORT).show();
        }
    }

    private void fetchPreviewUrl(String url) {
        Request request = new Request.Builder().url(url).build();
        client.newCall(request).enqueue(new Callback() {
            public void onFailure(@NonNull Call call, @NonNull IOException e) { Log.e("API", "Echec", e); }

            public void onResponse(@NonNull Call call, @NonNull Response response) throws IOException {
                if (response.isSuccessful()) {
                    try {
                        String responseData = response.body().string();
                        JSONObject jsonObject = new JSONObject(responseData);
                        JSONArray dataArray = jsonObject.getJSONArray("data");

                        musicList.clear();
                        for (int i = 0; i < Math.min(10, dataArray.length()); i++) {
                            JSONObject obj = dataArray.getJSONObject(i);
                            musicItem item = new musicItem(
                                    obj.getString("title"),
                                    obj.getJSONObject("artist").getString("name"),
                                    obj.getString("preview"),
                                    obj.getJSONObject("album").getString("cover_medium")
                            );
                            musicList.add(item);
                        }
                        if (getActivity() != null) {
                            getActivity().runOnUiThread(() -> musicAdapter.notifyDataSetChanged());
                        }
                    } catch (JSONException e) { Log.e("JSON", "Erreur parsing", e); }
                }
            }
        });
    }

    private void downloadMp3AndSend(String url) {
        Request request = new Request.Builder().url(url).build();

        client.newCall(request).enqueue(new Callback() {
            public void onFailure(@NonNull Call call, @NonNull IOException e) { Log.e("DL", "Fail", e); }

            public void onResponse(@NonNull Call call, @NonNull Response response) throws IOException {
                if (response.isSuccessful() && response.body() != null) {
                    File outputFile = new File(requireContext().getCacheDir(), "preview_" + System.currentTimeMillis() + ".mp3");
                    try (InputStream is = response.body().byteStream();
                         OutputStream os = new FileOutputStream(outputFile)) {
                        byte[] buffer = new byte[4096];
                        int bytesRead;
                        while ((bytesRead = is.read(buffer)) != -1) os.write(buffer, 0, bytesRead);
                        os.flush();
                    } catch (IOException e) {
                        Log.e("DL", "Erreur écriture fichier", e);
                        return;
                    }

                    if (getActivity() != null)
                        getActivity().runOnUiThread(() -> sendAudioToServer(outputFile));
                }
            }
        });
    }

    private void sendAudioToServer(File file) {
        MultipartBody.Builder builder = new MultipartBody.Builder().setType(MultipartBody.FORM);
        builder.addFormDataPart("file", file.getName(), RequestBody.create(MediaType.parse("audio/mpeg"), file));
        Request request = new Request.Builder()
                .url("https://wassleboss-artishow-api.hf.space/predict")
                .post(builder.build())
                .build();

        client.newCall(request).enqueue(new Callback() {
            public void onFailure(@NonNull Call call, @NonNull IOException e) {
                if (getActivity() != null)
                    getActivity().runOnUiThread(() -> Snackbar.make(binding.getRoot(), "Erreur Serveur", Snackbar.LENGTH_SHORT).show());
            }

            public void onResponse(@NonNull Call call, @NonNull Response response) throws IOException {
                if (response.isSuccessful()) {
                    try {
                        JSONObject jsonObject = new JSONObject(response.body().string());
                        JSONArray resultatArray = jsonObject.getJSONArray("resultat");
                        List<Long> idList = new ArrayList<>();
                        for (int i = 0; i < resultatArray.length(); i++) idList.add(resultatArray.getLong(i));
                        fetchDeezerInfos(idList);
                    } catch (JSONException e) { Log.e("JSON", "Error", e); }
                }
            }
        });
    }

    private void fetchDeezerInfos(List<Long> idList) {
        musicList.clear();
        if (getActivity() != null) getActivity().runOnUiThread(() -> musicAdapter.notifyDataSetChanged());
        if (idList != null && !idList.isEmpty()) fetchTrackInfoSequentially(idList, 0);
    }

    private void fetchTrackInfoSequentially(List<Long> idList, int index) {
        if (index >= idList.size()) return;
        String url = "https://api.deezer.com/track/" + idList.get(index);

        client.newCall(new Request.Builder().url(url).build()).enqueue(new Callback() {
            public void onFailure(@NonNull Call call, @NonNull IOException e) { fetchTrackInfoSequentially(idList, index + 1); }

            public void onResponse(@NonNull Call call, @NonNull Response response) throws IOException {
                if (response.isSuccessful()) {
                    try {
                        JSONObject obj = new JSONObject(response.body().string());
                        if (obj.has("preview")) {
                            musicItem item = new musicItem(
                                    obj.getString("title"),
                                    obj.getJSONObject("artist").getString("name"),
                                    obj.getString("preview"),
                                    obj.getJSONObject("album").getString("cover_medium")
                            );
                            if (getActivity() != null) {
                                getActivity().runOnUiThread(() -> {
                                    musicList.add(item);
                                    musicAdapter.notifyItemInserted(musicList.size() - 1);
                                });
                            }
                        }
                    } catch (JSONException e) { Log.e("DEEZER", "Error", e); }
                }
                fetchTrackInfoSequentially(idList, index + 1);
            }
        });
    }

    @Override
    public void onDestroyView() {
        super.onDestroyView();
        if (mediaPlayer != null) {
            mediaPlayer.release();
            mediaPlayer = null;
        }
        handler.removeCallbacks(updateSeekBarRunnable);
        binding = null;
    }
}
