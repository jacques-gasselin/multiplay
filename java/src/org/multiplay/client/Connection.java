package org.multiplay.client;

import org.multiplay.ConnectionToken;
import org.multiplay.DeviceToken;
import org.multiplay.GameToken;

import com.owlike.genson.Genson;
import com.owlike.genson.GensonBuilder;
import org.multiplay.LocalPlayerToken;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionStage;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.ForkJoinPool;

public abstract class Connection {
    private final GameToken gameToken;
    private final DeviceToken deviceToken;
    private final URL serverURL;
    private final ExecutorService executor;
    private ConnectionToken connectionToken = null;
    private boolean verboseLoggingEnabled = false;

    private Genson jsonDeserializer = null;

    protected Connection(GameToken gameToken, DeviceToken deviceToken, URL serverURL, ExecutorService executor) {
        this.gameToken = gameToken;
        this.deviceToken = deviceToken;
        this.serverURL = serverURL;
        if (executor != null) {
            this.executor = executor;
        }
        else {
            this.executor = ForkJoinPool.commonPool();
        }
        jsonDeserializer = new GensonBuilder()
                .useClassMetadata(true)
                .useRuntimeType(true)
                .create();
    }

    public void close() {
        executor.shutdown();
    }

    private static final class ConnectionResponse {
        private String connectionToken = null;

        public void setConnectionToken(String connectionToken) {
            this.connectionToken = connectionToken;
        }

        public String getConnectionToken() {
            return this.connectionToken;
        }

        public String toString() {
            return "connectionToken: " + connectionToken;
        }
    }

    /**
     * Connect to the game's instance of the multiplay service.
     * @return {Promise} a promise that is fulfilled when the game is connected.
     */
    public CompletionStage<Connection> connectAsync() {
        if (isVerboseLoggingEnabled()) {
            System.out.println("Connection.connectAsync()");
        }
        String protocol = serverURL.getProtocol();
        String host = serverURL.getHost();
        int port = serverURL.getPort();
        return CompletableFuture.supplyAsync(() -> {
            HttpURLConnection conn = null;
            try {
                URL connectUrl = new URL(protocol, host, port, "/connect.json?game=" + gameToken.toString());
                if (isVerboseLoggingEnabled()) {
                    System.out.println("Connecting to server at " + connectUrl);
                }
                conn = (HttpURLConnection) connectUrl.openConnection();
                if (isVerboseLoggingEnabled()) {
                    System.out.println("conn: " + conn);
                }
                // grab the response as JSON and get the connection token
                BufferedReader reader = new BufferedReader(new InputStreamReader(conn.getInputStream()));
                try {
                    ConnectionResponse response = new ConnectionResponse();
                    jsonDeserializer.deserializeInto(reader, response);
                    if (isVerboseLoggingEnabled()) {
                        System.out.println(response);
                    }
                    connectionToken = new ConnectionToken(response.getConnectionToken());
                }
                finally {
                    reader.close();
                }
            }
            catch (IOException e) {
                e.printStackTrace(System.err);
            }
            finally {
                if (conn != null) {
                    conn.disconnect();
                }
            }
            return this;
        });
    }

    private static final class LoginResponse {
        private String localPlayerToken = null;
        private String displayName = null;
        private String friendCode = null;
        private boolean authenticated = false;

        public String getLocalPlayerToken() {
            return localPlayerToken;
        }

        public void setLocalPlayerToken(String localPlayerToken) {
            this.localPlayerToken = localPlayerToken;
        }

        public String getDisplayName() {
            return displayName;
        }

        public void setDisplayName(String displayName) {
            this.displayName = displayName;
        }

        public String getFriendCode() {
            return friendCode;
        }

        public void setFriendCode(String friendCode) {
            this.friendCode = friendCode;
        }

        public boolean isAuthenticated() {
            return authenticated;
        }

        public void setAuthenticated(boolean authenticated) {
            this.authenticated = authenticated;
        }

        public String toString() {
            return "localPlayerToken: " + localPlayerToken + ", displayName: " + displayName + ", friendCode: " + friendCode + ", authenticated: " + authenticated;
        }
    }

    public LocalPlayer login() {
        if (isVerboseLoggingEnabled()) {
            System.out.println("Connection.login()");
        }

        String protocol = serverURL.getProtocol();
        String host = serverURL.getHost();
        int port = serverURL.getPort();

        HttpURLConnection conn = null;
        LocalPlayer localPlayer = null;
        try {
            URL loginUrl = new URL(protocol, host, port, "/login.json?connection=" + connectionToken.toString() + "&localDevice=" + deviceToken.toString());
            if (isVerboseLoggingEnabled()) {
                System.out.println("Logging in at " + loginUrl);
            }
            conn = (HttpURLConnection) loginUrl.openConnection();
            if (isVerboseLoggingEnabled()) {
                System.out.println("conn: " + conn);
            }
            // grab the response as JSON and get the player token and data
            BufferedReader reader = new BufferedReader(new InputStreamReader(conn.getInputStream()));
            try {
                LoginResponse response = new LoginResponse();
                jsonDeserializer.deserializeInto(reader, response);
                if (isVerboseLoggingEnabled()) {
                    System.out.println(response);
                }
                LocalPlayerToken playerToken = new LocalPlayerToken(response.getLocalPlayerToken());

                localPlayer = new LocalPlayer(this, playerToken, response.getDisplayName(), response.getFriendCode(), response.isAuthenticated());
            }
            finally {
                reader.close();
            }
        }
        catch (Throwable t) {
            t.printStackTrace(System.err);
        }
        finally {
            if (conn != null) {
                conn.disconnect();
            }
        }
        return localPlayer;
    }

    public CompletionStage<LocalPlayer> loginAsync() {
        if (isVerboseLoggingEnabled()) {
            System.out.println("Connection.loginAsync()");
        }

        return CompletableFuture.supplyAsync(() -> {
            return login();
        }, executor);
    }

    public final boolean isVerboseLoggingEnabled() {
        return verboseLoggingEnabled;
    }

    public final void setVerboseLoggingEnabled(boolean enabled) {
        this.verboseLoggingEnabled = enabled;
    }
}
