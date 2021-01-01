package org.multiplay.client;

import org.multiplay.ConnectionToken;
import org.multiplay.LocalPlayerToken;
import org.multiplay.RemotePlayerToken;
import org.multiplay.client.response.LocalPlayerFriendsResponse;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionStage;

public class LocalPlayer extends Player {
    private final Connection connection;
    private final LocalPlayerToken playerToken;
    private String friendCode = "";
    private boolean authenticated = false;

    private List<Session> sessions = new ArrayList<Session>();
    private List<Friend> friends = new ArrayList<Friend>();

    LocalPlayer(Connection connection, LocalPlayerToken localPlayerToken, String displayName, String friendCode, boolean authenticated) {
        super(displayName);
        this.connection = connection;
        this.playerToken = localPlayerToken;
        if (friendCode != null) {
            this.friendCode = friendCode;
        }
        this.authenticated = authenticated;
    }

    LocalPlayerToken getLocalPlayerToken() {
        return playerToken;
    }

    public String getFriendCode() {
        return friendCode;
    }

    public boolean isAuthenticated() {
        return authenticated;
    }

    List<Session> getSessions() {
        return sessions;
    }

    List<Friend> getFriends() {
        return friends;
    }

    public List<Friend> fetchFriends() {
        String resource = "/listPlayerFriends.json?connection=" + connection.getConnectionToken() + "&localPlayer=" + playerToken;
        LocalPlayerFriendsResponse response = new LocalPlayerFriendsResponse();
        connection.fetchJSONInto(resource, response);
        friends.clear();

        for (LocalPlayerFriendsResponse.Friend f: response.getFriends()) {
            RemotePlayerToken token = new RemotePlayerToken(f.getRemotePlayerToken());
            String displayName = f.getDisplayName();
            String alias = null;

            Friend friend = new Friend(connection, token, displayName, alias);
            friends.add(friend);
        }

        return friends;
    }

    public CompletionStage<List<Friend>> fetchFriendsAsync() {
        if (connection.isVerboseLoggingEnabled()) {
            System.out.println("LocalPlayer.fetchFriendsAsync()");
        }
        return CompletableFuture.supplyAsync(() -> {
            return fetchFriends();
        });
    }
}
