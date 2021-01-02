package org.multiplay.chat;

import org.multiplay.GameToken;
import org.multiplay.client.Connection;

import java.net.URL;
import java.util.concurrent.CompletionStage;

public final class ChatConnection extends Connection {
    private static GameToken CHAT_GAME_TOKEN = new GameToken("00000000-0000-0000-0000-000000000000");

    private ChatConnection(URL serverURL) {
        super(CHAT_GAME_TOKEN, null, serverURL, null);
    }

    public static CompletionStage<Connection> connect(URL serverURL, boolean verboseLoggingEnabled) {
        ChatConnection conn = new ChatConnection(serverURL);
        conn.setVerboseLoggingEnabled(verboseLoggingEnabled);
        return conn.connectAsync();
    }
}
