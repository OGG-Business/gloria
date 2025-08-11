package com.banking.transfers.security;

import com.banking.transfers.service.AuthService;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;

@Component
public class JwtAuthorizationFilter extends OncePerRequestFilter {

    @Autowired
    private AuthService authService;

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {

        try {
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();

            if (authentication != null && authentication.isAuthenticated() && 
                authentication.getPrincipal() instanceof UserDetails) {
                
                UserDetails userDetails = (UserDetails) authentication.getPrincipal();
                
                // Vérifier si l'utilisateur est actif et non verrouillé
                if (!isUserAccountValid(userDetails.getUsername())) {
                    SecurityContextHolder.clearContext();
                    throw new AccessDeniedException("Compte utilisateur invalide ou verrouillé");
                }

                // Vérifier les permissions spécifiques si nécessaire
                String requestURI = request.getRequestURI();
                String method = request.getMethod();
                
                if (requiresSpecialAuthorization(requestURI, method)) {
                    if (!hasRequiredPermissions(userDetails, requestURI, method)) {
                        throw new AccessDeniedException("Permissions insuffisantes pour accéder à cette ressource");
                    }
                }

                // Ajouter des informations d'audit
                addAuditHeaders(response, userDetails);
            }
        } catch (AccessDeniedException e) {
            handleAccessDenied(response, e);
            return;
        } catch (Exception e) {
            logger.error("Erreur lors de l'autorisation: {}", e.getMessage());
            // Continuer le traitement pour les erreurs non critiques
        }

        filterChain.doFilter(request, response);
    }

    private boolean isUserAccountValid(String username) {
        try {
            // Vérifier le statut du compte via AuthService
            return authService.isUserAccountValid(username);
        } catch (Exception e) {
            logger.error("Erreur lors de la vérification du compte utilisateur: {}", e.getMessage());
            return false;
        }
    }

    private boolean requiresSpecialAuthorization(String requestURI, String method) {
        // Endpoints nécessitant des vérifications spéciales
        return requestURI.startsWith("/admin/") ||
               requestURI.startsWith("/users/") ||
               requestURI.startsWith("/kyc/") ||
               (requestURI.startsWith("/transfers/") && "DELETE".equals(method)) ||
               (requestURI.startsWith("/accounts/") && "DELETE".equals(method));
    }

    private boolean hasRequiredPermissions(UserDetails userDetails, String requestURI, String method) {
        // Vérifier les permissions selon le rôle et l'endpoint
        if (requestURI.startsWith("/admin/")) {
            return userDetails.getAuthorities().stream()
                    .anyMatch(authority -> authority.getAuthority().equals("ROLE_ADMIN"));
        }
        
        if (requestURI.startsWith("/users/")) {
            return userDetails.getAuthorities().stream()
                    .anyMatch(authority -> 
                        authority.getAuthority().equals("ROLE_ADMIN") ||
                        authority.getAuthority().equals("ROLE_USER_MANAGER"));
        }
        
        if (requestURI.startsWith("/kyc/")) {
            return userDetails.getAuthorities().stream()
                    .anyMatch(authority -> 
                        authority.getAuthority().equals("ROLE_ADMIN") ||
                        authority.getAuthority().equals("ROLE_KYC_OFFICER") ||
                        authority.getAuthority().equals("ROLE_USER_MANAGER"));
        }

        // Pour les suppressions, vérifier des permissions spéciales
        if ("DELETE".equals(method)) {
            return userDetails.getAuthorities().stream()
                    .anyMatch(authority -> 
                        authority.getAuthority().equals("ROLE_ADMIN") ||
                        authority.getAuthority().equals("ROLE_USER_MANAGER"));
        }

        return true;
    }

    private void addAuditHeaders(HttpServletResponse response, UserDetails userDetails) {
        response.setHeader("X-User-ID", userDetails.getUsername());
        response.setHeader("X-User-Roles", String.join(",", 
            userDetails.getAuthorities().stream()
                .map(authority -> authority.getAuthority())
                .toArray(String[]::new)));
        response.setHeader("X-Authorization-Level", getAuthorizationLevel(userDetails));
    }

    private String getAuthorizationLevel(UserDetails userDetails) {
        if (userDetails.getAuthorities().stream()
                .anyMatch(authority -> authority.getAuthority().equals("ROLE_ADMIN"))) {
            return "ADMIN";
        } else if (userDetails.getAuthorities().stream()
                .anyMatch(authority -> authority.getAuthority().equals("ROLE_USER_MANAGER"))) {
            return "MANAGER";
        } else if (userDetails.getAuthorities().stream()
                .anyMatch(authority -> authority.getAuthority().equals("ROLE_KYC_OFFICER"))) {
            return "KYC_OFFICER";
        } else if (userDetails.getAuthorities().stream()
                .anyMatch(authority -> authority.getAuthority().equals("ROLE_TRANSFER_USER"))) {
            return "TRANSFER_USER";
        } else {
            return "USER";
        }
    }

    private void handleAccessDenied(HttpServletResponse response, AccessDeniedException e) throws IOException {
        response.setStatus(HttpServletResponse.SC_FORBIDDEN);
        response.setContentType("application/json");
        response.setCharacterEncoding("UTF-8");
        
        String errorResponse = String.format(
            "{\"success\":false,\"error\":\"FORBIDDEN\",\"message\":\"%s\",\"timestamp\":\"%s\"}",
            e.getMessage(),
            java.time.LocalDateTime.now()
        );
        
        response.getWriter().write(errorResponse);
    }

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) throws ServletException {
        String path = request.getRequestURI();
        
        // Ne pas filtrer les endpoints publics
        return path.startsWith("/auth/login") ||
               path.startsWith("/auth/register") ||
               path.startsWith("/auth/refresh") ||
               path.startsWith("/auth/validate") ||
               path.startsWith("/auth/reset-password") ||
               path.startsWith("/auth/mfa/test-code") ||
               path.startsWith("/auth/mfa/validate") ||
               path.startsWith("/auth/mfa/config") ||
               path.startsWith("/actuator/health") ||
               path.startsWith("/actuator/info") ||
               path.startsWith("/actuator/metrics") ||
               path.startsWith("/actuator/prometheus") ||
               path.startsWith("/swagger-ui") ||
               path.startsWith("/v3/api-docs") ||
               path.startsWith("/swagger-resources") ||
               path.startsWith("/webjars");
    }
}