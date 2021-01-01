package org.multiplay.chat;

import org.multiplay.CommandlineArguments;
import org.multiplay.client.Connection;
import org.multiplay.client.LocalPlayer;

import java.io.IOException;
import java.net.URL;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;

public class Chat {
    private Connection connection = null;
    private boolean closed = false;
    private UserInterface userInterface = null;

    public void close() {
        if (connection != null) {
            connection.close();
            connection = null;
        }
        closed = true;
    }

    public void setUserInterface(UserInterface userInterface) {
        this.userInterface = userInterface;
    }

    public void start(String[] args) throws IOException {
        CommandlineArguments cmd = new CommandlineArguments();
        cmd.parse(args);

        UserInterface userInterface = this.userInterface;
        if (userInterface == null) {
            System.err.println("no user interface set");
        }

        URL serverURL = new URL(cmd.getProtocol(), cmd.getHost(), cmd.getPort(), "/");
        ChatConnection.connect(serverURL, cmd.isVerbose()).thenAccept(connection -> {
            connection = connection;
            LocalPlayer localPlayer = connection.login();
            if (userInterface != null) {
                userInterface.updatePlayer(localPlayer);
                userInterface.updateChannels();
                userInterface.updateFriends();
                userInterface.updateMessages();
            }
        });
    }

    public static void main(String[] args) throws IOException {
        final Chat chat = new Chat();
        chat.start(args);
        while (!chat.closed) {
            Thread.yield();
        }
    }
}
