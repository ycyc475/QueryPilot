package com.querypilot.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * JWT 配置（app.jwt.*），密钥与有效期从环境变量/配置读取。
 */
@ConfigurationProperties(prefix = "app.jwt")
public class JwtProperties {

    private String secret;
    private long expirationMs;

    public String getSecret() {
        return secret;
    }

    public void setSecret(String secret) {
        this.secret = secret;
    }

    public long getExpirationMs() {
        return expirationMs;
    }

    public void setExpirationMs(long expirationMs) {
        this.expirationMs = expirationMs;
    }
}
