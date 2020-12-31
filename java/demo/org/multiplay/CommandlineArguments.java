package org.multiplay;

public class CommandlineArguments {
    private boolean verbose = false;
    private String protocol = "http";
    private String host = "localhost";
    private int port = 12345;

    public void parse(String[] args) {
        for (int i = 0; i < args.length; ++i) {
            String arg = args[i];
            if (arg.equals("--host") || arg.equals("-h")) {
                host = args[++i];
            }
            if (arg.equals("--port") || arg.equals("-p")) {
                port = Integer.valueOf(args[++i]);
            }
            if (arg.equals("--protocol")) {
                protocol = args[++i];
            }
            if (arg.equals("--verbose") || arg.equals("-v")) {
                verbose = true;
                System.out.println("[--verbose] logging enabled");
            }
        }
    }

    public final boolean isVerbose() {
        return verbose;
    }

    public final String getProtocol() {
        return protocol;
    }

    public final String getHost() {
        return host;
    }

    public final int getPort() {
        return port;
    }
}

