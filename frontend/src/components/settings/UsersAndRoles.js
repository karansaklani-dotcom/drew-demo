import React, { useState } from "react";
import { UserPlus, Shield, Users, UserCheck } from "lucide-react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "../ui/select";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "../ui/dialog";
import { useToast } from "../../hooks/use-toast";

const UsersAndRoles = () => {
    const { toast } = useToast();
    const [users, setUsers] = useState([
        {
            id: 1,
            name: "John Doe",
            email: "john@acmecorp.com",
            role: "Admin",
            status: "Active",
            joinedDate: "Jan 15, 2024",
        },
        {
            id: 2,
            name: "Sarah Smith",
            email: "sarah@acmecorp.com",
            role: "Manager",
            status: "Active",
            joinedDate: "Feb 20, 2024",
        },
        {
            id: 3,
            name: "Mike Johnson",
            email: "mike@acmecorp.com",
            role: "Member",
            status: "Active",
            joinedDate: "Mar 10, 2024",
        },
        {
            id: 4,
            name: "Emily Davis",
            email: "emily@acmecorp.com",
            role: "Member",
            status: "Invited",
            joinedDate: "Apr 5, 2024",
        },
    ]);

    const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
    const [newUser, setNewUser] = useState({
        name: "",
        email: "",
        role: "Member",
    });

    const handleAddUser = () => {
        const user = {
            id: users.length + 1,
            ...newUser,
            status: "Invited",
            joinedDate: new Date().toLocaleDateString("en-US", {
                month: "short",
                day: "numeric",
                year: "numeric",
            }),
        };
        setUsers([...users, user]);
        setNewUser({ name: "", email: "", role: "Member" });
        setIsAddDialogOpen(false);
        toast({
            title: "User invited",
            description: `Invitation sent to ${user.email}`,
        });
    };

    const handleDeleteUser = (userId) => {
        setUsers(users.filter((user) => user.id !== userId));
        toast({
            title: "User removed",
            description: "User has been removed from the organization.",
        });
    };

    const admins = users.filter((u) => u.role === "Admin");
    const managers = users.filter((u) => u.role === "Manager");
    const members = users.filter((u) => u.role === "Member");

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h2 className="text-2xl font-bold text-gray-900">
                        Users and Roles
                    </h2>
                    <p className="text-sm text-gray-600 mt-1">
                        Manage team members and their access levels
                    </p>
                </div>
                <Dialog
                    open={isAddDialogOpen}
                    onOpenChange={setIsAddDialogOpen}
                >
                    <DialogTrigger asChild>
                        <Button className="bg-black hover:bg-gray-800 text-white">
                            <UserPlus className="mr-2 h-4 w-4" />
                            Add User
                        </Button>
                    </DialogTrigger>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle>Invite New User</DialogTitle>
                            <DialogDescription>
                                Add a new team member to your organization
                            </DialogDescription>
                        </DialogHeader>
                        <div className="space-y-4 py-4">
                            <div className="space-y-2">
                                <Label htmlFor="userName">Name</Label>
                                <Input
                                    id="userName"
                                    value={newUser.name}
                                    onChange={(e) =>
                                        setNewUser({
                                            ...newUser,
                                            name: e.target.value,
                                        })
                                    }
                                    placeholder="John Doe"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="userEmail">Email</Label>
                                <Input
                                    id="userEmail"
                                    type="email"
                                    value={newUser.email}
                                    onChange={(e) =>
                                        setNewUser({
                                            ...newUser,
                                            email: e.target.value,
                                        })
                                    }
                                    placeholder="john@example.com"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="userRole">Role</Label>
                                <Select
                                    value={newUser.role}
                                    onValueChange={(value) =>
                                        setNewUser({ ...newUser, role: value })
                                    }
                                >
                                    <SelectTrigger>
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="Admin">
                                            Admin
                                        </SelectItem>
                                        <SelectItem value="Manager">
                                            Manager
                                        </SelectItem>
                                        <SelectItem value="Member">
                                            Member
                                        </SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>
                        <DialogFooter>
                            <Button
                                variant="outline"
                                onClick={() => setIsAddDialogOpen(false)}
                            >
                                Cancel
                            </Button>
                            <Button
                                onClick={handleAddUser}
                                className="bg-black hover:bg-gray-800 text-white"
                            >
                                Send Invitation
                            </Button>
                        </DialogFooter>
                    </DialogContent>
                </Dialog>
            </div>

            {/* Role Summary - Three Separate Rounded Sections */}
            <div className="grid grid-cols-3 gap-4">
                {/* Admins Section */}
                <div className="border border-gray-200 rounded-xl p-4 bg-gray-50 relative">
                    <div className="absolute top-4 right-4">
                        <Shield className="h-6 w-6 text-gray-700" />
                    </div>
                    <div>
                        <p className="text-sm font-medium text-gray-900 mb-2">
                            Admins
                        </p>
                        <p className="text-2xl font-bold text-gray-900 mb-1">
                            {admins.length}
                        </p>
                        <p className="text-xs text-gray-600">
                            Full access to all settings
                        </p>
                    </div>
                </div>

                {/* Managers Section */}
                <div className="border border-gray-200 rounded-xl p-4 bg-gray-50 relative">
                    <div className="absolute top-4 right-4">
                        <UserCheck className="h-6 w-6 text-gray-700" />
                    </div>
                    <div>
                        <p className="text-sm font-medium text-gray-900 mb-2">
                            Managers
                        </p>
                        <p className="text-2xl font-bold text-gray-900 mb-1">
                            {managers.length}
                        </p>
                        <p className="text-xs text-gray-600">
                            Can manage team and events
                        </p>
                    </div>
                </div>

                {/* Members Section */}
                <div className="border border-gray-200 rounded-xl p-4 bg-gray-50 relative">
                    <div className="absolute top-4 right-4">
                        <Users className="h-6 w-6 text-gray-700" />
                    </div>
                    <div>
                        <p className="text-sm font-medium text-gray-900 mb-2">
                            Members
                        </p>
                        <p className="text-2xl font-bold text-gray-900 mb-1">
                            {members.length}
                        </p>
                        <p className="text-xs text-gray-600">
                            Standard access level
                        </p>
                    </div>
                </div>
            </div>

            {/* Role Explanations */}
            <div className="border border-gray-200 rounded-lg p-6 bg-gray-50">
                <h3 className="text-sm font-semibold text-gray-900 mb-4">
                    Role Permissions
                </h3>
                <div className="space-y-4">
                    <div>
                        <div className="flex items-center gap-2 mb-1">
                            <Shield className="h-4 w-4 text-gray-700" />
                            <span className="text-sm font-medium text-gray-900">
                                Admin
                            </span>
                        </div>
                        <p className="text-xs text-gray-600 ml-6">
                            Full access to all organization settings, user
                            management, and can modify critical configurations.
                        </p>
                    </div>
                    <div>
                        <div className="flex items-center gap-2 mb-1">
                            <UserCheck className="h-4 w-4 text-gray-700" />
                            <span className="text-sm font-medium text-gray-900">
                                Manager
                            </span>
                        </div>
                        <p className="text-xs text-gray-600 ml-6">
                            Can manage team members, create and edit events, but
                            cannot modify organization settings.
                        </p>
                    </div>
                    <div>
                        <div className="flex items-center gap-2 mb-1">
                            <Users className="h-4 w-4 text-gray-700" />
                            <span className="text-sm font-medium text-gray-900">
                                Member
                            </span>
                        </div>
                        <p className="text-xs text-gray-600 ml-6">
                            Standard access to view and participate in events,
                            limited to personal profile management.
                        </p>
                    </div>
                </div>
            </div>

            {/* Users Table */}
            <div className="border border-gray-200 rounded-lg overflow-hidden">
                <table className="w-full">
                    <thead className="bg-gray-50 border-b border-gray-200">
                        <tr>
                            <th className="text-left py-3 px-4 text-xs font-medium text-gray-700">
                                User
                            </th>
                            <th className="text-left py-3 px-4 text-xs font-medium text-gray-700">
                                Role
                            </th>
                            <th className="text-left py-3 px-4 text-xs font-medium text-gray-700">
                                Status
                            </th>
                            <th className="text-left py-3 px-4 text-xs font-medium text-gray-700">
                                Joined
                            </th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                        {users.map((user) => (
                            <tr key={user.id} className="hover:bg-gray-50">
                                <td className="py-3 px-4">
                                    <div className="flex items-center gap-3">
                                        <div className="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-700 font-medium text-sm">
                                            {user.name
                                                .split(" ")
                                                .map((n) => n[0])
                                                .join("")}
                                        </div>
                                        <div>
                                            <p className="text-sm font-medium text-gray-900">
                                                {user.name}
                                            </p>
                                            <p className="text-xs text-gray-500">
                                                {user.email}
                                            </p>
                                        </div>
                                    </div>
                                </td>
                                <td className="py-3 px-4">
                                    <span className="text-sm text-gray-900">
                                        {user.role}
                                    </span>
                                </td>
                                <td className="py-3 px-4">
                                    <span
                                        className={`text-xs ${
                                            user.status === "Active"
                                                ? "text-gray-900 font-medium"
                                                : "text-gray-500"
                                        }`}
                                    >
                                        {user.status}
                                    </span>
                                </td>
                                <td className="py-3 px-4 text-xs text-gray-600">
                                    {user.joinedDate}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default UsersAndRoles;
