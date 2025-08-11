package com.banking.transfers.service;

import com.banking.transfers.dto.LoginRequest;
import com.banking.transfers.dto.LoginResponse;
import com.banking.transfers.model.AMLStatus;
import com.banking.transfers.model.KYCStatus;
import com.banking.transfers.model.RiskLevel;
import com.banking.transfers.model.User;
import com.banking.transfers.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.LockedException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class AuthServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private AuthenticationManager authenticationManager;

    @Mock
    private PasswordEncoder passwordEncoder;

    @Mock
    private JwtService jwtService;

    @Mock
    private KeycloakService keycloakService;

    @Mock
    private MfaService mfaService;

    @Mock
    private AuditService auditService;

    @InjectMocks
    private AuthService authService;

    private User testUser;
    private LoginRequest loginRequest;

    @BeforeEach
    void setUp() {
        testUser = new User();
        testUser.setId(UUID.randomUUID());
        testUser.setUsername("testuser");
        testUser.setEmail("test@example.com");
        testUser.setFirstName("Test");
        testUser.setLastName("User");
        testUser.setPassword("encodedPassword");
        testUser.setIsActive(true);
        testUser.setIsLocked(false);
        testUser.setKycStatus(KYCStatus.VERIFIED);
        testUser.setAmlStatus(AMLStatus.PASSED);
        testUser.setRiskLevel(RiskLevel.LOW);
        testUser.setRiskScore(10);
        testUser.setMfaEnabled(false);
        testUser.setDateOfBirth(LocalDate.of(1990, 1, 1));
        testUser.setNationality("FR");
        testUser.setCountry("FR");
        testUser.setPhone("+33123456789");
        testUser.setCreatedAt(LocalDateTime.now());

        loginRequest = new LoginRequest();
        loginRequest.setUsername("testuser");
        loginRequest.setPassword("password123");
        loginRequest.setClientIp("127.0.0.1");
        loginRequest.setUserAgent("Mozilla/5.0");
    }

    @Test
    void testLoginSuccess() {
        // Arrange
        Authentication authentication = mock(Authentication.class);
        when(authentication.getPrincipal()).thenReturn(testUser);
        when(authenticationManager.authenticate(any(UsernamePasswordAuthenticationToken.class)))
                .thenReturn(authentication);
        when(userRepository.findByUsername("testuser")).thenReturn(Optional.of(testUser));
        when(jwtService.generateAccessToken(testUser)).thenReturn("accessToken");
        when(jwtService.generateRefreshToken(testUser)).thenReturn("refreshToken");
        when(keycloakService.generateAccessToken(anyString())).thenReturn("keycloakToken");
        when(keycloakService.generateRefreshToken(anyString())).thenReturn("keycloakRefreshToken");
        when(keycloakService.getUserRoles(anyString())).thenReturn(java.util.Arrays.asList("USER", "TRANSFER_USER"));
        when(keycloakService.getUserPermissions(anyString())).thenReturn(java.util.Arrays.asList("READ", "WRITE"));

        // Act
        LoginResponse response = authService.login(loginRequest, "127.0.0.1", "Mozilla/5.0");

        // Assert
        assertNotNull(response);
        assertEquals("testuser", response.getUsername());
        assertEquals("accessToken", response.getAccessToken());
        assertEquals("refreshToken", response.getRefreshToken());
        assertEquals(KYCStatus.VERIFIED, response.getKycStatus());
        assertEquals(AMLStatus.PASSED, response.getAmlStatus());
        assertEquals(RiskLevel.LOW, response.getRiskLevel());
        assertFalse(response.getMfaEnabled());

        verify(auditService).logLoginSuccess(testUser.getId(), "127.0.0.1", "Mozilla/5.0");
        verify(userRepository).save(testUser);
    }

    @Test
    void testLoginWithMfa() {
        // Arrange
        testUser.setMfaEnabled(true);
        loginRequest.setMfaCode("123456");

        Authentication authentication = mock(Authentication.class);
        when(authentication.getPrincipal()).thenReturn(testUser);
        when(authenticationManager.authenticate(any(UsernamePasswordAuthenticationToken.class)))
                .thenReturn(authentication);
        when(userRepository.findByUsername("testuser")).thenReturn(Optional.of(testUser));
        when(mfaService.validateCode(anyString(), eq("123456"))).thenReturn(true);
        when(jwtService.generateAccessToken(testUser)).thenReturn("accessToken");
        when(jwtService.generateRefreshToken(testUser)).thenReturn("refreshToken");
        when(keycloakService.generateAccessToken(anyString())).thenReturn("keycloakToken");
        when(keycloakService.generateRefreshToken(anyString())).thenReturn("keycloakRefreshToken");
        when(keycloakService.getUserRoles(anyString())).thenReturn(java.util.Arrays.asList("USER"));
        when(keycloakService.getUserPermissions(anyString())).thenReturn(java.util.Arrays.asList("READ"));

        // Act
        LoginResponse response = authService.login(loginRequest, "127.0.0.1", "Mozilla/5.0");

        // Assert
        assertNotNull(response);
        assertTrue(response.getMfaEnabled());
        verify(mfaService).validateCode(anyString(), eq("123456"));
    }

    @Test
    void testLoginWithInvalidCredentials() {
        // Arrange
        when(authenticationManager.authenticate(any(UsernamePasswordAuthenticationToken.class)))
                .thenThrow(new BadCredentialsException("Invalid credentials"));

        // Act & Assert
        assertThrows(BadCredentialsException.class, () -> {
            authService.login(loginRequest, "127.0.0.1", "Mozilla/5.0");
        });

        verify(auditService).logLoginFailed("testuser", "Invalid credentials", "127.0.0.1", "Mozilla/5.0");
    }

    @Test
    void testLoginWithLockedAccount() {
        // Arrange
        when(authenticationManager.authenticate(any(UsernamePasswordAuthenticationToken.class)))
                .thenThrow(new LockedException("Account locked"));

        // Act & Assert
        assertThrows(LockedException.class, () -> {
            authService.login(loginRequest, "127.0.0.1", "Mozilla/5.0");
        });

        verify(auditService).logLoginFailed("testuser", "Account locked", "127.0.0.1", "Mozilla/5.0");
    }

    @Test
    void testLoginWithMfaRequiredButNotProvided() {
        // Arrange
        testUser.setMfaEnabled(true);
        loginRequest.setMfaCode(null);

        Authentication authentication = mock(Authentication.class);
        when(authentication.getPrincipal()).thenReturn(testUser);
        when(authenticationManager.authenticate(any(UsernamePasswordAuthenticationToken.class)))
                .thenReturn(authentication);
        when(userRepository.findByUsername("testuser")).thenReturn(Optional.of(testUser));

        // Act & Assert
        assertThrows(IllegalArgumentException.class, () -> {
            authService.login(loginRequest, "127.0.0.1", "Mozilla/5.0");
        });
    }

    @Test
    void testLoginWithInvalidMfaCode() {
        // Arrange
        testUser.setMfaEnabled(true);
        loginRequest.setMfaCode("123456");

        Authentication authentication = mock(Authentication.class);
        when(authentication.getPrincipal()).thenReturn(testUser);
        when(authenticationManager.authenticate(any(UsernamePasswordAuthenticationToken.class)))
                .thenReturn(authentication);
        when(userRepository.findByUsername("testuser")).thenReturn(Optional.of(testUser));
        when(mfaService.validateCode(anyString(), eq("123456"))).thenReturn(false);

        // Act & Assert
        assertThrows(IllegalArgumentException.class, () -> {
            authService.login(loginRequest, "127.0.0.1", "Mozilla/5.0");
        });

        verify(auditService).logLoginFailed("testuser", "Code MFA invalide", "127.0.0.1", "Mozilla/5.0");
    }

    @Test
    void testLogout() {
        // Arrange
        String token = "Bearer validToken";
        when(jwtService.extractUsername("validToken")).thenReturn("testuser");
        when(userRepository.findByUsername("testuser")).thenReturn(Optional.of(testUser));

        // Act
        authService.logout(token, "127.0.0.1");

        // Assert
        verify(jwtService).invalidateToken("validToken");
        verify(auditService).logLogout(testUser.getId(), "127.0.0.1");
    }

    @Test
    void testRefreshToken() {
        // Arrange
        String refreshToken = "validRefreshToken";
        when(jwtService.validateRefreshToken(refreshToken)).thenReturn(true);
        when(jwtService.extractUsername(refreshToken)).thenReturn("testuser");
        when(userRepository.findByUsername("testuser")).thenReturn(Optional.of(testUser));
        when(jwtService.generateNewAccessTokenFromRefreshToken(refreshToken)).thenReturn("newAccessToken");
        when(jwtService.generateRefreshToken(testUser)).thenReturn("newRefreshToken");
        when(keycloakService.generateAccessToken(anyString())).thenReturn("keycloakToken");
        when(keycloakService.generateRefreshToken(anyString())).thenReturn("keycloakRefreshToken");
        when(keycloakService.getUserRoles(anyString())).thenReturn(java.util.Arrays.asList("USER"));
        when(keycloakService.getUserPermissions(anyString())).thenReturn(java.util.Arrays.asList("READ"));

        // Act
        LoginResponse response = authService.refreshToken(refreshToken, "127.0.0.1");

        // Assert
        assertNotNull(response);
        assertEquals("newAccessToken", response.getAccessToken());
        assertEquals("newRefreshToken", response.getRefreshToken());
        verify(auditService).logTokenRefresh(testUser.getId(), "127.0.0.1");
    }

    @Test
    void testRefreshTokenWithInvalidToken() {
        // Arrange
        String refreshToken = "invalidRefreshToken";
        when(jwtService.validateRefreshToken(refreshToken)).thenReturn(false);

        // Act & Assert
        assertThrows(BadCredentialsException.class, () -> {
            authService.refreshToken(refreshToken, "127.0.0.1");
        });
    }

    @Test
    void testValidateAccessToken() {
        // Arrange
        String token = "Bearer validToken";
        when(jwtService.validateAccessToken("validToken")).thenReturn(true);
        when(jwtService.extractUsername("validToken")).thenReturn("testuser");
        when(userRepository.findByUsername("testuser")).thenReturn(Optional.of(testUser));

        // Act
        User result = authService.validateAccessToken(token);

        // Assert
        assertNotNull(result);
        assertEquals("testuser", result.getUsername());
    }

    @Test
    void testValidateAccessTokenWithInvalidToken() {
        // Arrange
        String token = "Bearer invalidToken";
        when(jwtService.validateAccessToken("invalidToken")).thenReturn(false);

        // Act
        User result = authService.validateAccessToken(token);

        // Assert
        assertNull(result);
    }

    @Test
    void testIsUserAccountValid() {
        // Arrange
        when(userRepository.findByUsername("testuser")).thenReturn(Optional.of(testUser));

        // Act
        boolean result = authService.isUserAccountValid("testuser");

        // Assert
        assertTrue(result);
    }

    @Test
    void testIsUserAccountValidWithLockedUser() {
        // Arrange
        testUser.setIsLocked(true);
        when(userRepository.findByUsername("testuser")).thenReturn(Optional.of(testUser));

        // Act
        boolean result = authService.isUserAccountValid("testuser");

        // Assert
        assertFalse(result);
    }

    @Test
    void testIsUserAccountValidWithInactiveUser() {
        // Arrange
        testUser.setIsActive(false);
        when(userRepository.findByUsername("testuser")).thenReturn(Optional.of(testUser));

        // Act
        boolean result = authService.isUserAccountValid("testuser");

        // Assert
        assertFalse(result);
    }

    @Test
    void testIsUserAccountValidWithNonExistentUser() {
        // Arrange
        when(userRepository.findByUsername("nonexistent")).thenReturn(Optional.empty());

        // Act
        boolean result = authService.isUserAccountValid("nonexistent");

        // Assert
        assertFalse(result);
    }
}