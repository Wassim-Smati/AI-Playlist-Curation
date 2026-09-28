package com.example.artishow.network;

import android.util.Log;

import com.datadog.android.okhttp.DatadogInterceptor;
import com.datadog.android.okhttp.trace.TracingInterceptor;

import java.util.Arrays;
import java.util.List;
import java.util.concurrent.TimeUnit;

import okhttp3.OkHttpClient;

/**
 * Fournisseur centralisé pour OkHttpClient avec instrumentation Datadog.
 * Injecte automatiquement les en-têtes de traçage (APM Distributed Tracing)
 * pour relier les requêtes mobiles aux traces du backend Flask.
 */
public class HttpClientProvider {

    private static final String TAG = "HttpClientProvider";
    private static volatile OkHttpClient sClient;

    // Hôtes pour lesquels injecter les en-têtes de traçage distribué Datadog
    private static final List<String> TRACED_HOSTS = Arrays.asList(
            "wassleboss-artishow-api.hf.space",
            "*.hf.space",
            "8d933c23a627.ngrok-free.app",
            "*.ngrok-free.app",
            "api.deezer.com",
            "10.0.2.2",
            "localhost"
    );

    private HttpClientProvider() {
    }

    public static OkHttpClient getClient() {
        if (sClient == null) {
            synchronized (HttpClientProvider.class) {
                if (sClient == null) {
                    sClient = buildClient();
                }
            }
        }
        return sClient;
    }

    private static OkHttpClient buildClient() {
        OkHttpClient.Builder builder = new OkHttpClient.Builder()
                .connectTimeout(30, TimeUnit.SECONDS)
                .writeTimeout(30, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS);

        try {
            // Intercepteur Datadog pour le suivi des ressources réseau dans RUM
            builder.addInterceptor(new DatadogInterceptor.Builder(TRACED_HOSTS).build());

            // Intercepteur de traçage réseau (Distributed Tracing APM)
            builder.addNetworkInterceptor(new TracingInterceptor.Builder(TRACED_HOSTS).build());

            Log.i(TAG, "OkHttpClient configuré avec les intercepteurs Datadog.");
        } catch (Throwable t) {
            Log.w(TAG, "Impossible d'ajouter les intercepteurs Datadog à OkHttpClient (mode dégradé): " + t.getMessage());
        }

        return builder.build();
    }
}
