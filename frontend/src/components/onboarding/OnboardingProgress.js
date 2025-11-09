import React from "react";
import { Progress } from "../ui/progress";

export const OnboardingProgress = ({ step, totalSteps = 3 }) => {
    const getProgress = () => {
        if (totalSteps === 2) {
            // If only 2 steps (user has organization)
            if (step === 1) return 50;
            if (step === 2) return 100;
        } else {
            // If 3 steps (user doesn't have organization)
            if (step === 1) return 25;
            if (step === 2) return 60;
            if (step === 3) return 100;
        }
        return 0;
    };

    return (
        <div className="max-w-3xl mx-auto px-4 mt-4">
            <Progress value={getProgress()} className="h-2" />
        </div>
    );
};
