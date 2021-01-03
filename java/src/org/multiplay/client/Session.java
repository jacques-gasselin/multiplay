package org.multiplay.client;

import org.multiplay.SessionToken;
import org.multiplay.client.response.SessionPlayersResponse;

import java.net.URLEncoder;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletionStage;

public class Session {
    private final Connection connection;
    private final SessionToken sessionToken;
    private String displayName = "";

    Session(Connection connection, SessionToken sessionToken, String displayName) {
        this.connection = connection;
        this.sessionToken = sessionToken;
        if (displayName != null) {
            this.displayName = displayName;
        }
    }

    public <T> CompletionStage<T> fetchJSONDataIntoAsync(T response) {
        String resource = "/readSessionData?connection=" + connection.getConnectionToken() + "&session=" + this.sessionToken;
        return connection.fetchJSONIntoAsync(resource, response);
    }

    public CompletionStage<Void> sendJSONDataAsync(JSONSerializable object) {
        String json = object.toJSONString();
        String octetsGETParam = URLEncoder.encode(json);
        String resource = "/writeSessionData?connection=" + connection.getConnectionToken() + "&session=" + this.sessionToken +
                "&data=" + octetsGETParam;
        return connection.fetchAsync(resource);
    }

    public CompletionStage<List<Player>> fetchPlayersAsync() {
        String resource = "/listSessionPlayers.json?connection=" + connection.getConnectionToken() + "&session=" + this.sessionToken;
        return connection.fetchJSONIntoAsync(resource, new SessionPlayersResponse()).thenApply(response -> {
            List<Player> players = new ArrayList<>();

            return players;
        });
    }

    public SessionToken getSessionToken() {
        return sessionToken;
    }

    public String getDisplayName() {
        return displayName;
    }

    @Override
    public String toString() {
        return displayName;
    }
}
