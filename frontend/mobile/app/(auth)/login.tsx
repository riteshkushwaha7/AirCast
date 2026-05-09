import { useState } from "react";
import { KeyboardAvoidingView, Platform, Text, View } from "react-native";
import { Link, router } from "expo-router";

import { AppTextInput, PrimaryButton, SectionContainer } from "../../components/ui";
import { ROUTES } from "../../constants/app";
import { signIn } from "../../services/auth";

export default function LoginScreen() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      await signIn(email, password);
      router.replace(ROUTES.home);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign in failed. Check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : undefined} className="flex-1 bg-surface px-5 pt-20">
      <SectionContainer>
        <Text className="text-xs uppercase tracking-wide text-ink-soft">Welcome back</Text>
        <Text className="mt-2 text-2xl font-semibold text-ink">Log in to My AirCast</Text>
        <Text className="mt-2 text-sm text-ink-soft">Check your air quality forecast in seconds.</Text>

        <View className="mt-5 gap-3">
          <AppTextInput value={email} onChangeText={setEmail} keyboardType="email-address" autoCapitalize="none" placeholder="Email" />
          <AppTextInput value={password} onChangeText={setPassword} secureTextEntry placeholder="Password" />
          <PrimaryButton label={loading ? "Signing in..." : "Continue"} onPress={onSubmit} disabled={loading} />
          {error ? <Text className="mt-2 text-sm text-red-500">{error}</Text> : null}
        </View>

        <Text className="mt-4 text-sm text-ink-soft">
          New here? <Link href={ROUTES.signup} style={{ color: "#1e252b" }}>Create account</Link>
        </Text>
      </SectionContainer>
    </KeyboardAvoidingView>
  );
}
