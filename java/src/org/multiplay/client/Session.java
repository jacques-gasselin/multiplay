package org.multiplay.client;

import org.multiplay.SessionToken;

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

    @Override
    public String toString() {
        return displayName;
    }
}
