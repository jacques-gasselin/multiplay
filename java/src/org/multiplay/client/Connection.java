package org.multiplay.client;

import com.owlike.genson.stream.JsonStreamException;
import org.multiplay.ConnectionToken;
import org.multiplay.DeviceToken;
import org.multiplay.GameToken;

import com.owlike.genson.Genson;
import com.owlike.genson.GensonBuilder;
import org.multiplay.client.response.ConnectionResponse;
import org.multiplay.client.response.LoginResponse;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.NetworkInterface;
import java.net.URL;
import java.util.Enumeration;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.*;

public abstract class Connection {
    private final GameToken gameToken;
    private final DeviceToken deviceToken;
    private final URL serverURL;
    private final ExecutorService executor;
    private ConnectionToken connectionToken = null;
    private boolean verboseLoggingEnabled = false;

    private Genson jsonDeserializer = null;

    private static DeviceToken getDefaultDeviceToken() {
        UUID deviceUUID = UUID.randomUUID();
        try {
            Enumeration<NetworkInterface> iter = NetworkInterface.getNetworkInterfaces();
            while (iter.hasMoreElements()){
                NetworkInterface ni = iter.nextElement();
                byte[] macBytes = ni.getHardwareAddress();
                if (macBytes != null) {
                    System.out.println("mac address: " + macBytes);
                    deviceUUID = UUID.nameUUIDFromBytes(macBytes);
                    break;
                }
            }
        }
        catch (Throwable t) {
            t.printStackTrace();
        }
        return new DeviceToken(deviceUUID.toString());
    }

    protected Connection(GameToken gameToken, DeviceToken deviceToken, URL serverURL, ExecutorService executor) {
        this.gameToken = gameToken;
        if (deviceToken == null) {
            this.deviceToken = getDefaultDeviceToken();
        }
        else {
            this.deviceToken = deviceToken;
        }
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

    public ConnectionToken getConnectionToken() {
        return connectionToken;
    }

    CompletionStage<Void> fetchAsync(String resource) {
        String protocol = serverURL.getProtocol();
        String host = serverURL.getHost();
        int port = serverURL.getPort();

        return CompletableFuture.supplyAsync(() -> {
            HttpURLConnection conn = null;
            try {
                URL fetchURL = new URL(protocol, host, port, resource);
                if (isVerboseLoggingEnabled()) {
                    System.out.println(fetchURL);
                }
                conn = (HttpURLConnection) fetchURL.openConnection();
                // grab the response
                try (InputStream is = conn.getInputStream()) {
                    int success = is.read();
                    if (isVerboseLoggingEnabled()) {
                        System.out.println(success);
                    }
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
            return null;
        }, executor);
    }

    <T> T fetchJSONInto(String resource, T response) {
        return fetchJSONInto(resource, response, null);
    }

    <T> T fetchJSONInto(String resource, T response, Map<String, String> properties) {
        String protocol = serverURL.getProtocol();
        String host = serverURL.getHost();
        int port = serverURL.getPort();

        HttpURLConnection conn = null;
        try {
            URL fetchURL = new URL(protocol, host, port, resource);
            if (isVerboseLoggingEnabled()) {
                System.out.println(fetchURL);
            }
            conn = (HttpURLConnection) fetchURL.openConnection();
            if (properties != null) {
                final HttpURLConnection c = conn;
                properties.forEach((key, value) -> {
                    c.setRequestProperty(key, value);
                });
            }
            // grab the response as JSON and get the player token and data
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(conn.getInputStream()))) {
                try {
                    jsonDeserializer.deserializeInto(reader, response);
                }
                catch (JsonStreamException e) {
                    System.err.println(e);
                }

                if (isVerboseLoggingEnabled()) {
                    System.out.println(response);
                }
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
        return response;
    }

    <T> CompletionStage<T> fetchJSONIntoAsync(String resource, T response) {
        return CompletableFuture.supplyAsync(() -> {
            return fetchJSONInto(resource, response);
        }, executor);
    }

    /**
     * Connect to the game's instance of the multiplay service.
     * @return {Promise} a promise that is fulfilled when the game is connected.
     */
    public CompletionStage<Connection> connectAsync() {
        if (isVerboseLoggingEnabled()) {
            System.out.println("Connection.connectAsync()");
        }
        return CompletableFuture.supplyAsync(() -> {
            String resource = "/connect.json?game=" + gameToken;
            ConnectionResponse response = new ConnectionResponse();
            fetchJSONInto(resource, response);
            connectionToken = new ConnectionToken(response.getConnectionToken());
            return this;
        }, executor);
    }

    public LocalPlayer login() {
        if (isVerboseLoggingEnabled()) {
            System.out.println("Connection.login()");
        }

        String resource = "/login.json?connection=" + connectionToken.toString() + "&localDevice=" + deviceToken.toString();
        LoginResponse response = new LoginResponse();
        fetchJSONInto(resource, response);
        LocalPlayer localPlayer = new LocalPlayer(this, response.getLocalPlayerToken(), response.getDisplayName(), response.getFriendCode(), response.isAuthenticated());
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

    public Executor getExecutor() {
        return executor;
    }
}
