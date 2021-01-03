package org.multiplay.client.response;

public class StatusResponse {
    boolean success = false;

    public StatusResponse() {

    }

    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }
}
