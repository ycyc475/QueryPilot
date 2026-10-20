package com.querypilot.auth.dto;

import com.querypilot.user.User;

public record UserDto(Long id, String email, String displayName, String role) {

    public static UserDto from(User user) {
        return new UserDto(user.getId(), user.getEmail(), user.getDisplayName(), user.getRole().name());
    }
}
