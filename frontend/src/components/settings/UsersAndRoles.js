import React, { useState } from "react";
import {
    UserPlus,
    Mail,
    Shield,
    MoreVertical,
    Trash2,
    Edit,
} from "lucide-react";
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
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "../ui/dropdown-menu";
import { Badge } from "../ui/badge";
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

    const getRoleBadgeColor = (role) => {
        switch (role) {
            case "Admin":
                return "bg-red-100 text-red-800";
            case "Manager":
                return "bg-blue-100 text-blue-800";
            case "Member":
                return "bg-green-100 text-green-800";
            default:
                return "bg-gray-100 text-gray-800";
        }
    };

    const getStatusBadgeColor = (status) => {
        switch (status) {
            case "Active":
                return "bg-green-100 text-green-800";
            case "Invited":
                return "bg-yellow-100 text-yellow-800";
            case "Inactive":
                return "bg-gray-100 text-gray-800";
            default:
                return "bg-gray-100 text-gray-800";
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-semibold text-gray-900">
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
                        <Button>
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
                                        <SelectItem value="Admin">Admin</SelectItem>
                                        <SelectItem value="Manager">
                                            Manager
                                        </SelectItem>
                                        <SelectItem value="Member">Member</SelectItem>
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
                            <Button onClick={handleAddUser}>Send Invitation</Button>
                        </DialogFooter>
                    </DialogContent>
                </Dialog>
            </div>

            <div className="grid grid-cols-3 gap-4">
                <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-lg p-4 border border-red-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-red-900">
                                Admins
                            </p>
                            <p className="text-2xl font-bold text-red-900 mt-1">
                                {users.filter((u) => u.role === "Admin").length}
                            </p>
                        </div>
                        <Shield className="h-8 w-8 text-red-600" />
                    </div>
                    <p className="text-xs text-red-700 mt-2">
                        Full access to all settings
                    </p>
                </div>
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-blue-900">
                                Managers
                            </p>
                            <p className="text-2xl font-bold text-blue-900 mt-1">
                                {users.filter((u) => u.role === "Manager").length}
                            </p>
                        </div>
                        <Shield className="h-8 w-8 text-blue-600" />
                    </div>
                    <p className="text-xs text-blue-700 mt-2">
                        Can manage team and events
                    </p>
                </div>
                <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 border border-green-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-green-900">
                                Members
                            </p>
                            <p className="text-2xl font-bold text-green-900 mt-1">
                                {users.filter((u) => u.role === "Member").length}
                            </p>
                        </div>
                        <Shield className="h-8 w-8 text-green-600" />
                    </div>
                    <p className="text-xs text-green-700 mt-2">
                        Standard access level
                    </p>
                </div>
            </div>

            <div className="border rounded-lg overflow-hidden">
                <table className="w-full">
                    <thead className="bg-gray-50 border-b">
                        <tr>
                            <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">
                                User
                            </th>
                            <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">
                                Role
                            </th>
                            <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">
                                Status
                            </th>
                            <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">
                                Joined
                            </th>
                            <th className="text-right py-3 px-4 text-sm font-medium text-gray-600">
                                Actions
                            </th>
                        </tr>
                    </thead>
                    <tbody className="divide-y">
                        {users.map((user) => (
                            <tr key={user.id} className="hover:bg-gray-50">
                                <td className="py-3 px-4">
                                    <div className="flex items-center gap-3">
                                        <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white font-medium">
                                            {user.name
                                                .split(" ")
                                                .map((n) => n[0])
                                                .join("")}
                                        </div>
                                        <div>
                                            <p className="text-sm font-medium text-gray-900">
                                                {user.name}
                                            </p>
                                            <p className="text-sm text-gray-500">
                                                {user.email}
                                            </p>
                                        </div>
                                    </div>
                                </td>
                                <td className="py-3 px-4">
                                    <Badge
                                        className={getRoleBadgeColor(user.role)}
                                    >
                                        {user.role}
                                    </Badge>
                                </td>
                                <td className="py-3 px-4">
                                    <Badge
                                        className={getStatusBadgeColor(
                                            user.status
                                        )}
                                    >
                                        {user.status}
                                    </Badge>
                                </td>
                                <td className="py-3 px-4 text-sm text-gray-600">
                                    {user.joinedDate}
                                </td>
                                <td className="py-3 px-4 text-right">
                                    <DropdownMenu>
                                        <DropdownMenuTrigger asChild>
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                className="h-8 w-8"
                                            >
                                                <MoreVertical className="h-4 w-4" />
                                            </Button>
                                        </DropdownMenuTrigger>
                                        <DropdownMenuContent align="end">
                                            <DropdownMenuItem>
                                                <Edit className="mr-2 h-4 w-4" />
                                                Edit Role
                                            </DropdownMenuItem>
                                            <DropdownMenuItem
                                                className="text-red-600"
                                                onClick={() =>
                                                    handleDeleteUser(user.id)
                                                }
                                            >
                                                <Trash2 className="mr-2 h-4 w-4" />
                                                Remove User
                                            </DropdownMenuItem>
                                        </DropdownMenuContent>
                                    </DropdownMenu>
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
