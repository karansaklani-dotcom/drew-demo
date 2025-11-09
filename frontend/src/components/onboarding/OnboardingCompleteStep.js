import React from "react";
import { Button } from "../ui/button";
import { CheckCircle2 } from "lucide-react";

export const OnboardingCompleteStep = ({
    firstName,
    onComplete,
    isCompleting,
}) => {
    return (
        <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 text-center">
            <div className="mb-6 flex justify-center">
                <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-full p-3">
                    <CheckCircle2 className="h-12 w-12 text-white" />
                </div>
            </div>

            <h2 className="text-3xl font-bold mb-4">You're all set!</h2>
            <p className="text-gray-600 mb-8 text-lg">
                Welcome to Drew, {firstName}! Let's start discovering amazing
                events.
            </p>

            <Button
                onClick={onComplete}
                disabled={isCompleting}
                className="h-12 px-8 bg-black hover:bg-gray-800 text-white text-lg disabled:opacity-50"
            >
                {isCompleting ? "Completing..." : "Get Started"}
            </Button>
        </div>
    );
};
