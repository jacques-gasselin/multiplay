package org.multiplay.client;

import org.multiplay.RemotePlayerToken;

public class Friend extends Player {
    private final Connection connection;
    private final RemotePlayerToken playerToken;
    private String alias = "";

    Friend(Connection connection, RemotePlayerToken playerToken, String displayName, String alias) {
        super(displayName);
        this.connection = connection;
        this.playerToken = playerToken;
        if (alias != null) {
            this.alias = alias;
        }
    }

    String getAlias() {
        return alias;
    }
}
