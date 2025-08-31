package com.example.artishow.ui.slideshow;

import android.icu.text.StringPrepParseException;
import android.media.MediaPlayer;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;

import com.example.artishow.MusicAdapter;
import com.example.artishow.R;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;
import androidx.lifecycle.ViewModelProvider;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.example.artishow.databinding.FragmentSlideshowBinding;
import com.example.artishow.musicItem;
import com.google.android.material.snackbar.Snackbar;
import com.google.android.material.textfield.TextInputEditText;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.File;
import java.io.IOException;
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

public class SlideshowFragment extends Fragment {

    private MusicAdapter musicAdapter;

    private int currentPlayingIndex = -1;

    private MediaPlayer mediaPlayer = new MediaPlayer();

    private List<musicItem> musicList = new ArrayList<>();

    private TextView textMoodPhraseResult;

    private final Handler handler = new Handler(Looper.getMainLooper());

    private final OkHttpClient client = new OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build();
    private FragmentSlideshowBinding binding;

    public View onCreateView(@NonNull LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        SlideshowViewModel slideshowViewModel = new ViewModelProvider(this).get(SlideshowViewModel.class);

        binding = FragmentSlideshowBinding.inflate(inflater, container, false);
        View root = binding.getRoot();

        final TextView textView = binding.textView3;
        Button searchButton = root.findViewById(R.id.searchButton2);
        TextInputEditText phraseInput = root.findViewById(R.id.phraseInput);
        textMoodPhraseResult = root.findViewById(R.id.textMoodPhraseResult);
        RecyclerView recyclerMoodPhrase = root.findViewById(R.id.recyclerMoodPhrase);

        searchButton.setOnClickListener(new View.OnClickListener() {
            public void onClick(View view) {
                String query = phraseInput.getText().toString();
                if (!query.isEmpty()){
                    stringToServer(query);
                }
            }
        }
        );

        musicAdapter = new MusicAdapter(musicList, false, new MusicAdapter.OnItemClickListener() {
            @Override
            public void onPlayClick(musicItem item, int position) {
                handlePlayPause(item, position);
            }

            public void onPredictClick(musicItem item, int position) {
                System.out.println("t'es pas sensé voir ce bouton");
            }
        }
        );

        recyclerMoodPhrase.setLayoutManager(new LinearLayoutManager(getContext()));
        recyclerMoodPhrase.setAdapter(musicAdapter);

        slideshowViewModel.getText().observe(getViewLifecycleOwner(), textView::setText);
        return root;
    }

    private void stringToServer(String query) {
        if (query.isEmpty()) {
            Log.e("STRING", "La phrase est vide");
            return;
        }

        musicList.clear();
        getActivity().runOnUiThread(() -> musicAdapter.notifyDataSetChanged());

        MultipartBody.Builder builder = new MultipartBody.Builder();
        builder.setType(MultipartBody.FORM);
        builder.addFormDataPart("string", query);
        RequestBody requestBody = builder.build();
        Request.Builder builder2 = new Request.Builder();
        builder2.url("https://8d933c23a627.ngrok-free.app/moodPhrasePredict");
        builder2.post(requestBody);
        Request request = builder2.build();

        textMoodPhraseResult.setText("Chargement de la playlist...");

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                Log.e("API_ERROR", "échec de la requête : " + e);
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                if (response.isSuccessful()) {
                    requireActivity().runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            textMoodPhraseResult.setText("");
                        }
                    });
                    final String responseData = response.body().string();
                    Log.i("API_RESPONSE", responseData);
                    try {
                        JSONObject jsonObject = new JSONObject(responseData);
                        JSONArray resultatArray = jsonObject.getJSONArray("resultat");

                        List<Long> idList = new ArrayList<>();
                        for (int i = 0; i < resultatArray.length(); i++) {
                            idList.add(resultatArray.getLong(i));
                        }
                        fetchDeezerInfos(idList);
                    } catch (JSONException e) {
                        e.printStackTrace();
                    };
                } else {
                    Log.e("API_ERROR", "Code d'erreur : " + response.code());
                }
            }
        });
    }

    @Override
    public void onDestroyView() {
        super.onDestroyView();
        binding = null;
    }
    private void handlePlayPause(musicItem item, int position) {
        try {
            if (currentPlayingIndex == position) {
                if (mediaPlayer.isPlaying()) {
                    mediaPlayer.pause();
                    handler.removeCallbacks(updateSeekBarRunnable);
                } else {
                    System.out.println("debut Musique");
                    mediaPlayer.start();
                    handler.post(updateSeekBarRunnable);
                }
            } else {
                mediaPlayer.reset();
                mediaPlayer.setDataSource(item.getPreviewUrl());
                mediaPlayer.prepare();
                mediaPlayer.start();
                currentPlayingIndex = position;
                handler.post(updateSeekBarRunnable);
            }
        } catch (IOException e) {
            Log.e("PLAYER", "Erreur de lecture", e);
            Snackbar.make(binding.getRoot(), "Erreur de lecture", Snackbar.LENGTH_SHORT).show();
        }
    }

    Runnable updateSeekBarRunnable = new Runnable() {
        @Override
        public void run() {
            if (mediaPlayer != null && mediaPlayer.isPlaying() && currentPlayingIndex != -1) {
                int position = mediaPlayer.getCurrentPosition();
                System.out.println(currentPlayingIndex);
                musicAdapter.updateSeekBar(currentPlayingIndex, position);
                handler.postDelayed(this, 500);
            }
        }
    };

    private void fetchDeezerInfos(List<Long> idList) {
        musicList.clear();
        getActivity().runOnUiThread(() -> musicAdapter.notifyDataSetChanged());

        if (idList != null && !idList.isEmpty()) {
            fetchTrackInfoSequentially(idList, 0);
        }
    }

    private void fetchTrackInfoSequentially(List<Long> idList, int index) {
        if (index >= idList.size()) {
            return;
        }

        Long id = idList.get(index);
        String url = "https://api.deezer.com/track/" + id;
        Request request = new Request.Builder().url(url).build();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                Log.e("DEEZER_API", "Erreur requête pour ID " + id, e);
                fetchTrackInfoSequentially(idList, index + 1);
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                if (response.isSuccessful()) {
                    try {
                        String responseData = response.body().string();
                        JSONObject dataObject = new JSONObject(responseData);

                        if (dataObject.has("preview") && !dataObject.getString("preview").isEmpty()) {
                            String title = dataObject.getString("title");
                            String artist = dataObject.getJSONObject("artist").getString("name");
                            String previewUrl = dataObject.getString("preview");
                            String coverUrl = dataObject.getJSONObject("album").getString("cover_medium");
                            musicItem item = new musicItem(title, artist, previewUrl, coverUrl);

                            getActivity().runOnUiThread(() -> {
                                musicList.add(item);
                                musicAdapter.notifyItemInserted(musicList.size() - 1);
                            });
                        } else {
                            Log.w("DEEZER_API", "Track ID " + id + " n'a pas de preview URL.");
                        }

                    } catch (JSONException e) {
                        Log.e("DEEZER_API", "Erreur parsing JSON pour ID " + id, e);
                    }
                } else {
                    Log.e("DEEZER_API", "Réponse non réussie pour ID " + id + ". Code: " + response.code());
                }
                fetchTrackInfoSequentially(idList, index + 1);
            }
        });
    }

}