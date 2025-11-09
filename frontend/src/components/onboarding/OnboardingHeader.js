import React from "react";

export const OnboardingHeader = ({ step, totalSteps = 3 }) => {
    return (
        <div className="border-b bg-white/80 backdrop-blur-sm">
            <div className="max-w-3xl mx-auto px-4 py-4">
                <div className="flex items-center justify-between">
                    <img
                        src="/assets/logo-small.png"
                        alt="Drew"
                        className="h-8"
                    />
                    <div className="text-sm text-gray-600">
                        Step {step} of {totalSteps}
                    </div>
                </div>
            </div>
        </div>
    );
};
