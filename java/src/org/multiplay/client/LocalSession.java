package org.multiplay.client;

import org.multiplay.SessionToken;

public class LocalSession extends Session {
    private String shareCode;

    LocalSession(Connection connection, SessionToken localSessionToken, String displayName, String shareCode) {
        super(connection, localSessionToken, displayName);
        this.shareCode = shareCode;
    }

    String getShareCode() {
        return this.shareCode;
    }
}
