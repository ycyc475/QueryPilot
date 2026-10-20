package com.querypilot.auth.dto;

public record LoginResponse(String token, UserDto user) {
}
