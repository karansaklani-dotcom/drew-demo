/**
 * Onboarding utility functions
 */

/**
 * Checks if the profile data is complete
 * @param {Object} profileData - The profile data object
 * @returns {boolean} - True if profile is complete (firstName, lastName, and role are filled)
 */
export function isProfileComplete(profileData) {
    if (!profileData) return false;

    return (
        profileData.firstName &&
        profileData.firstName.trim() !== "" &&
        profileData.lastName &&
        profileData.lastName.trim() !== "" &&
        profileData.role &&
        profileData.role.trim() !== ""
    );
}

/**
 * Checks if the organization data is complete
 * @param {Object} orgData - The organization data object
 * @returns {boolean} - True if organization is complete (name, industry, and companySize are filled)
 */
export function isOrganizationComplete(orgData) {
    if (!orgData) return false;

    return (
        orgData.name &&
        orgData.name.trim() !== "" &&
        orgData.industry &&
        orgData.industry.trim() !== "" &&
        orgData.companySize &&
        orgData.companySize.trim() !== ""
    );
}
