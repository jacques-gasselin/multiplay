package org.multiplay.server;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentLinkedDeque;
import java.util.concurrent.ExecutorService;

public abstract class HttpServer {
    private final int port;
    private final ExecutorService executor;

    HttpServer(int port, ExecutorService executor) {
        this.port = port;
        this.executor = executor;
    }

    void shutdown() {
        executor.shutdown();
    }

    protected HttpRequest readRequestFromStream(InputStream stream) {
        return null;
    }

    protected void writeResponseToStream(OutputStream stream) {

    }

    private final HttpRequest readSocketRequest(Socket socket) {
        HttpRequest request = null;
        try (InputStream stream = socket.getInputStream()) {
            request = readRequestFromStream(stream);
        }
        catch (IOException e) {
            e.printStackTrace();
        }
        return request;
    }

    protected abstract HttpResponse handleRequest(HttpRequest request);

    private final void writeSocketResponse(Socket socket, HttpResponse response) {
        try (OutputStream stream = socket.getOutputStream()) {
            writeResponseToStream(stream);
        }
        catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void processSocket(Socket socket) {
        CompletableFuture.supplyAsync(() -> {
            return readSocketRequest(socket);
        }, executor).thenApply((request) -> {
            return handleRequest(request);
        }).thenAccept((response) -> {
            writeSocketResponse(socket, response);
            if (response.isKeepAlive()) {
                executor.execute(() -> {
                    processSocket(socket);
                });
            }
            else {
                try {
                    socket.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        });
    }

    void start() {
        try (ServerSocket serverSocket = new ServerSocket(port)) {
            while (!executor.isShutdown()) {
                Socket clientSocket = serverSocket.accept();
                executor.execute(() -> {
                    processSocket(clientSocket);
                });
            }
        }
        catch (IOException e) {
            e.printStackTrace();
        }
    }
}
