package com.querypilot.seed;

import com.querypilot.user.Role;
import com.querypilot.user.User;
import com.querypilot.user.UserRepository;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

/**
 * 幂等种子：写入演示账号（密码用 BCrypt 哈希，不落明文）。
 * 目录元数据与指标口径由 Flyway V3 的 SQL 种子写入。
 */
@Component
public class DataSeeder implements ApplicationRunner {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public DataSeeder(UserRepository userRepository, PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @Override
    public void run(ApplicationArguments args) {
        seedUser("admin@querypilot.dev", "Admin123!", "管理员", Role.ADMIN);
        seedUser("demo@querypilot.dev", "Demo123!", "演示用户", Role.ANALYST);
    }

    private void seedUser(String email, String rawPassword, String displayName, Role role) {
        if (userRepository.existsByEmail(email)) {
            return;
        }
        User user = new User();
        user.setEmail(email);
        user.setPasswordHash(passwordEncoder.encode(rawPassword));
        user.setDisplayName(displayName);
        user.setRole(role);
        user.setActive(true);
        userRepository.save(user);
    }
}
