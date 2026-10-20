package com.querypilot.auth;

import com.querypilot.config.JwtProperties;
import com.querypilot.user.Role;
import com.querypilot.user.User;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

class JwtServiceTest {

    private JwtService jwtService;

    @BeforeEach
    void setUp() {
        JwtProperties properties = new JwtProperties();
        properties.setSecret("querypilot-test-secret-0123456789abcdef0123456789abcdef");
        properties.setExpirationMs(60000L);
        jwtService = new JwtService(properties);
    }

    @Test
    void generatesAndParsesToken() {
        User user = new User();
        user.setId(1L);
        user.setEmail("admin@querypilot.dev");
        user.setRole(Role.ADMIN);

        String token = jwtService.generateToken(user);

        assertThat(jwtService.isValid(token)).isTrue();
        assertThat(jwtService.extractEmail(token)).isEqualTo("admin@querypilot.dev");
    }

    @Test
    void rejectsTamperedToken() {
        assertThat(jwtService.isValid("not-a-jwt")).isFalse();
    }
}
