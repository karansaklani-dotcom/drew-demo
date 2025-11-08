import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Progress } from '../components/ui/progress';
import { RadioGroup, RadioGroupItem } from '../components/ui/radio-group';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { CheckCircle2 } from 'lucide-react';

const Onboarding = () => {
  const [step, setStep] = useState(1);
  const { completeOnboarding } = useAuth();
  const navigate = useNavigate();

  // Form state
  const [orgData, setOrgData] = useState({
    name: '',
    industry: '',
    companySize: '',
    website: ''
  });

  const [profileData, setProfileData] = useState({
    firstName: '',
    lastName: '',
    role: ''
  });

  const getProgress = () => {
    if (step === 1) return 25;
    if (step === 2) return 60;
    if (step === 3) return 100;
    return 0;
  };

  const handleStep1Continue = () => {
    if (!orgData.name || !orgData.industry || !orgData.companySize) {
      alert('Please fill in all required fields');
      return;
    }
    setStep(2);
  };

  const handleStep2Continue = () => {
    if (!profileData.firstName || !profileData.lastName || !profileData.role) {
      alert('Please fill in all required fields');
      return;
    }
    setStep(3);
  };

  const handleComplete = async () => {
    try {
      await completeOnboarding({
        ...profileData,
        organization: orgData
      });
      navigate('/');
    } catch (error) {
      alert('Failed to complete onboarding. Please try again.');
    }
  };

  const handleSkip = () => {
    setStep(2);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-white">
      {/* Header */}
      <div className="border-b bg-white/80 backdrop-blur-sm">
        <div className="max-w-3xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="bg-black text-white px-4 py-2 rounded-lg text-xl font-bold">
              Drew
            </div>
            <div className="text-sm text-gray-600">
              Step {step} of 3
            </div>
          </div>
        </div>
      </div>

      {/* Progress bar */}
      <div className="max-w-3xl mx-auto px-4 mt-4">
        <Progress value={getProgress()} className="h-2" />
      </div>

      {/* Content */}
      <div className="max-w-2xl mx-auto px-4 py-12">
        {step === 1 && (
          <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
            <h2 className="text-3xl font-bold mb-2">Set up your organization</h2>
            <p className="text-gray-600 mb-8">Tell us about your company</p>

            <div className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="orgName">
                  Organization name <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="orgName"
                  placeholder="Acme Inc."
                  value={orgData.name}
                  onChange={(e) => setOrgData({ ...orgData, name: e.target.value })}
                  className="h-12"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="industry">
                  Industry <span className="text-red-500">*</span>
                </Label>
                <Select
                  value={orgData.industry}
                  onValueChange={(value) => setOrgData({ ...orgData, industry: value })}
                >
                  <SelectTrigger className="h-12">
                    <SelectValue placeholder="Select industry" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="technology">Technology</SelectItem>
                    <SelectItem value="healthcare">Healthcare</SelectItem>
                    <SelectItem value="finance">Finance</SelectItem>
                    <SelectItem value="education">Education</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>
                  Company size <span className="text-red-500">*</span>
                </Label>
                <RadioGroup
                  value={orgData.companySize}
                  onValueChange={(value) => setOrgData({ ...orgData, companySize: value })}
                  className="space-y-3"
                >
                  <div className="flex items-center space-x-3 border rounded-lg p-4 hover:bg-gray-50 cursor-pointer">
                    <RadioGroupItem value="1-50" id="size1" />
                    <Label htmlFor="size1" className="flex-1 cursor-pointer">1-50 employees</Label>
                  </div>
                  <div className="flex items-center space-x-3 border rounded-lg p-4 hover:bg-gray-50 cursor-pointer">
                    <RadioGroupItem value="51-200" id="size2" />
                    <Label htmlFor="size2" className="flex-1 cursor-pointer">51-200 employees</Label>
                  </div>
                  <div className="flex items-center space-x-3 border rounded-lg p-4 hover:bg-gray-50 cursor-pointer">
                    <RadioGroupItem value="201-1000" id="size3" />
                    <Label htmlFor="size3" className="flex-1 cursor-pointer">201-1,000 employees</Label>
                  </div>
                  <div className="flex items-center space-x-3 border rounded-lg p-4 hover:bg-gray-50 cursor-pointer">
                    <RadioGroupItem value="1000+" id="size4" />
                    <Label htmlFor="size4" className="flex-1 cursor-pointer">1,000+ employees</Label>
                  </div>
                </RadioGroup>
              </div>

              <div className="space-y-2">
                <Label htmlFor="website">Website URL (optional)</Label>
                <Input
                  id="website"
                  type="url"
                  placeholder="https://example.com"
                  value={orgData.website}
                  onChange={(e) => setOrgData({ ...orgData, website: e.target.value })}
                  className="h-12"
                />
              </div>
            </div>

            <div className="flex gap-4 mt-8">
              <Button
                variant="outline"
                onClick={handleSkip}
                className="flex-1 h-12"
              >
                Skip
              </Button>
              <Button
                onClick={handleStep1Continue}
                className="flex-1 h-12 bg-black hover:bg-gray-800 text-white"
              >
                Continue
              </Button>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
            <h2 className="text-3xl font-bold mb-2">Complete your profile</h2>
            <p className="text-gray-600 mb-8">Help us personalize your experience</p>

            <div className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="firstName">
                  First name <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="firstName"
                  placeholder="John"
                  value={profileData.firstName}
                  onChange={(e) => setProfileData({ ...profileData, firstName: e.target.value })}
                  className="h-12"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="lastName">
                  Last name <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="lastName"
                  placeholder="Doe"
                  value={profileData.lastName}
                  onChange={(e) => setProfileData({ ...profileData, lastName: e.target.value })}
                  className="h-12"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="role">
                  Role/Department <span className="text-red-500">*</span>
                </Label>
                <Select
                  value={profileData.role}
                  onValueChange={(value) => setProfileData({ ...profileData, role: value })}
                >
                  <SelectTrigger className="h-12">
                    <SelectValue placeholder="Select your role" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="engineering">Engineering</SelectItem>
                    <SelectItem value="marketing">Marketing</SelectItem>
                    <SelectItem value="hr">HR</SelectItem>
                    <SelectItem value="operations">Operations</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="flex gap-4 mt-8">
              <Button
                variant="outline"
                onClick={() => setStep(1)}
                className="flex-1 h-12"
              >
                Back
              </Button>
              <Button
                onClick={handleStep2Continue}
                className="flex-1 h-12 bg-black hover:bg-gray-800 text-white"
              >
                Continue
              </Button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100 text-center">
            <div className="mb-6 flex justify-center">
              <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-full p-3">
                <CheckCircle2 className="h-12 w-12 text-white" />
              </div>
            </div>
            
            <h2 className="text-3xl font-bold mb-4">You're all set!</h2>
            <p className="text-gray-600 mb-8 text-lg">
              Welcome to Drew, {profileData.firstName}! Let's start discovering amazing events.
            </p>

            <Button
              onClick={handleComplete}
              className="h-12 px-8 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white text-lg"
            >
              Get Started
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Onboarding;
