package com.querypilot.common;

/**
 * 统一响应包装：code=0 表示成功，其余为业务错误码（与 HTTP 状态一致）。
 */
public record ApiResponse<T>(int code, String message, T data) {

    public static <T> ApiResponse<T> ok(T data) {
        return new ApiResponse<>(0, "ok", data);
    }

    public static <T> ApiResponse<T> error(int code, String message) {
        return new ApiResponse<>(code, message, null);
    }
}
