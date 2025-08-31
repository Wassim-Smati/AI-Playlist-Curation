package com.example.artishow;

import static android.app.PendingIntent.getActivity;
import static java.security.AccessController.getContext;

import android.Manifest;
import android.content.pm.PackageManager;
import android.media.MediaRecorder;
import android.os.Handler;
import android.os.Looper;
import android.widget.EditText;
import android.media.MediaPlayer;
import android.os.Bundle;
import android.view.View;
import android.view.Menu;
import java.io.File;
import com.google.android.material.snackbar.Snackbar;
import com.google.android.material.navigation.NavigationView;
import android.widget.Button;

import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.navigation.NavController;
import androidx.navigation.Navigation;
import androidx.navigation.ui.AppBarConfiguration;
import androidx.navigation.ui.NavigationUI;
import androidx.drawerlayout.widget.DrawerLayout;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;

import android.util.Log;
import android.widget.TextView;
import android.widget.Toast;


import com.example.artishow.databinding.ActivityMainBinding;


public class MainActivity extends AppCompatActivity {

    private AppBarConfiguration mAppBarConfiguration;
    private ActivityMainBinding binding;
    private MediaPlayer mediaPlayer = new MediaPlayer();
    private int currentPlayingIndex = -1;
    private TextView textResult;

    private RecyclerView recyclerView;
    private MusicAdapter musicAdapter;
    private List<musicItem> musicList = new ArrayList<>();

    private final Handler handler = new Handler(Looper.getMainLooper());

    private final OkHttpClient client = new OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build();

    @Override
    protected void onCreate(Bundle savedInstanceState) {

        super.onCreate(savedInstanceState);
        binding = ActivityMainBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());
        setSupportActionBar(binding.appBarMain.toolbar);
        EditText searchInput = findViewById (R.id.musicInput);
        recyclerView = findViewById(R.id.RecyclerView);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        recyclerView.setAdapter(musicAdapter);
        System.out.println("je suis la");
        Button searchButton = findViewById(R.id.searchButton);
        textResult = findViewById(R.id.text_result);
        checkPermissions();

        searchButton.setOnClickListener(new View.OnClickListener(){

            @Override
            public void onClick(View view){
                String query = searchInput.getText().toString().trim();
                if (!query.isEmpty()){
                    try{
                        String url = "https://api.deezer.com/search?q=" + URLEncoder.encode(query, "UTF-8");
                        fetchPreviewUrl(url);
                    } catch (UnsupportedEncodingException e) {
                        Log.e("ENCODING", "Erreur encodage", e);
                    }}
            }}
        );


        DrawerLayout drawer = binding.drawerLayout;
        NavigationView navigationView = binding.navView;
        mAppBarConfiguration = new AppBarConfiguration.Builder(
                R.id.nav_home, R.id.nav_gallery, R.id.nav_slideshow)
                .setOpenableLayout(drawer)
                .build();
        NavController navController = Navigation.findNavController(this, R.id.nav_host_fragment_content_main);
        NavigationUI.setupActionBarWithNavController(this, navController, mAppBarConfiguration);
        NavigationUI.setupWithNavController(navigationView, navController);

        musicAdapter = new MusicAdapter(musicList, true,  new MusicAdapter.OnItemClickListener() {
            @Override
            public void onPlayClick(musicItem item, int position) {
                handlePlayPause(item, position);
            }

            public void onPredictClick(musicItem item, int position) {
                System.out.println("Bonjour");
                handlePredict(item, position);
            }
        });

        recyclerView.setAdapter(musicAdapter);

    }

    private void fetchPreviewUrl(String url){
        Request request = new Request.Builder().url(url).build();

        client.newCall(request).enqueue(new Callback() {
            public void onFailure(Call call, IOException e){
                Log.e("API_ERROR", "échec de la requête : " + e);
            }

            public void onResponse(Call call, Response response){
                if (response.isSuccessful()){
                    try {
                        String responseData = response.body().string();
                        JSONObject jsonObject = new JSONObject(responseData);
                        JSONArray dataArray = jsonObject.getJSONArray("data");

                        musicList.clear();
                        for (int i = 0; i < Math.min(10, dataArray.length()); i++){
                            JSONObject dataObject = dataArray.getJSONObject(i);
                            String title = dataObject.getString("title");
                            String artist = dataObject.getJSONObject("artist").getString("name");
                            String previewUrl = dataObject.getString("preview");
                            String coverUrl = dataObject.getJSONObject("album").getString("cover_medium");

                            musicItem item = new musicItem(title, artist, previewUrl, coverUrl);
                            System.out.println(title);
                            musicList.add(item);

                        } runOnUiThread(() -> musicAdapter.notifyDataSetChanged());

                    } catch (Exception e) {
                        Log.e("JSON_ERROR", "Erreur parsing JSON", e);
                    }
                } else {
                    Log.e("API_ERROR", "Code d'erreur : " + response.code());
                }
            }
        });
    }

    private void downloadMp3AndSend(String url){

        File outputFile = new File(getExternalFilesDir(null), "preview.mp3");
        Request request = new Request.Builder().url(url).build();

        client.newCall(request).enqueue(new Callback() {
            public void onFailure(Call call, IOException e){
                Log.e("DOWNLOAD", "échec du téléchargement : " + e);
            }

            public void onResponse(Call call, Response response) throws IOException {

                InputStream inputStream = null;
                OutputStream outputStream = null;

                if (response.isSuccessful()){
                    try {
                        inputStream = response.body().byteStream();
                        outputStream = new FileOutputStream(outputFile);
                        byte[] buffer = new byte [4096];

                        int bytesRead;
                        while ((bytesRead = inputStream.read(buffer)) != -1){
                            outputStream.write(buffer, 0, bytesRead);
                        }

                        outputStream.close();
                        inputStream.close();

                        runOnUiThread(() -> sendAudioToServer(outputFile));
                    } catch (IOException e) {
                        Log.e("DOWNLOAD", "Erreur pendant l'écriture du fichier", e);
                    } finally {
                        if (inputStream != null) inputStream.close();
                        if (outputStream != null) outputStream.close();
                    }
                }
            }
        });
    }

    private void playPreview(String url){
        if (mediaPlayer != null){
            mediaPlayer.stop();
            mediaPlayer.release();
        }
        mediaPlayer = new MediaPlayer();
        try {
            mediaPlayer.setDataSource(url);
            mediaPlayer.prepare();
            mediaPlayer.start();
            Snackbar.make(binding.getRoot(), "Lecture du preview", Snackbar.LENGTH_LONG).show();
        } catch (IOException e){
            Log.e("PLAYER", "Erreur lecture preview", e);
            Snackbar.make(binding.getRoot(), "Erreur lors de la lecture", Snackbar.LENGTH_SHORT).show();
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

    private void handlePredict(musicItem item, int position) {
        if (item.getPreviewUrl() != null && !item.getPreviewUrl().isEmpty()) {
            System.out.println("Je suis dans handlePredict");
            downloadMp3AndSend(item.getPreviewUrl());
        } else {
            Snackbar.make(binding.getRoot(), "Aucun preview disponible", Snackbar.LENGTH_SHORT).show();
        }

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

    private void sendAudioToServer(File file) {
        System.out.println("je suis dans sendAudioToServer");
        if (!file.exists()) {
            Log.e("FILE", "Le fichier n'existe pas");
            return;
        }

        MultipartBody.Builder builder = new MultipartBody.Builder();
        builder.setType(MultipartBody.FORM);
        builder.addFormDataPart("file", file.getName(), RequestBody.create(MediaType.parse("audio/mpeg"), file));
        RequestBody requestBody = builder.build();

        Request.Builder builder2 = new Request.Builder();
        builder2.url("https://8d933c23a627.ngrok-free.app/predict");
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
                        fetchDeezerInfos(idList);

                    } catch (JSONException e) {
                        e.printStackTrace();
                    }

                } else {
                    Log.e("API_ERROR", "Code d'erreur : " + response.code());
                }
            }
        });
    }



    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.main, menu);
        return true;
    }

    @Override
    public boolean onSupportNavigateUp() {
        NavController navController = Navigation.findNavController(this, R.id.nav_host_fragment_content_main);
        return NavigationUI.navigateUp(navController, mAppBarConfiguration)
                || super.onSupportNavigateUp();
    }

    private void checkPermissions() {
        if (ContextCompat.checkSelfPermission(  this, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED ||
                ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {

            ActivityCompat.requestPermissions(this,
                    new String[]{Manifest.permission.RECORD_AUDIO, Manifest.permission.WRITE_EXTERNAL_STORAGE}, 200);
        }
    }

    private void fetchDeezerInfos(List<Long> idList) {
        musicList.clear();
        runOnUiThread(() -> musicAdapter.notifyDataSetChanged());

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

                            runOnUiThread(() -> {
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