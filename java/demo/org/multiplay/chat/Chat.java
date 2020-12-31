package org.multiplay.chat;

import org.multiplay.CommandlineArguments;

import java.io.IOException;
import java.net.URL;

class Chat {
    public static void main(String[] args) throws IOException {
        CommandlineArguments cmd = new CommandlineArguments();
        cmd.parse(args);

        URL serverURL = new URL(cmd.getProtocol(), cmd.getHost(), cmd.getPort(), "/");
        ChatConnection.connect(serverURL, cmd.isVerbose()).thenApply(connection -> {
            return null;
        });
    }
}