package org.multiplay.chat;

import org.multiplay.GameToken;
import org.multiplay.client.Connection;

import java.net.URL;
import java.util.UUID;
import java.util.concurrent.CompletionStage;

public class ChatConnection extends Connection {
    private static GameToken CHAT_GAME_TOKEN = new GameToken(UUID.fromString("00000000-0000-0000-0000-000000000000"));

    private ChatConnection(URL serverURL) {
        super(CHAT_GAME_TOKEN, null, serverURL, null);
    }

    public static CompletionStage<Connection> connect(URL serverURL) {
        ChatConnection conn = new ChatConnection(serverURL);
        return conn.connectAsync();
    }
}
