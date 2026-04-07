import { useState } from "react";
import { KeyboardAvoidingView, Platform, Text, View } from "react-native";
import { Link, router } from "expo-router";

import { AppTextInput, PrimaryButton, SectionContainer } from "../../components/ui";
import { ROUTES } from "../../constants/app";
import { signIn } from "../../services/auth";

export default function LoginScreen() {
  const [email, setEmail] = useState("aarav@myaircast.app");
  const [password, setPassword] = useState("password123");
  const [loading, setLoading] = useState(false);

  const onSubmit = async () => {
    setLoading(true);
    await signIn(email, password);
    setLoading(false);
    router.replace(ROUTES.home);
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
        </View>

        <Text className="mt-4 text-sm text-ink-soft">
          New here? <Link href={ROUTES.signup} style={{ color: "#1e252b" }}>Create account</Link>
        </Text>
      </SectionContainer>
    </KeyboardAvoidingView>
  );
}
