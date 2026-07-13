"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { getCurrentUserApiV1AuthMeGet } from "@/client/sdk.gen";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAppConfig } from "@/context/AppConfigContext";
import { useAuth } from "@/lib/auth";
import { resolveBrowserBackendUrl } from "@/lib/apiClient";

export default function AccountSettingsPage() {
  const router = useRouter();
  const { provider, getAccessToken, redirectToLogin, loading: authLoading } = useAuth();
  const { config } = useAppConfig();

  const [email, setEmail] = useState("");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loadingProfile, setLoadingProfile] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (authLoading) {
      return;
    }

    if (provider === "stack") {
      router.replace("/handler/account-settings");
      return;
    }

    if (provider !== "local") {
      return;
    }

    const loadProfile = async () => {
      try {
        const token = await getAccessToken();
        const response = await getCurrentUserApiV1AuthMeGet({
          headers: { Authorization: `Bearer ${token}` },
        });

        if (response.error || !response.data?.email) {
          redirectToLogin();
          return;
        }

        setEmail(response.data.email);
      } catch {
        toast.error("Failed to load account details");
      } finally {
        setLoadingProfile(false);
      }
    };

    void loadProfile();
  }, [authLoading, getAccessToken, provider, redirectToLogin, router]);

  const handlePasswordChange = async (event: React.FormEvent) => {
    event.preventDefault();

    if (newPassword !== confirmPassword) {
      toast.error("New passwords do not match");
      return;
    }

    setSaving(true);

    try {
      const token = await getAccessToken();
      const baseUrl = resolveBrowserBackendUrl(config?.backendApiEndpoint);
      const response = await fetch(`${baseUrl}/api/v1/auth/change-password`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
        }),
      });

      if (!response.ok) {
        const body = (await response.json().catch(() => null)) as {
          detail?: string;
        } | null;
        toast.error(body?.detail || "Failed to update password");
        return;
      }

      toast.success("Password updated successfully");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch {
      toast.error("An error occurred. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  if (authLoading || loadingProfile || provider === "stack") {
    return null;
  }

  return (
    <div className="flex justify-center py-12 px-4">
      <div className="w-full max-w-2xl space-y-6">
        <div>
          <h1 className="text-2xl font-bold">Account settings</h1>
          <p className="text-muted-foreground">
            Manage your sign-in email and password.
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Email</CardTitle>
            <CardDescription>
              Your account email address used to sign in.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Input value={email} readOnly disabled />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Change password</CardTitle>
            <CardDescription>
              Update your password. Use at least 8 characters.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handlePasswordChange} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="current-password">Current password</Label>
                <Input
                  id="current-password"
                  type="password"
                  value={currentPassword}
                  onChange={(event) => setCurrentPassword(event.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="new-password">New password</Label>
                <Input
                  id="new-password"
                  type="password"
                  value={newPassword}
                  onChange={(event) => setNewPassword(event.target.value)}
                  minLength={8}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="confirm-password">Confirm new password</Label>
                <Input
                  id="confirm-password"
                  type="password"
                  value={confirmPassword}
                  onChange={(event) => setConfirmPassword(event.target.value)}
                  minLength={8}
                  required
                />
              </div>
              <Button type="submit" disabled={saving}>
                {saving ? "Saving..." : "Update password"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
