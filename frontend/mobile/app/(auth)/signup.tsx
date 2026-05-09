import { useState } from "react";
import { KeyboardAvoidingView, Platform, Text, View } from "react-native";
import { Link, router } from "expo-router";

import { AppTextInput, PrimaryButton, SectionContainer } from "../../components/ui";
import { ROUTES } from "../../constants/app";
import { signUp } from "../../services/auth";

export default function SignupScreen() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      await signUp(name, email, password);
      router.replace(ROUTES.onboarding);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign up failed. Try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : undefined} className="flex-1 bg-surface px-5 pt-20">
      <SectionContainer>
        <Text className="text-xs uppercase tracking-wide text-ink-soft">Get started</Text>
        <Text className="mt-2 text-2xl font-semibold text-ink">Create your My AirCast account</Text>
        <Text className="mt-2 text-sm text-ink-soft">Set your location and preferences for personalized guidance.</Text>

        <View className="mt-5 gap-3">
          <AppTextInput value={name} onChangeText={setName} placeholder="Full name" />
          <AppTextInput value={email} onChangeText={setEmail} keyboardType="email-address" autoCapitalize="none" placeholder="Email" />
          <AppTextInput value={password} onChangeText={setPassword} secureTextEntry placeholder="Password" />
          <PrimaryButton label={loading ? "Creating..." : "Create account"} onPress={onSubmit} disabled={loading} />
          {error ? <Text className="mt-2 text-sm text-red-500">{error}</Text> : null}
        </View>

        <Text className="mt-4 text-sm text-ink-soft">
          Already have an account? <Link href={ROUTES.login} style={{ color: "#1e252b" }}>Log in</Link>
        </Text>
      </SectionContainer>
    </KeyboardAvoidingView>
  );
}
