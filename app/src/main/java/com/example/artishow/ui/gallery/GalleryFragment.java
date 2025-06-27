package com.example.artishow.ui.gallery;

import android.media.MediaPlayer;
import android.media.MediaRecorder;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;
import androidx.lifecycle.ViewModelProvider;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.example.artishow.MainActivity;
import com.example.artishow.MusicAdapter;
import com.example.artishow.R;
import com.example.artishow.databinding.FragmentGalleryBinding;
import com.example.artishow.musicItem;
import com.google.android.material.snackbar.Snackbar;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.File;
import java.io.IOException;
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



public class GalleryFragment extends Fragment {

    private FragmentGalleryBinding binding;
    private MediaRecorder recorder;
    private String audioFilePath;
    private MusicAdapter musicAdapter;

    private final Handler handler = new Handler(Looper.getMainLooper());
    private int currentPlayingIndex = -1;

    private MediaPlayer mediaPlayer = new MediaPlayer();

    private List<musicItem> musicList = new ArrayList<>();

    private final OkHttpClient client = new OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build();

    public View onCreateView(@NonNull LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        GalleryViewModel galleryViewModel = new ViewModelProvider(this).get(GalleryViewModel.class);

        binding = FragmentGalleryBinding.inflate(inflater, container, false);
        View root = binding.getRoot();

        final TextView textView = binding.textView2;
        galleryViewModel.getText().observe(getViewLifecycleOwner(), textView::setText);

        RecyclerView recyclerView = root.findViewById(R.id.recyclerView);
        Button recordButton = root.findViewById(R.id.recordButton);
        Button stopRecordButton = root.findViewById(R.id.stopRecordButton);

        recordButton.setOnClickListener(new View.OnClickListener() {
            public void onClick(View view) {
                startRecording();
            }
        });

        stopRecordButton.setOnClickListener(new View.OnClickListener() {
            public void onClick(View view) {
                stopRecording();
                System.out.println("enregistrement terminé!");
            }
        });

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

        recyclerView.setLayoutManager(new LinearLayoutManager(getContext()));
        recyclerView.setAdapter(musicAdapter);

        return root;
    }

    @Override
    public void onDestroyView() {
        super.onDestroyView();
        binding = null;
    }

    private void startRecording() {
        try {
            File outputDir = getContext().getExternalFilesDir(null);
            File outputFile = File.createTempFile("recording_", ".3gp", outputDir);
            audioFilePath = outputFile.getAbsolutePath();

            recorder = new MediaRecorder();
            recorder.setAudioSource(MediaRecorder.AudioSource.MIC);
            recorder.setOutputFormat(MediaRecorder.OutputFormat.THREE_GPP);
            recorder.setOutputFile(audioFilePath);
            recorder.setAudioEncoder(MediaRecorder.AudioEncoder.AMR_NB);

            recorder.prepare();
            recorder.start();

            Toast.makeText(getContext(), "Enregistrement démarré", Toast.LENGTH_SHORT).show();

        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void stopRecording() {
        recorder.stop();
        recorder.release();
        recorder = null;

        Toast.makeText(getContext(), "Enregistrement terminé :\n" + audioFilePath, Toast.LENGTH_LONG).show();
        Toast.makeText(getContext(), "Détermination des caractéristiques et génération de la playlist... :\n" + audioFilePath, Toast.LENGTH_LONG).show();
        sendRecordingToServer(new File(audioFilePath));
    }

    private void sendRecordingToServer(File file) {
        if (!file.exists()) {
            Log.e("FILE", "Le fichier n'existe pas");
            return;
        }

        MultipartBody.Builder builder = new MultipartBody.Builder();
        builder.setType(MultipartBody.FORM);
        builder.addFormDataPart("file", file.getName(), RequestBody.create(MediaType.parse("audio/mpeg"), file));
        RequestBody requestBody = builder.build();

        Request.Builder builder2 = new Request.Builder();
        builder2.url("https://c180-2a04-8ec0-0-240-7103-8004-fb37-32c3.ngrok-free.app/predict");
        builder2.post(requestBody);
        Request request = builder2.build();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                Log.e("API_ERROR", "échec de la requête : " + e);
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                if (response.isSuccessful()) {
                    final String responseData = response.body().string();
                    Log.i("API_RESPONSE", responseData);

                    try {
                        JSONObject jsonObject = new JSONObject(responseData);
                        JSONArray resultatArray = jsonObject.getJSONArray("resultat");

                        List<Long> idList = new ArrayList<>();
                        for (int i = 0; i < resultatArray.length(); i++) {
                            idList.add(resultatArray.getLong(i));
                        }

                        // Appelle une méthode pour récupérer les infos Deezer
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

    private void fetchDeezerInfos(List<Long> idList) {
        // On s'assure que la liste est vide avant de commencer
        musicList.clear();
        // On notifie une première fois pour vider l'ancienne liste de l'écran
        getActivity().runOnUiThread(() -> musicAdapter.notifyDataSetChanged());

        if (idList != null && !idList.isEmpty()) {
            // On commence par la première piste (index 0)
            fetchTrackInfoSequentially(idList, 0);
        }
    }

    private void fetchTrackInfoSequentially(List<Long> idList, int index) {
        // Condition d'arrêt : si on a traité tous les IDs, on arrête.
        if (index >= idList.size()) {
            // Toutes les musiques ont été ajoutées, on peut s'arrêter.
            // L'UI a déjà été mise à jour au fur et à mesure.
            return;
        }

        Long id = idList.get(index);
        String url = "https://api.deezer.com/track/" + id;
        Request request = new Request.Builder().url(url).build();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                Log.e("DEEZER_API", "Erreur requête pour ID " + id, e);
                // On passe quand même au suivant, même en cas d'échec
                fetchTrackInfoSequentially(idList, index + 1);
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                if (response.isSuccessful()) {
                    try {
                        String responseData = response.body().string();
                        JSONObject dataObject = new JSONObject(responseData);

                        // Vérifions que le preview n'est pas vide, Deezer le fait parfois
                        if (dataObject.has("preview") && !dataObject.getString("preview").isEmpty()) {
                            String title = dataObject.getString("title");
                            String artist = dataObject.getJSONObject("artist").getString("name");
                            String previewUrl = dataObject.getString("preview");
                            String coverUrl = dataObject.getJSONObject("album").getString("cover_medium");
                            musicItem item = new musicItem(title, artist, previewUrl, coverUrl);

                            // On ajoute à la liste et on notifie l'UI immédiatement
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
                    // Logue l'erreur pour savoir ce qu'il se passe !
                    Log.e("DEEZER_API", "Réponse non réussie pour ID " + id + ". Code: " + response.code());
                }

                // Important : qu'il y ait succès ou échec, on lance la requête pour l'ID suivant.
                fetchTrackInfoSequentially(idList, index + 1);
            }
        });
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

}