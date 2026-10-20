package com.querypilot.common;

import org.springframework.http.HttpStatus;

/**
 * 业务异常，携带 HTTP 状态码，由 {@link GlobalExceptionHandler} 统一转换为响应。
 */
public class BusinessException extends RuntimeException {

    private final HttpStatus status;

    public BusinessException(HttpStatus status, String message) {
        super(message);
        this.status = status;
    }

    public HttpStatus getStatus() {
        return status;
    }
}
