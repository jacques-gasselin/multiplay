package org.multiplay.client;

import org.multiplay.ConnectionToken;
import org.multiplay.LocalPlayerToken;
import org.multiplay.RemotePlayerToken;
import org.multiplay.SessionToken;
import org.multiplay.client.response.*;

import java.net.URLEncoder;
import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionStage;

public class LocalPlayer extends Player {
    private final Connection connection;
    private final LocalPlayerToken playerToken;
    private String friendCode = "";
    private boolean authenticated = false;

    private List<LocalSession> sessions = new ArrayList<>();
    private List<Friend> friends = new ArrayList<>();

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

    public List<LocalSession> getLocalSessions() {
        return sessions;
    }

    List<Friend> getFriends() {
        return friends;
    }

    public List<Friend> fetchFriends() {
        String resource = "/listPlayerFriends.json?connection=" + connection.getConnectionToken() + "&localPlayer=" + playerToken;
        LocalPlayerFriendsResponse response = new LocalPlayerFriendsResponse();
        connection.fetchJSONInto(resource, response);

        List<Friend> friends = new ArrayList<>(response.getFriends().size());
        for (LocalPlayerFriendsResponse.Friend f: response.getFriends()) {
            RemotePlayerToken token = new RemotePlayerToken(f.getRemotePlayerToken());
            String displayName = f.getDisplayName();
            String alias = null;

            Friend friend = new Friend(connection, token, displayName, alias);
            friends.add(friend);
        }

        this.friends = friends;

        return friends;
    }

    public CompletionStage<List<Friend>> fetchFriendsAsync() {
        return CompletableFuture.supplyAsync(() -> {
            return fetchFriends();
        });
    }

    public List<LocalSession> fetchSessions() {
        String resource = "/listPlayerSessions.json?connection=" + connection.getConnectionToken() + "&localPlayer=" + playerToken;
        LocalPlayerSessionsResponse response = new LocalPlayerSessionsResponse();
        connection.fetchJSONInto(resource, response);

        List<LocalSession> sessions = new ArrayList<>(response.getSessions().size());
        for (LocalPlayerSessionsResponse.Session s: response.getSessions()) {
            SessionToken sessionToken = new SessionToken(s.getLocalSessionToken());
            String displayName = s.getDisplayName();
            String shareCode = s.getShareCode();

            LocalSession session = new LocalSession(connection, sessionToken, displayName, shareCode);
            sessions.add(session);
        }

        this.sessions = sessions;

        return sessions;
    }

    public CompletionStage<List<LocalSession>> fetchSessionsAsync() {
        return CompletableFuture.supplyAsync(() -> {
            return fetchSessions();
        });
    }

    public Session createSessionWithName(String name) {
        String encodedName = URLEncoder.encode(name);
        String resource = "/createSession.json?connection=" + connection.getConnectionToken()
                + "&localPlayer=" + playerToken + "&displayName=" + encodedName;
        CreateSessionResponse response = new CreateSessionResponse();
        connection.fetchJSONInto(resource, response);

        SessionToken sessionToken = new SessionToken(response.getLocalSessionToken());
        String displayName = response.getDisplayName();
        String shareCode = response.getShareCode();

        LocalSession session = new LocalSession(connection, sessionToken, displayName, shareCode);

        sessions.add(session);

        return session;
    }

    public CompletionStage<Session> createSessionWithNameAsync(String name) {
        return CompletableFuture.supplyAsync(() -> {
            return createSessionWithName(name);
        });
    }

    /**
     * Returns null if we are already in this session
     * @param sessionCode
     * @return
     */
    public Session joinSessionWithCode(String sessionCode) {
        String code = URLEncoder.encode(sessionCode);
        String resource = "/joinSession.json?connection=" + connection.getConnectionToken()
                + "&localPlayer=" + playerToken + "&sessionCode=" + code;
        JoinSessionResponse response = new JoinSessionResponse();
        connection.fetchJSONInto(resource, response);

        SessionToken sessionToken = new SessionToken(response.getLocalSessionToken());

        // Are we already in this session?
        for (Session s : sessions) {
            if (sessionToken.equals(s.getSessionToken())) {
                return null;
            }
        }

        String displayName = response.getDisplayName();
        String shareCode = response.getShareCode();
        LocalSession session = new LocalSession(connection, sessionToken, displayName, shareCode);

        sessions.add(session);

        return session;
    }

    public CompletionStage<Session> joinSessionWithCodeAsync(String sessionCode) {
        return CompletableFuture.supplyAsync(() -> {
            return joinSessionWithCode(sessionCode);
        });
    }

    public void addFriendWithCode(String friendCode) {
        String resource = "/addPlayerFriend.json?connection=" + connection.getConnectionToken()
                + "&localPlayer=" + playerToken + "&friendCode=" + friendCode;
        StatusResponse response = new StatusResponse();
        connection.fetchJSONInto(resource, response);
    }

    public CompletionStage<Void> addFriendWithCodeAsync(String friendCode) {
        return CompletableFuture.supplyAsync(() -> {
            addFriendWithCode(friendCode);
            return null;
        });
    }

    public LocalPlayer httpAuthenticate(String username, String password) {
        String resource = "/httpAuthenticate.json?connection=" + connection.getConnectionToken()
                + "&localPlayer=" + playerToken;
        LoginResponse response = new LoginResponse();
        response.setDisplayName(getDisplayName());
        response.setFriendCode(friendCode);
        response.setAuthenticated(authenticated ? 1 : 0);

        HashMap<String, String> properties = new HashMap<>();
        String concat = username + ":" + password;
        String value = "Basic " + new String(Base64.getEncoder().encode(concat.getBytes()));
        properties.put("Authorization", value);

        connection.fetchJSONInto(resource, response, properties);

        setDisplayName(response.getDisplayName());
        friendCode = response.getFriendCode();
        authenticated = response.isAuthenticated();

        return this;
    }

    public CompletionStage<LocalPlayer> httpAuthenticateAsync(String username, String password) {
        return CompletableFuture.supplyAsync(() -> {
            return httpAuthenticate(username, password);
        });
    }
}
