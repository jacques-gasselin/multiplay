package org.multiplay.chat;

import org.multiplay.CommandlineArguments;
import org.multiplay.client.Connection;
import org.multiplay.client.LocalPlayer;

import java.io.IOException;
import java.net.URL;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;

class Chat {
    private Connection connection = null;
    private boolean closed = false;

    void updatePlayer(LocalPlayer player) {

    }

    void updateChannels() {

    }

    void updateFriends() {

    }

    void updateMessages() {

    }

    void close() {
        if (connection != null) {
            connection.close();
            connection = null;
        }
        closed = true;
    }

    public static void main(String[] args) throws IOException {
        final Chat chat = new Chat();

        CommandlineArguments cmd = new CommandlineArguments();
        cmd.parse(args);

        URL serverURL = new URL(cmd.getProtocol(), cmd.getHost(), cmd.getPort(), "/");
        ChatConnection.connect(serverURL, cmd.isVerbose()).thenAccept(connection -> {
            chat.connection = connection;
            LocalPlayer localPlayer = connection.login();
            chat.updatePlayer(localPlayer);
            chat.updateChannels();
            chat.updateFriends();
            chat.updateMessages();
        });
        while (!chat.closed) {
            Thread.yield();
        }
    }
}
