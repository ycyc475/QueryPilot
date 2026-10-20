package com.querypilot.auth;

import com.querypilot.auth.dto.LoginRequest;
import com.querypilot.auth.dto.LoginResponse;
import com.querypilot.auth.dto.UserDto;
import com.querypilot.user.User;
import com.querypilot.user.UserRepository;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.stereotype.Service;

@Service
public class AuthService {

    private final AuthenticationManager authenticationManager;
    private final UserRepository userRepository;
    private final JwtService jwtService;

    public AuthService(AuthenticationManager authenticationManager,
                       UserRepository userRepository,
                       JwtService jwtService) {
        this.authenticationManager = authenticationManager;
        this.userRepository = userRepository;
        this.jwtService = jwtService;
    }

    public LoginResponse login(LoginRequest request) {
        authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(request.email(), request.password()));
        User user = userRepository.findByEmail(request.email())
                .orElseThrow(() -> new IllegalStateException("认证通过但用户不存在"));
        String token = jwtService.generateToken(user);
        return new LoginResponse(token, UserDto.from(user));
    }

    public UserDto me(String email) {
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new IllegalStateException("用户不存在"));
        return UserDto.from(user);
    }
}
