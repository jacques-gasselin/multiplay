package org.multiplay.client;

import org.multiplay.LocalPlayerToken;

import java.util.ArrayList;
import java.util.List;

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

    String getFriendCode() {
        return friendCode;
    }

    boolean isAuthenticated() {
        return authenticated;
    }

    List<Session> getSessions() {
        return sessions;
    }

    List<Friend> getFriends() {
        return friends;
    }
}
