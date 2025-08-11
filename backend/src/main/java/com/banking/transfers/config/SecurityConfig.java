package com.banking.transfers.config;

import com.banking.transfers.security.JwtAuthenticationEntryPoint;
import com.banking.transfers.security.JwtAuthenticationFilter;
import com.banking.transfers.security.JwtAuthorizationFilter;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.Arrays;
import java.util.List;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity(prePostEnabled = true, securedEnabled = true, jsr250Enabled = true)
public class SecurityConfig {

    @Autowired
    private JwtAuthenticationEntryPoint jwtAuthenticationEntryPoint;

    @Autowired
    private JwtAuthenticationFilter jwtAuthenticationFilter;

    @Autowired
    private JwtAuthorizationFilter jwtAuthorizationFilter;

    @Value("${cors.allowed-origins:http://localhost:3000,http://localhost:8080}")
    private String allowedOrigins;

    @Value("${cors.allowed-methods:GET,POST,PUT,DELETE,OPTIONS}")
    private String allowedMethods;

    @Value("${cors.allowed-headers:*}")
    private String allowedHeaders;

    @Value("${cors.allow-credentials:true}")
    private boolean allowCredentials;

    @Value("${cors.max-age:3600}")
    private long maxAge;

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(12);
    }

    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration authConfig) throws Exception {
        return authConfig.getAuthenticationManager();
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            // Désactiver CSRF pour les APIs REST
            .csrf(AbstractHttpConfigurer::disable)
            
            // Configuration CORS
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            
            // Configuration des sessions
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            )
            
            // Configuration des autorisations
            .authorizeHttpRequests(authz -> authz
                // Endpoints publics
                .requestMatchers(
                    "/auth/login",
                    "/auth/register",
                    "/auth/refresh",
                    "/auth/validate",
                    "/auth/reset-password-request",
                    "/auth/reset-password-confirm",
                    "/auth/mfa/test-code",
                    "/auth/mfa/validate",
                    "/auth/mfa/config",
                    "/actuator/health",
                    "/actuator/info",
                    "/actuator/metrics",
                    "/actuator/prometheus",
                    "/swagger-ui/**",
                    "/v3/api-docs/**",
                    "/v3/api-docs.yaml",
                    "/swagger-resources/**",
                    "/webjars/**"
                ).permitAll()
                
                // Endpoints d'administration (nécessitent le rôle ADMIN)
                .requestMatchers(
                    "/admin/**",
                    "/auth/users/*/unlock",
                    "/auth/users/*/deactivate",
                    "/auth/users/*/kyc-status",
                    "/auth/users/*/aml-status"
                ).hasRole("ADMIN")
                
                // Endpoints de gestion des utilisateurs (nécessitent le rôle USER_MANAGER ou ADMIN)
                .requestMatchers(
                    "/users/**"
                ).hasAnyRole("USER_MANAGER", "ADMIN")
                
                // Endpoints de transferts (nécessitent le rôle TRANSFER_USER ou plus)
                .requestMatchers(
                    "/transfers/**",
                    "/accounts/**"
                ).hasAnyRole("TRANSFER_USER", "USER_MANAGER", "ADMIN")
                
                // Endpoints KYC (nécessitent le rôle KYC_OFFICER ou plus)
                .requestMatchers(
                    "/kyc/**"
                ).hasAnyRole("KYC_OFFICER", "USER_MANAGER", "ADMIN")
                
                // Tous les autres endpoints nécessitent une authentification
                .anyRequest().authenticated()
            )
            
            // Configuration des exceptions
            .exceptionHandling(exceptions -> exceptions
                .authenticationEntryPoint(jwtAuthenticationEntryPoint)
            )
            
            // Ajout des filtres JWT
            .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class)
            .addFilterAfter(jwtAuthorizationFilter, JwtAuthenticationFilter.class);

        return http.build();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        
        // Configuration des origines autorisées
        if ("*".equals(allowedOrigins)) {
            configuration.setAllowedOriginPatterns(List.of("*"));
        } else {
            configuration.setAllowedOrigins(Arrays.asList(allowedOrigins.split(",")));
        }
        
        // Configuration des méthodes HTTP autorisées
        configuration.setAllowedMethods(Arrays.asList(allowedMethods.split(",")));
        
        // Configuration des en-têtes autorisés
        if ("*".equals(allowedHeaders)) {
            configuration.setAllowedHeaders(List.of("*"));
        } else {
            configuration.setAllowedHeaders(Arrays.asList(allowedHeaders.split(",")));
        }
        
        // Configuration des en-têtes exposés
        configuration.setExposedHeaders(Arrays.asList(
            "Authorization",
            "Content-Type",
            "X-Requested-With",
            "Accept",
            "Origin",
            "Access-Control-Request-Method",
            "Access-Control-Request-Headers",
            "X-Total-Count",
            "X-Page-Number",
            "X-Page-Size"
        ));
        
        // Configuration des credentials
        configuration.setAllowCredentials(allowCredentials);
        
        // Configuration du max age
        configuration.setMaxAge(maxAge);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        
        return source;
    }

    // Configuration des en-têtes de sécurité
    @Bean
    public org.springframework.security.web.header.HeaderWriterFilter securityHeadersFilter() {
        return new org.springframework.security.web.header.HeaderWriterFilter(
            new org.springframework.security.web.header.writers.DelegatingRequestMatcherHeaderWriter(
                new org.springframework.security.web.util.matcher.AntPathRequestMatcher("/**"),
                new org.springframework.security.web.header.writers.StaticHeadersWriter("X-Content-Type-Options", "nosniff"),
                new org.springframework.security.web.header.writers.StaticHeadersWriter("X-Frame-Options", "DENY"),
                new org.springframework.security.web.header.writers.StaticHeadersWriter("X-XSS-Protection", "1; mode=block"),
                new org.springframework.security.web.header.writers.StaticHeadersWriter("Referrer-Policy", "strict-origin-when-cross-origin"),
                new org.springframework.security.web.header.writers.StaticHeadersWriter("Permissions-Policy", "geolocation=(), microphone=(), camera=()"),
                new org.springframework.security.web.header.writers.StaticHeadersWriter("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
            )
        );
    }
}