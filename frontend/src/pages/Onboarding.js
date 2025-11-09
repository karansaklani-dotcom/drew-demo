import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useOnboardingComplete } from "../hooks/use-onboarding";
import { useToast } from "../hooks/use-toast";
import { isProfileComplete } from "../utils/onboarding";
import { OnboardingHeader } from "../components/onboarding/OnboardingHeader";
import { OnboardingProgress } from "../components/onboarding/OnboardingProgress";
import { OrganizationSetupStep } from "../components/onboarding/OrganizationSetupStep";
import { ProfileSetupStep } from "../components/onboarding/ProfileSetupStep";
import { OnboardingCompleteStep } from "../components/onboarding/OnboardingCompleteStep";

const Onboarding = () => {
    const { user } = useAuth();
    const [step, setStep] = useState(1);
    const { mutate: completeOnboarding, isPending: isCompleting } =
        useOnboardingComplete();
    const navigate = useNavigate();
    const { toast } = useToast();

    // Check if user already has an organization
    const hasOrganization = user?.organizationId;

    // Form state
    const [orgData, setOrgData] = useState({
        name: "",
        industry: "",
        companySize: "",
        website: "",
    });

    const [profileData, setProfileData] = useState({
        firstName: "",
        lastName: "",
        role: "",
    });

    // Prefill profile data from user if available
    useEffect(() => {
        if (user) {
            setProfileData((prev) => ({
                firstName: prev.firstName || user.firstName || "",
                lastName: prev.lastName || user.lastName || "",
                role: prev.role || user.role || "",
            }));
        }
    }, [user]);

    // Skip organization step if user already has organization
    useEffect(() => {
        if (hasOrganization && step === 1) {
            setStep(2); // Skip to profile step
        }
    }, [hasOrganization, step]);

    const handleStep1Continue = () => {
        setStep(2);
    };

    const handleStep2Continue = () => {
        // Check if profile is complete before proceeding
        if (!isProfileComplete(profileData)) {
            toast({
                variant: "destructive",
                title: "Profile Incomplete",
                description:
                    "Please fill in all required fields (First name, Last name, and Role) before continuing.",
            });
            return;
        }
        setStep(3);
    };

    const handleComplete = async () => {
        // Check if profile is complete before submitting
        if (!isProfileComplete(profileData)) {
            toast({
                variant: "destructive",
                title: "Profile Incomplete",
                description:
                    "Please fill in all required fields (First name, Last name, and Role) before completing onboarding.",
            });
            return;
        }

        try {
            // Prepare payload based on whether user has organization
            const payload = {
                firstName: profileData.firstName,
                lastName: profileData.lastName,
                role: profileData.role,
            };

            // Only include organization if user doesn't have one
            if (!hasOrganization && orgData.name) {
                payload.organization = {
                    name: orgData.name,
                    industry: orgData.industry,
                    companySize: orgData.companySize,
                    websiteUrl: orgData.website || "",
                };
            }

            await completeOnboarding(payload);
            navigate("/");
        } catch (error) {
            toast({
                variant: "destructive",
                title: "Error",
                description:
                    error.message ||
                    "Failed to complete onboarding. Please try again.",
            });
        }
    };

    const handleSkip = () => {
        setStep(2);
    };

    // Calculate actual step for progress (skip step 1 if user has organization)
    const getActualStep = () => {
        if (hasOrganization) {
            // If user has organization, step 2 is actually step 1 (profile)
            // and step 3 is actually step 2 (complete)
            if (step === 2) return 1;
            if (step === 3) return 2;
            return step;
        }
        return step;
    };

    const getTotalSteps = () => {
        return hasOrganization ? 2 : 3;
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-white">
            <OnboardingHeader
                step={getActualStep()}
                totalSteps={getTotalSteps()}
            />
            <OnboardingProgress
                step={getActualStep()}
                totalSteps={getTotalSteps()}
            />

            <div className="max-w-2xl mx-auto px-4 py-12">
                {!hasOrganization && step === 1 && (
                    <OrganizationSetupStep
                        orgData={orgData}
                        setOrgData={setOrgData}
                        onContinue={handleStep1Continue}
                        onSkip={handleSkip}
                    />
                )}

                {step === 2 && (
                    <ProfileSetupStep
                        profileData={profileData}
                        setProfileData={setProfileData}
                        onContinue={handleStep2Continue}
                        onBack={hasOrganization ? undefined : () => setStep(1)}
                        showBack={!hasOrganization}
                    />
                )}

                {step === 3 && (
                    <OnboardingCompleteStep
                        firstName={profileData.firstName}
                        onComplete={handleComplete}
                        isCompleting={isCompleting}
                    />
                )}
            </div>
        </div>
    );
};

export default Onboarding;
