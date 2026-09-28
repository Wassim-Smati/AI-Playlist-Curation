package com.example.artishow;

import android.app.Application;
import android.util.Log;

import com.datadog.android.Datadog;
import com.datadog.android.DatadogSite;
import com.datadog.android.core.configuration.Configuration;
import com.datadog.android.privacy.TrackingConsent;
import com.datadog.android.rum.Rum;
import com.datadog.android.rum.RumConfiguration;
import com.datadog.android.rum.tracking.FragmentViewTrackingStrategy;
import com.datadog.android.trace.Trace;
import com.datadog.android.trace.TraceConfiguration;

public class ArtishowApplication extends Application {

    private static final String TAG = "ArtishowApplication";

    // =========================================================================
    // Configurations Datadog Android
    // Remplacez ces valeurs par celles générées sur votre dashboard Datadog :
    // UX Monitoring > RUM Applications > New Application (Android)
    // =========================================================================
    public static final String DATADOG_CLIENT_TOKEN = "pub5cd57ac1202fabc21c0c8a478c2888c5";
    public static final String DATADOG_APPLICATION_ID = "9f493ba3-d7d1-48f2-b7b0-d1d5b2894dc2";
    public static final String REMOTE_CONFIG_ID = "848b15fe-ed8c-4b5c-b2d1-c4d1bb9ce1bc";
    public static final String ENVIRONMENT = "production";  
    public static final String APP_VARIANT = "release";
    public static final DatadogSite DATADOG_SITE = DatadogSite.US5; // Votre compte est hébergé sur le datacenter US5

    @Override
    public void onCreate() {
        super.onCreate();

        initializeDatadog();
    }

    private void initializeDatadog() {
        try {
            // 1. Configuration principale de l'agent Datadog
            Configuration configuration = new Configuration.Builder(
                    DATADOG_CLIENT_TOKEN,
                    ENVIRONMENT,
                    APP_VARIANT
            )
            .setRemoteConfigurationId(REMOTE_CONFIG_ID)
            .useSite(DATADOG_SITE)
            .build();

            // 2. Initialisation globale avec consentement de suivi RGPD
            Datadog.initialize(this, configuration, TrackingConsent.GRANTED);

            // 3. Activation de RUM (Real User Monitoring) et suivi automatique des Fragments
            RumConfiguration rumConfiguration = new RumConfiguration.Builder(DATADOG_APPLICATION_ID)
                    .trackUserInteractions()
                    .useViewTrackingStrategy(new FragmentViewTrackingStrategy(true))
                    .build();
            Rum.enable(rumConfiguration);

            // 4. Activation du traçage distribué APM
            TraceConfiguration traceConfiguration = new TraceConfiguration.Builder().build();
            Trace.enable(traceConfiguration);

            Log.i(TAG, "Datadog SDK initialisé avec succès");
        } catch (Exception e) {
            Log.e(TAG, "Erreur lors de l'initialisation de Datadog SDK: " + e.getMessage(), e);
        }
    }
}
