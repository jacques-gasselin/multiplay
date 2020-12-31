package org.multiplay.chat;

import org.multiplay.client.Connection;

import java.io.IOException;
import java.net.URL;
import java.util.concurrent.CompletionStage;
import java.util.concurrent.Future;

class Chat {
    public static void main(String[] args) throws IOException {
        String protocol = "http";
        String host = "localhost";
        int port = 12345;
        for (int i = 0; i < args.length; ++i) {
            String arg = args[i];
            if (arg.equals("--host") || arg.equals("-h")) {
                host = args[++i];
            }
            if (arg.equals("--port") || arg.equals("-p")) {
                port = Integer.valueOf(args[++i]);
            }
        }
        URL serverURL = new URL(protocol, host, port, "/");
        ChatConnection.connect(serverURL).thenApply(connection -> {
            return null;
        });
    }
}