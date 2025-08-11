package com.banking.transfers.dto;

import java.util.Map;

/**
 * DTO pour les réponses de statistiques utilisateurs
 */
public class UserStatisticsResponse {

    private long totalUsers;
    private long activeUsers;
    private long inactiveUsers;
    private long lockedUsers;
    private Map<String, Long> usersByKycStatus;
    private Map<String, Long> usersByAmlStatus;
    private Map<String, Long> usersByRiskLevel;
    private Map<String, Long> usersByCountry;
    private Map<String, Long> usersByNationality;
    private long usersWithMfaEnabled;
    private long usersWithMfaDisabled;
    private Map<String, Long> usersByRegistrationMonth;

    // Constructeurs
    public UserStatisticsResponse() {}

    // Getters et Setters
    public long getTotalUsers() { return totalUsers; }
    public void setTotalUsers(long totalUsers) { this.totalUsers = totalUsers; }

    public long getActiveUsers() { return activeUsers; }
    public void setActiveUsers(long activeUsers) { this.activeUsers = activeUsers; }

    public long getInactiveUsers() { return inactiveUsers; }
    public void setInactiveUsers(long inactiveUsers) { this.inactiveUsers = inactiveUsers; }

    public long getLockedUsers() { return lockedUsers; }
    public void setLockedUsers(long lockedUsers) { this.lockedUsers = lockedUsers; }

    public Map<String, Long> getUsersByKycStatus() { return usersByKycStatus; }
    public void setUsersByKycStatus(Map<String, Long> usersByKycStatus) { this.usersByKycStatus = usersByKycStatus; }

    public Map<String, Long> getUsersByAmlStatus() { return usersByAmlStatus; }
    public void setUsersByAmlStatus(Map<String, Long> usersByAmlStatus) { this.usersByAmlStatus = usersByAmlStatus; }

    public Map<String, Long> getUsersByRiskLevel() { return usersByRiskLevel; }
    public void setUsersByRiskLevel(Map<String, Long> usersByRiskLevel) { this.usersByRiskLevel = usersByRiskLevel; }

    public Map<String, Long> getUsersByCountry() { return usersByCountry; }
    public void setUsersByCountry(Map<String, Long> usersByCountry) { this.usersByCountry = usersByCountry; }

    public Map<String, Long> getUsersByNationality() { return usersByNationality; }
    public void setUsersByNationality(Map<String, Long> usersByNationality) { this.usersByNationality = usersByNationality; }

    public long getUsersWithMfaEnabled() { return usersWithMfaEnabled; }
    public void setUsersWithMfaEnabled(long usersWithMfaEnabled) { this.usersWithMfaEnabled = usersWithMfaEnabled; }

    public long getUsersWithMfaDisabled() { return usersWithMfaDisabled; }
    public void setUsersWithMfaDisabled(long usersWithMfaDisabled) { this.usersWithMfaDisabled = usersWithMfaDisabled; }

    public Map<String, Long> getUsersByRegistrationMonth() { return usersByRegistrationMonth; }
    public void setUsersByRegistrationMonth(Map<String, Long> usersByRegistrationMonth) { this.usersByRegistrationMonth = usersByRegistrationMonth; }
}